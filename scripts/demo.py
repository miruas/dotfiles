#!/usr/bin/env python3
"""A fast 20-second showcase across workspaces 3 and 4."""
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
TIMELINE=[(0,'Workspace 3: normal terminal'),(.25,'Firefox website'),(.5,'Mission Center'),(2,'Rearrange applications'),(2.35,'Rotate split'),(2.7,'Float Mission Center'),(3.1,'Move and resize'),(3.5,'Return to tiling'),(3.9,'Fullscreen Firefox'),(4.3,'Return to tiling'),(4.7,'Workspace 4: unobstructed wallpaper showcase'),(5.2,'Purple live wallpaper'),(6.5,'Yellow live wallpaper'),(7.8,'Red live wallpaper'),(9.1,'Blue live wallpaper'),(10.4,'Live off: Black/white still wallpaper'),(11.9,'White/black still wallpaper'),(13.4,'Unobstructed still wallpaper'),(14.2,'Workspace 3: terminal colors and applications'),(15,'Cooling and performance card'),(16.2,'Theme and wallpaper settings'),(17.4,'Workspace 4: closing theme gallery'),(18,'Black/white still wallpaper'),(19.2,'Clean desktop closing shot'),(20,'Restore starting state')]


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
    parser.add_argument('--countdown',type=float,default=0,help='Optional lead-in; default starts immediately')
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
    demo_workspace=3
    wallpaper_workspace=4
    current_clients=clients()
    if any(c.get('class','').startswith('local.') and c.get('class','').endswith('.ThemeManager') for c in current_clients):
        parser.error('Close the existing theme settings window before the showcase')
    if any(c.get('workspace',{}).get('id')==4 for c in current_clients):
        parser.error('Workspace 4 must be empty for the unobstructed wallpaper showcase')
    original_windows={c['address'] for c in current_clients}
    settings_path=THEMES/'settings.json'
    original_settings=settings_path.read_text()
    settings=json.loads(original_settings)
    def live_active():
        try:return ipc('plugins','status','linuxWallpaperEngine')!='disabled' and ipc('linuxWallpaperEngine','status')=='on'
        except (RuntimeError,subprocess.TimeoutExpired):return False
    original_live=live_active()
    live_job=None
    def set_live(active):
        nonlocal live_job
        if live_job is not None:
            try:live_job.wait(timeout=3)
            except subprocess.TimeoutExpired:raise RuntimeError('Live wallpaper is still starting')
            live_job=None
        if live_active()!=active:
            call(str(HOME/'.local/bin/theme-manager'),'--toggle-live',timeout=20)
    def start_live():
        nonlocal live_job
        if not live_active():
            live_job=launch(str(HOME/'.local/bin/theme-manager'),'--toggle-live')
    def write_settings(text):
        temporary=settings_path.with_suffix('.demo.tmp')
        temporary.write_text(text)
        temporary.replace(settings_path)
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
        if c['address'] in original_windows or c.get('workspace',{}).get('id') not in [demo_workspace,wallpaper_workspace]:return False
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
        ipc('island','open','themes')
        deadline=time.monotonic()+1
        while time.monotonic()<deadline:
            try:reply=ipc('themeGallery','apply',name)
            except RuntimeError:time.sleep(.04);continue
            if reply=='SUBMITTED':return
            if reply!='BUSY':raise RuntimeError(reply)
            time.sleep(.04)
        raise RuntimeError('Theme application did not accept the next palette in time')
    def still_theme(name):
        set_live(False)
        theme(name)
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
        0:lambda:(workspace(3),start_live(),normal_terminal()),
        .25:lambda:app('browser','firefox','--new-window',args.url),
        .5:lambda:app('monitor','missioncenter','--app-id','io.missioncenter.MissionCenter.Demo'),
        2:lambda:manipulate('browser','hl.dispatch(hl.dsp.focus({window=w})); hl.dispatch(hl.dsp.window.move({window=w,direction="left"}))'),
        2.35:lambda:manipulate('browser','hl.dispatch(hl.dsp.focus({window=w})); hl.dispatch(hl.dsp.layout("togglesplit"))'),
        2.7:lambda:manipulate('monitor','hl.dispatch(hl.dsp.window.float({window=w,action="set"})); hl.dispatch(hl.dsp.window.resize({window=w,x=800,y=480})); hl.dispatch(hl.dsp.window.center({window=w})); hl.dispatch(hl.dsp.focus({window=w}))'),
        3.1:lambda:manipulate('monitor','hl.dispatch(hl.dsp.window.move({window=w,x=100,y=120})); hl.dispatch(hl.dsp.window.resize({window=w,x=960,y=560}))'),
        3.5:lambda:manipulate('monitor','hl.dispatch(hl.dsp.window.float({window=w,action="unset"}))'),
        3.9:lambda:manipulate('browser','hl.dispatch(hl.dsp.window.fullscreen({window=w,mode="fullscreen",action="set"}))'),
        4.3:lambda:manipulate('browser','hl.dispatch(hl.dsp.window.fullscreen({window=w,mode="fullscreen",action="unset"}))'),
        4.7:lambda:(workspace(4),set_live(True),ipc('island','open','themes')),
        5.2:lambda:theme('purple'),6.5:lambda:theme('yellow'),7.8:lambda:theme('red'),9.1:lambda:theme('blue'),
        10.4:lambda:still_theme('black-white'),
        11.9:lambda:theme('white-black'),
        13.4:lambda:ipc('island','close'),
        14.2:lambda:workspace(3),
        15:lambda:ipc('island','open','controlcenter'),
        16.2:lambda:(ipc('island','close'),launch(str(HOME/'.local/bin/theme-manager'),'--settings')),
        17.4:lambda:(close_demo_windows(settings_only=True),workspace(4),ipc('island','open','themes')),
        18:lambda:theme('black-white'),
        19.2:lambda:ipc('island','close'),
    }
    print('Showcase starts immediately. Ctrl+C cancels and restores the desktop.')
    try:
        settings['changeWallpaperWithTheme']=True
        write_settings(json.dumps(settings,indent=2)+'\n')
        time.sleep(max(0,args.countdown))
        start=time.monotonic()
        for at,label in TIMELINE[:-1]:
            time.sleep(max(0,start+at-time.monotonic()))
            print(f'{at:04.1f}s  {label}',flush=True)
            try:actions[at]()
            except (RuntimeError,subprocess.TimeoutExpired,ImportError) as exc:print(str(exc),file=sys.stderr)
        time.sleep(max(0,start+20-time.monotonic()))
    except KeyboardInterrupt:pass
    finally:
        try:ipc('island','close');close_demo_windows()
        except (RuntimeError,subprocess.TimeoutExpired):pass
        try:
            set_live(original_live)
            call(str(HOME/'.local/bin/theme-manager'),'--apply',original_theme,timeout=25)
        except (RuntimeError,subprocess.TimeoutExpired) as exc:print(f'Restore the original theme manually: {original_theme}. {exc}',file=sys.stderr)
        write_settings(original_settings)
        try:workspace(original_workspace)
        except (RuntimeError,subprocess.TimeoutExpired):pass
        print('Showcase finished. Stop the recorder; restoration may take a moment.')

if __name__=='__main__':main()
