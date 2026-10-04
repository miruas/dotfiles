#!/usr/bin/env python3
"""A 29-second desktop showcase with a normal terminal, Firefox and Mission Center."""
import argparse
import fcntl
import os
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HOME=Path.home()
THEMES=HOME/'.config/theme-manager'
TIMELINE=[(0,'Normal Super+T terminal'),(.8,'Firefox website window'),(1.6,'Mission Center'),(3,'Animated theme gallery'),(4,'Purple: shell and terminal'),(6,'Yellow: shell and terminal'),(8,'Red: shell and terminal'),(10,'Blue: shell and terminal'),(12,'Rearrange the application windows'),(13,'Rotate the split'),(14,'Float and center Mission Center'),(15,'Move and resize Mission Center'),(16,'Return Mission Center to tiling'),(17,'Fullscreen Firefox'),(18,'Restore the tiled layout'),(19,'Floating theme settings'),(21,'Cooling and performance card'),(24,'Wallpaper picker'),(26,'Return to the theme gallery'),(27,'Black/white closing palette'),(29,'Restore theme and workspace')]


def call(*args,timeout=3):
    result=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if result.returncode:raise RuntimeError((result.stderr or result.stdout).strip()[-300:])
    return result.stdout.strip()
def ipc(*args):return call('dms','ipc','call',*args)
def clients():return json.loads(call('hyprctl','clients','-j'))
def workspace(value):
    call('hyprctl','eval',f'hl.dispatch(hl.dsp.focus({{workspace = {int(value)}}}))')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default=os.environ.get('DOTFILES_DEMO_URL','https://example.org'),help='Website opened in a new Firefox window')
    parser.add_argument('--dry-run',action='store_true',help='Print the timeline without changing the desktop')
    parser.add_argument('--countdown',type=int,default=5,help='Lead-in before the 29-second showcase')
    args=parser.parse_args()
    if args.dry_run:
        for at,label in TIMELINE:print(f'{at:04.1f}s  {label}')
        return
    for name in ['dms','hyprctl','alacritty','firefox','missioncenter']:
        if not shutil.which(name):parser.error(f'Missing command: {name}')
    if not args.url.startswith(('https://','http://')):parser.error('Use an HTTP or HTTPS website URL')
    lock_path=Path(os.environ.get('XDG_RUNTIME_DIR',str(HOME/'.cache')))/'dotfiles-demo.lock'
    lock_path.parent.mkdir(parents=True,exist_ok=True)
    lock_file=lock_path.open('w')
    try:fcntl.flock(lock_file,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:parser.error('A showcase is already running')
    original_theme=(THEMES/'selected').read_text().strip()
    available={p['id'] for p in json.loads((THEMES/'presets.json').read_text())}
    if original_theme not in available:parser.error('Cannot restore the current theme')
    original_workspace=json.loads(call('hyprctl','activeworkspace','-j'))['id']
    occupied={w['id'] for w in json.loads(call('hyprctl','workspaces','-j'))}
    demo_workspace=next(w for w in range(91,100) if w not in occupied)
    current_clients=clients()
    if any(c.get('class','').startswith('local.') and c.get('class','').endswith('.ThemeManager') for c in current_clients):
        parser.error('Close the existing theme settings window before the showcase')
    original_windows={c['address'] for c in current_clients}
    role_addresses={}
    def role_for(c):
        cls=c.get('class','').lower()
        if cls in ['alacritty','org.alacritty.alacritty']:return 'terminal'
        if 'firefox' in cls:return 'browser'
        if cls in ['missioncenter','io.missioncenter.missioncenter.demo']:return 'monitor'
        if cls.startswith('local.') and cls.endswith('.thememanager'):return 'settings'
        return None
    # Match the existing pre-export installation as well, without embedding a user name.
    def owned(c):
        cls=c.get('class','')
        if c['address'] in original_windows or c.get('workspace',{}).get('id')!=demo_workspace:return False
        role=role_for(c)
        if role and role not in role_addresses:role_addresses[role]=c['address']
        return role is not None and role_addresses.get(role)==c['address']
    processes=[]
    def launch(*command):
        p=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        processes.append(p)
        return p
    def close_demo_windows(settings_only=False):
        for c in clients():
            if owned(c) and (not settings_only or role_for(c)=='settings'):
                selector=json.dumps('address:'+c['address'])
                call('hyprctl','eval','hl.dispatch(hl.dsp.window.close({window = '+selector+'}))')
    def theme(name):
        reply=ipc('themeGallery','apply',name)
        if reply!='SUBMITTED':print(f'Skipped {name}: {reply}',file=sys.stderr)
    def app(role,*command):
        launch(*command)
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            for c in clients():
                if c['address'] in original_windows or role_for(c)!=role:continue
                role_addresses[role]=c['address']
                if c.get('workspace',{}).get('id')!=demo_workspace:
                    selector=json.dumps('address:'+c['address'])
                    call('hyprctl','eval','local w=hl.get_window('+selector+'); if w then hl.dispatch(hl.dsp.window.move({window=w,workspace='+str(demo_workspace)+'})) end')
                workspace(demo_workspace)
                return
            time.sleep(.05)
        raise RuntimeError(f'Demo {role} did not open in time')
    def normal_terminal():
        app('terminal',str(HOME/'.config/hypr/launch-app.sh'),'alacritty','--config-file',str(HOME/'.config/hypr/terminal.toml'))
    def manipulate(role,body):
        windows=[c for c in clients() if owned(c) and role_for(c)==role]
        if not windows:raise RuntimeError(f'Demo {role} window is not ready')
        selector=json.dumps('address:'+windows[0]['address'])
        code='local w = hl.get_window('+selector+'); if w then '+body+' end'
        call('hyprctl','eval',code)
    actions={
        0:lambda:(workspace(demo_workspace),normal_terminal()),
        .8:lambda:app('browser','firefox','--new-window',args.url),
        1.6:lambda:app('monitor','missioncenter','--app-id','io.missioncenter.MissionCenter.Demo'),
        3:lambda:ipc('island','open','themes'),
        4:lambda:theme('purple'),6:lambda:theme('yellow'),8:lambda:theme('red'),10:lambda:theme('blue'),
        12:lambda:(ipc('island','close'),manipulate('browser','hl.dispatch(hl.dsp.focus({window=w})); hl.dispatch(hl.dsp.window.move({window=w,direction="left"}))')),
        13:lambda:manipulate('browser','hl.dispatch(hl.dsp.focus({window=w})); hl.dispatch(hl.dsp.layout("togglesplit"))'),
        14:lambda:manipulate('monitor','hl.dispatch(hl.dsp.window.float({window=w,action="set"})); hl.dispatch(hl.dsp.window.resize({window=w,x=800,y=480})); hl.dispatch(hl.dsp.window.center({window=w})); hl.dispatch(hl.dsp.focus({window=w}))'),
        15:lambda:manipulate('monitor','hl.dispatch(hl.dsp.window.move({window=w,x=100,y=120})); hl.dispatch(hl.dsp.window.resize({window=w,x=960,y=560}))'),
        16:lambda:manipulate('monitor','hl.dispatch(hl.dsp.window.float({window=w,action="unset"}))'),
        17:lambda:manipulate('browser','hl.dispatch(hl.dsp.window.fullscreen({window=w,mode="fullscreen",action="set"}))'),
        18:lambda:manipulate('browser','hl.dispatch(hl.dsp.window.fullscreen({window=w,mode="fullscreen",action="unset"}))'),
        19:lambda:launch(str(HOME/'.local/bin/theme-manager'),'--settings'),
        21:lambda:(close_demo_windows(settings_only=True),ipc('island','open','controlcenter')),
        24:lambda:ipc('island','open','wallpaper'),
        26:lambda:ipc('island','open','themes'),
        27:lambda:theme('black-white'),
    }
    print('Start your recorder now. Ctrl+C cancels and restores the desktop.')
    try:
        time.sleep(max(0,args.countdown))
        start=time.monotonic()
        for at,label in TIMELINE[:-1]:
            time.sleep(max(0,start+at-time.monotonic()))
            print(f'{at:04.1f}s  {label}',flush=True)
            try:actions[at]()
            except (RuntimeError,subprocess.TimeoutExpired,ImportError) as exc:print(str(exc),file=sys.stderr)
        time.sleep(max(0,start+29-time.monotonic()))
    except KeyboardInterrupt:pass
    finally:
        try:ipc('island','close');close_demo_windows()
        except (RuntimeError,subprocess.TimeoutExpired):pass
        try:call(str(HOME/'.local/bin/theme-manager'),'--apply',original_theme,timeout=25)
        except (RuntimeError,subprocess.TimeoutExpired) as exc:print(f'Restore the original theme manually: {original_theme}. {exc}',file=sys.stderr)
        try:workspace(original_workspace)
        except (RuntimeError,subprocess.TimeoutExpired):pass
        print('Showcase finished. Stop the recorder; restoration may take a moment.')

if __name__=='__main__':main()
