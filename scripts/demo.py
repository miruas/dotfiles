#!/usr/bin/env python3
"""A 24-second desktop showcase. Recording is separate."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HOME=Path.home()
THEMES=HOME/'.config/theme-manager'
TIMELINE=[(0,'Demo workspace and terminal'),(1,'Animated theme gallery'),(2,'Purple theme'),(4,'Yellow theme'),(6,'Red theme'),(8,'Black/white theme'),(9,'Floating theme settings'),(11,'Cooling and performance card'),(14,'Wallpaper picker'),(16,'App launcher'),(18,'Return to the animated theme gallery'),(20,'Blue theme'),(22,'White/black theme'),(24,'Restore theme and workspace')]

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
    parser.add_argument('--dry-run',action='store_true',help='Print the timeline without changing the desktop')
    parser.add_argument('--countdown',type=int,default=5,help='Lead-in before the 24-second showcase')
    args=parser.parse_args()
    if args.dry_run:
        for at,label in TIMELINE:print(f'{at:02d}s  {label}')
        return
    for name in ['dms','hyprctl','alacritty']:
        if not shutil.which(name):parser.error(f'Missing command: {name}')
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
    allowed={'DotfilesDemo','local.dotfiles.ThemeManager'}
    # Match the existing pre-export installation as well, without embedding a user name.
    def owned(c):
        cls=c.get('class','')
        return c['address'] not in original_windows and c.get('workspace',{}).get('id')==demo_workspace and (cls in allowed or (cls.startswith('local.') and cls.endswith('.ThemeManager')))
    processes=[]
    def launch(*command):
        p=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        processes.append(p)
        return p
    def close_demo_windows():
        for c in clients():
            if owned(c):
                selector=json.dumps('address:'+c['address'])
                call('hyprctl','eval','hl.dispatch(hl.dsp.window.close({window = '+selector+'}))')
    def theme(name):
        reply=ipc('themeGallery','apply',name)
        if reply!='SUBMITTED':print(f'Skipped {name}: {reply}',file=sys.stderr)
    def panel():
        text='HYPRLAND + DANK\n\n12 color palettes / animated island\nStill + live wallpaper links\nAdaptive RAM + VRAM caching\nKeyboard-driven desktop\nOptional cooling + performance profiles\n\nSuper + Alt + T: Themes\nSuper + B: Control Center\nSuper + Shift + Space: Floating\n'
        launch('alacritty','--class','DotfilesDemo','--title','Desktop showcase','--config-file',str(HOME/'.config/hypr/terminal.toml'),'-e',sys.executable,'-c','import time;print('+repr(text)+');time.sleep(90)')
    actions={
        0:lambda:(workspace(demo_workspace),panel()),
        1:lambda:ipc('island','open','themes'),
        2:lambda:theme('purple'),
        4:lambda:theme('yellow'),
        6:lambda:theme('red'),
        8:lambda:theme('black-white'),
        9:lambda:(ipc('island','close'),launch(str(HOME/'.local/bin/theme-manager'),'--settings')),
        11:lambda:(close_demo_windows(),ipc('island','open','controlcenter')),
        14:lambda:ipc('island','open','wallpaper'),
        16:lambda:ipc('island','open','launcher'),
        18:lambda:ipc('island','open','themes'),
        20:lambda:theme('blue'),
        22:lambda:theme('white-black'),
    }
    print('Start your recorder now. Ctrl+C cancels and restores the desktop.')
    try:
        time.sleep(max(0,args.countdown))
        start=time.monotonic()
        for at,label in TIMELINE[:-1]:
            time.sleep(max(0,start+at-time.monotonic()))
            print(f'{at:02d}s  {label}',flush=True)
            try:actions[at]()
            except (RuntimeError,subprocess.TimeoutExpired,ImportError) as exc:print(str(exc),file=sys.stderr)
        time.sleep(max(0,start+24-time.monotonic()))
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
