#!/usr/bin/python
"""Local, fixed-operation bridge for DMS, LACT and CoolerControl."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import socketserver
import struct
import subprocess
import threading
import time
import tomllib
import urllib.request
import uuid
import yaml

CONFIG = Path('/etc/dank-profile-manager')
DATA = Path('/var/lib/dank-profile-manager')
SOCKET = '/run/dank-profile-manager/control.sock'
LOW_PROFILE = 'Dank Low Performance'
LOCK = threading.RLock()
OPTIONS = json.loads((CONFIG/'hardware.json').read_text())
if not OPTIONS.get('board_uid') or OPTIONS['board_uid'].startswith('REPLACE'):
    raise RuntimeError('Configure hardware.json before starting the hardware bridge')

def run(*args):
    result = subprocess.run(args, text=True, capture_output=True, timeout=25)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or 'Command failed').strip()[-600:])
    return result.stdout.strip()

def atomic(path, value, mode=0o600):
    path = Path(path)
    tmp = path.with_name(path.name + '.new')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(fd, 'w') as f:
        f.write(value)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, mode)
    os.replace(tmp, path)

def read(path, fallback=None):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return fallback

def policies():
    return sorted(Path('/sys/devices/system/cpu/cpufreq').glob('policy*'))

def hwmon(name):
    return next((p for p in Path('/sys/class/hwmon').glob('hwmon*') if read(p/'name') == name), None)

def initialize():
    CONFIG.mkdir(mode=0o700, exist_ok=True)
    DATA.mkdir(mode=0o700, exist_ok=True)
    if (CONFIG/'baseline.json').exists():
        return
    backup = DATA/'original'
    backup.mkdir(mode=0o700, exist_ok=True)
    for source in ['/etc/lact/config.yaml', '/etc/coolercontrol/config.toml', '/etc/coolercontrol/modes.json', '/etc/coolercontrol/.tokens']:
        p = Path(source)
        if p.exists():
            atomic(backup/(p.parent.name+'-'+p.name), p.read_text())
    lact = yaml.safe_load(Path('/etc/lact/config.yaml').read_text())
    profile = lact.get('current_profile')
    assert profile and profile in lact['profiles'], 'An active LACT overclock profile is required'
    active = lact['profiles'][profile]['gpus']
    gpu = next(k for k in active if k.startswith('10DE:'))
    low = {'fan_control_enabled': False, 'power_mizer_mode': 'Adaptive', 'power_cap': OPTIONS['low_gpu_watts'],
           'min_core_clock': OPTIONS['low_gpu_min_mhz'], 'max_core_clock': OPTIONS['low_gpu_max_mhz'],
           'mem_clock_offsets': {0: 0}}
    lact['profiles'][LOW_PROFILE] = {'gpus': {gpu: low}}
    atomic('/etc/lact/config.yaml', yaml.safe_dump(lact, sort_keys=False), 0o644)
    baseline = {'uid': OPTIONS['uid'], 'gid': OPTIONS['gid'], 'gpu': gpu, 'lact_max_profile': profile,
                'cpu': {p.name:{n:read(p/n) for n in ['scaling_min_freq','scaling_max_freq','scaling_governor','energy_performance_preference']} for p in policies()},
                'boost': read('/sys/devices/system/cpu/cpufreq/boost'),
                'power_profile': run('/usr/bin/powerprofilesctl', 'get')}
    token = 'cc_'+uuid.uuid4().hex
    tokens_path = Path('/etc/coolercontrol/.tokens')
    tokens = json.loads(tokens_path.read_text()) if tokens_path.exists() else []
    tokens.append({'id':str(uuid.uuid4()), 'label':'Dank Profile Manager (local bridge)',
                   'hash':'', 'digest':hashlib.sha256(token.encode()).hexdigest(),
                   'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'expires_at':None, 'last_used':None, 'write_access':True})
    atomic(tokens_path, json.dumps(tokens))
    atomic(CONFIG/'coolercontrol.token', token)
    atomic(CONFIG/'baseline.json', json.dumps(baseline, indent=2))
    atomic(DATA/'state.json', json.dumps({'performance':'max'}))

def cooler(path, method='GET'):
    token = (CONFIG/'coolercontrol.token').read_text().strip()
    request = urllib.request.Request('http://127.0.0.1:11987'+path,
        data=b'{}' if method == 'POST' else None,
        headers={'Authorization':'Bearer '+token, 'Content-Type':'application/json'}, method=method)
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read()
        return json.loads(body) if body else None

def fan_modes():
    data = json.loads(Path('/etc/coolercontrol/modes.json').read_text())
    lookup = {name:key for key,name in OPTIONS['fan_modes'].items()}
    return data, {lookup[m['name']]:m['uid'] for m in data['modes'] if m['name'] in lookup}

def set_fan(value):
    if value not in ['silent','turbo','bios']:
        raise ValueError('Unknown fan mode')
    data, modes = fan_modes()
    selected = next(m for m in data['modes'] if m['uid'] == modes[value])
    expected_board = OPTIONS['board_uid']
    if set(selected['all_device_settings']) != {expected_board} or set(selected['all_device_settings'][expected_board]) != {OPTIONS['fan_channel']}:
        raise RuntimeError('This cooling mode contains channels beyond CPU_OPT; no changes applied')
    cooler('/modes-active/'+modes[value], 'POST')
    # The mode must remain confined to the radiator channel.
    active = cooler('/modes-active')
    if active.get('current_mode_uid') != modes[value]:
        # Field names differ between releases; persisted state is also authoritative.
        data, _ = fan_modes()
        if data.get('current_active_mode') != modes[value]:
            raise RuntimeError('CoolerControl did not activate the requested mode')

def apply_cpu(value, baseline):
    low = value == 'low'
    boost = Path('/sys/devices/system/cpu/cpufreq/boost')
    # PPD cannot enable per-policy boost while the global boost gate is disabled.
    if not low and boost.exists():
        boost.write_text(baseline['boost'] or '1')
        for p in policies():
            (p/'scaling_max_freq').write_text(baseline['cpu'][p.name]['scaling_max_freq'])
    run('/usr/bin/powerprofilesctl', 'set', 'power-saver' if low else 'performance')
    if boost.exists():
        boost.write_text('0' if low else baseline['boost'] or '1')
    for p in policies():
        original = baseline['cpu'][p.name]
        # Restore the floor before writing a reduced ceiling.
        (p/'scaling_min_freq').write_text(original['scaling_min_freq'])
        (p/'scaling_max_freq').write_text(str(OPTIONS['low_cpu_khz']) if low else original['scaling_max_freq'])
        (p/'scaling_governor').write_text('powersave' if low else original['scaling_governor'])
        epp = p/'energy_performance_preference'
        if epp.exists():
            epp.write_text('power' if low else original['energy_performance_preference'])

def set_performance(value, persist=True):
    if value not in ['low','max']:
        raise ValueError('Unknown performance mode')
    baseline = json.loads((CONFIG/'baseline.json').read_text())
    previous = json.loads((DATA/'state.json').read_text()).get('performance','max')
    target = LOW_PROFILE if value == 'low' else baseline['lact_max_profile']
    try:
        run('/usr/bin/lact','cli','profile','set',target)
        apply_cpu(value, baseline)
        if run('/usr/bin/lact','cli','profile','get') != target:
            raise RuntimeError('LACT profile verification failed')
        ceiling = int(read(policies()[0]/'scaling_max_freq'))
        if value == 'low' and ceiling > OPTIONS['low_cpu_khz']:
            raise RuntimeError('CPU frequency ceiling verification failed')
        if persist:
            atomic(DATA/'state.json',json.dumps({'performance':value}))
    except Exception:
        run('/usr/bin/lact','cli','profile','set',LOW_PROFILE if previous == 'low' else baseline['lact_max_profile'])
        apply_cpu(previous, baseline)
        raise

def snapshot():
    baseline = json.loads((CONFIG/'baseline.json').read_text())
    data, modes = fan_modes()
    fan = next((k for k,v in modes.items() if v == data.get('current_active_mode')), 'custom')
    if fan == 'custom':
        cfg=tomllib.loads(Path('/etc/coolercontrol/config.toml').read_text())
        assigned=cfg.get('device-settings',{}).get(OPTIONS['board_uid'],{}).get(OPTIONS['fan_channel'],{}).get('profile_uid')
        profile=next((p for p in cfg['profiles'] if p['uid']==assigned),{})
        fan={name:key for key,name in OPTIONS['fan_modes'].items()}.get(profile.get('name'),'custom')
    lact_profile = run('/usr/bin/lact','cli','profile','get')
    p = policies()[0]
    max_freq = int(read(p/'scaling_max_freq','0'))
    ppd = run('/usr/bin/powerprofilesctl','get')
    performance = 'low' if lact_profile == LOW_PROFILE and max_freq <= OPTIONS['low_cpu_khz'] and ppd == 'power-saver' else 'max' if lact_profile == baseline['lact_max_profile'] and max_freq > OPTIONS['low_cpu_khz'] and ppd == 'performance' else 'custom'
    cpu_hw = hwmon(OPTIONS['cpu_hwmon'])
    fan_hw = hwmon(OPTIONS['fan_hwmon'])
    gpu = run('/usr/bin/nvidia-smi','--query-gpu=temperature.gpu,clocks.gr,clocks.mem,power.limit,power.draw,utilization.gpu','--format=csv,noheader,nounits').split(', ')
    def numeric(v):
        try: return float(v)
        except (TypeError,ValueError): return None
    cpu_power = None
    for d in Path('/sys/class/powercap').glob('intel-rapl:*'):
        if read(d/'name') == 'package-0':
            a=read(d/'energy_uj')
            t=time.monotonic()
            time.sleep(.05)
            b=read(d/'energy_uj')
            if a and b and int(b)>=int(a): cpu_power=round((int(b)-int(a))/(time.monotonic()-t)/1e6,1)
            break
    return {'ok':True,'fan':fan,'performance':performance,'lact_profile':lact_profile,
            'cpu_temp':round(int(read(cpu_hw/'temp1_input','0'))/1000,1) if cpu_hw else None,
            'cpu_clock':round(int(read(p/'scaling_cur_freq','0'))/1e6,2),
            'cpu_limit':round(max_freq/1e6,2),'cpu_power':cpu_power,
            'gpu_temp':numeric(gpu[0]),'gpu_clock':numeric(gpu[1]),'gpu_memory':numeric(gpu[2]),
            'gpu_power_limit':numeric(gpu[3]),'gpu_power':numeric(gpu[4]),'gpu_load':numeric(gpu[5]),
            'fan_rpm':int(read(fan_hw/(OPTIONS['fan_channel']+'_input'),'0')) if fan_hw else None,
            'pump_rpm':int(read(fan_hw/(OPTIONS['pump_channel']+'_input'),'0')) if fan_hw else None}

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(40)
        _, uid, _ = struct.unpack('3i', self.request.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        if uid not in [0,OPTIONS['uid']]: return
        try:
            request=json.loads(self.rfile.readline(2048))
            with LOCK:
                if request.get('op') == 'fan': set_fan(request.get('value'))
                elif request.get('op') == 'performance': set_performance(request.get('value'))
                elif request.get('op') != 'status': raise ValueError('Unknown operation')
                result=snapshot()
        except Exception as exc:
            result={'ok':False,'error':str(exc)[-600:]}
            print(json.dumps(result),flush=True)
        self.wfile.write((json.dumps(result)+'\n').encode())

if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['--initialize']:
        initialize()
    else:
        Path(SOCKET).parent.mkdir(exist_ok=True)
        Path(SOCKET).unlink(missing_ok=True)
        server=socketserver.ThreadingUnixStreamServer(SOCKET,Handler)
        server.daemon_threads=True
        os.chown(SOCKET,0,OPTIONS['gid'])
        os.chmod(SOCKET,0o660)
        # Restore the selected limits after reboot without touching fan/pump control.
        state=json.loads((DATA/'state.json').read_text())
        set_performance(state.get('performance','max'),persist=False)
        print('Dank Profile Manager ready',flush=True)
        server.serve_forever()
