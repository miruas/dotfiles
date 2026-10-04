#!/usr/bin/env python3
"""A 28-second desktop showcase with live terminal colors and window choreography."""
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
TIMELINE=[(0,'First themed terminal'),(.7,'Second tiled terminal'),(1.4,'Third tiled terminal'),(2,'Animated theme gallery'),(3,'Purple: shell and all terminals'),(5,'Yellow: shell and all terminals'),(7,'Red: shell and all terminals'),(9,'Blue: shell and all terminals'),(11,'Rearrange the tiled windows'),(12,'Rotate the split'),(13,'Float and center the third terminal'),(14,'Move and resize the floating terminal'),(15,'Return the terminal to tiling'),(16,'Fullscreen the first terminal'),(17,'Restore the tiled layout'),(18,'Floating theme settings'),(20,'Cooling and performance card'),(23,'Wallpaper picker'),(25,'Return to the theme gallery'),(26,'Black/white closing palette'),(28,'Restore theme and workspace')]


def call(*args,timeout=3):
    result=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if result.returncode:raise RuntimeError((result.stderr or result.stdout).strip()[-300:])
    return result.stdout.strip()
def ipc(*args):return call('dms','ipc','call',*args)
def clients():return json.loads(call('hyprctl','clients','-j'))
def workspace(value):
    call('hyprctl','eval',f'hl.dispatch(hl.dsp.focus({{workspace = {int(value)}}}))')
def terminal_panel(kind):
    blocks={
        'overview':('HYPRLAND + DANK',['Animated island','12 coordinated palettes','Still + live wallpapers','Adaptive RAM / VRAM cache','Cooling + performance card']),
        'workflow':('KEYBOARD WORKFLOW',['Super + T        Terminal','Super + Alt + T  Themes','Super + B        Control Center','Super + W        Live wallpapers','Super + arrows   Focus','Shift + arrows   Arrange']),
        'palette':('LIVE COLOR SYNC',['One palette, one desktop.','','Shell / window borders','Terminal background / text','ANSI palette / selection','','No terminal restart needed.']),
    }
    title,lines=blocks[kind]
    print('\033[2J\033[H\n\033[1;36m  '+title+'\033[0m\n  '+('─'*32)+'\n')
    for line in lines:print('  '+line)
    print('\n  '+''.join('\033['+str(c)+'m● ● \033[0m ' for c in range(31,37)),flush=True)
    time.sleep(90)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--terminal-panel',choices=['overview','workflow','palette'],help=argparse.SUPPRESS)
    parser.add_argument('--dry-run',action='store_true',help='Print the timeline without changing the desktop')
    parser.add_argument('--countdown',type=int,default=5,help='Lead-in before the 28-second showcase')
    args=parser.parse_args()
    if args.terminal_panel:
        terminal_panel(args.terminal_panel)
        return
    if args.dry_run:
        for at,label in TIMELINE:print(f'{at:04.1f}s  {label}')
        return
    for name in ['dms','hyprctl','alacritty']:
        if not shutil.which(name):parser.error(f'Missing command: {name}')
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
    def close_demo_windows(settings_only=False):
        for c in clients():
            if owned(c) and (not settings_only or c.get("class")!="DotfilesDemo"):
                selector=json.dumps('address:'+c['address'])
                call('hyprctl','eval','hl.dispatch(hl.dsp.window.close({window = '+selector+'}))')
    def theme(name):
        reply=ipc('themeGallery','apply',name)
        if reply!='SUBMITTED':print(f'Skipped {name}: {reply}',file=sys.stderr)
    def panel(kind):
        launch('alacritty','--class','DotfilesDemo','--title','Dank / '+kind.title(),
               '--config-file',str(HOME/'.config/hypr/terminal.toml'),
               '-o','general.live_config_reload=true','-e',sys.executable,str(Path(__file__).resolve()),'--terminal-panel',kind)
    def manipulate(index,body):
        windows=[c for c in clients() if owned(c) and c.get('class')=='DotfilesDemo']
        windows.sort(key=lambda c:c.get('pid',0))
        if index>=len(windows):raise RuntimeError('Demo terminal is not ready')
        selector=json.dumps('address:'+windows[index]['address'])
        code='local w = hl.get_window('+selector+'); if w then '+body+' end'
        call('hyprctl','eval',code)
    actions={
        0:lambda:(workspace(demo_workspace),panel('overview')),
        .7:lambda:panel('workflow'),
        1.4:lambda:panel('palette'),
        2:lambda:ipc('island','open','themes'),
        3:lambda:theme('purple'),5:lambda:theme('yellow'),7:lambda:theme('red'),9:lambda:theme('blue'),
        11:lambda:(ipc('island','close'),manipulate(1,'hl.dispatch(hl.dsp.focus({window=w})); hl.dispatch(hl.dsp.window.move({window=w,direction="left"}))')),
        12:lambda:manipulate(1,'hl.dispatch(hl.dsp.focus({window=w})); hl.dispatch(hl.dsp.layout("togglesplit"))'),
        13:lambda:manipulate(2,'hl.dispatch(hl.dsp.window.float({window=w,action="set"})); hl.dispatch(hl.dsp.window.resize({window=w,x=800,y=480})); hl.dispatch(hl.dsp.window.center({window=w})); hl.dispatch(hl.dsp.focus({window=w}))'),
        14:lambda:manipulate(2,'hl.dispatch(hl.dsp.window.move({window=w,x=100,y=120})); hl.dispatch(hl.dsp.window.resize({window=w,x=960,y=560}))'),
        15:lambda:manipulate(2,'hl.dispatch(hl.dsp.window.float({window=w,action="unset"}))'),
        16:lambda:manipulate(0,'hl.dispatch(hl.dsp.window.fullscreen({window=w,mode="fullscreen",action="set"}))'),
        17:lambda:manipulate(0,'hl.dispatch(hl.dsp.window.fullscreen({window=w,mode="fullscreen",action="unset"}))'),
        18:lambda:launch(str(HOME/'.local/bin/theme-manager'),'--settings'),
        20:lambda:(close_demo_windows(settings_only=True),ipc('island','open','controlcenter')),
        23:lambda:ipc('island','open','wallpaper'),
        25:lambda:ipc('island','open','themes'),
        26:lambda:theme('black-white'),
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
        time.sleep(max(0,start+28-time.monotonic()))
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
