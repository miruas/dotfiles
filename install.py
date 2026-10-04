#!/usr/bin/env python3
"""Stage a pinned desktop bundle; apply only when explicitly requested."""
import argparse
import datetime
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
PINS = {
    'dms': ('https://github.com/AvengeMedia/DankMaterialShell.git', '2db7646fe3ab47fddfdb8723f2da07d61a0d47ac'),
    'plugin': ('https://github.com/sgtaziz/dms-wallpaperengine.git', 'e96718f5038f54546311a239ef0f6622f15c515a'),
}
def run(*args):
    subprocess.run(args, check=True)
def checkout(name, cache):
    url, revision = PINS[name]
    target = cache/name
    if not target.exists():
        run('git', 'clone', '--no-checkout', url, str(target))
    run('git', '-C', str(target), 'checkout', '--detach', revision)
    run('git', '-C', str(target), 'submodule', 'update', '--init', '--recursive')
    return target

def overlay(source, destination, home):
    for p in source.rglob('*'):
        if not p.is_file():
            continue
        dest = destination/p.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(p.read_text().replace('@HOME@', str(home)))
        shutil.copymode(p, dest)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=Path, default=Path('./staged-home'))
    parser.add_argument('--home', type=Path, default=Path.home(), help='Home path rendered into templates')
    parser.add_argument('--cache', type=Path, default=Path.home()/'.cache/dotfiles-sources')
    parser.add_argument('--apply', action='store_true', help='Copy staged files into home with backups; never restart the session')
    parser.add_argument('--profile-ui', action='store_true', help='Include the optional hardware bridge card')
    args = parser.parse_args()
    stage = args.stage.resolve()
    home = args.home.resolve()
    if stage == home or home in stage.parents:
        # A separate child stage is okay, but it must never be a managed config tree.
        if stage == home or any(x in stage.parts for x in ('.config', '.local')):
            parser.error('Use a separate staging directory')
    if stage.exists() and any(stage.iterdir()):
        parser.error('Staging directory must be empty')
    dms = checkout('dms', args.cache)
    plugin = checkout('plugin', args.cache)
    shell = stage/'.local/share/dms-custom-ui/1.6.2'
    shutil.copytree(dms/'quickshell', shell, symlinks=False)
    overlay(ROOT/'home', stage, home)
    demo = stage/'.local/share/dotfiles-demo/demo.py'
    demo.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'scripts/demo.py',demo)
    for p in (ROOT/'overlays/dms').rglob('*'):
        if not p.is_file():continue
        rel = p.relative_to(ROOT/'overlays/dms')
        if not args.profile_ui and str(rel).startswith('Modules/ControlCenter/'):
            continue
        dest = shell/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(p.read_text().replace('@HOME@', str(home)))
    dest = stage/'.config/DankMaterialShell/plugins/linuxWallpaperEngine'
    shutil.copytree(plugin, dest, ignore=shutil.ignore_patterns('.git','screenshot.png'))
    run('git', '-C', str(plugin), 'apply', '--check', str(ROOT/'patches/wallpaper-plugin.patch'))
    run('git', '-C', str(plugin), 'apply', str(ROOT/'patches/wallpaper-plugin.patch'))
    for rel in ['LinuxWallpaperEnginePlugin.qml', 'js/CommandBuilder.js']:
        target=dest/rel
        target.write_text((plugin/rel).read_text().replace('@HOME@', str(home)))
    run('git', '-C', str(plugin), 'restore', '.')
    print(f'Staged desktop bundle: {stage}')
    if not args.apply:
        print('Review staged files. Nothing was installed or restarted.')
        return
    backup = home/'.local/state/dotfiles/backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for p in stage.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(stage);target=home/rel
        if target.exists() or target.is_symlink():
            old=backup/rel;old.parent.mkdir(parents=True,exist_ok=True)
            if target.is_symlink():old.symlink_to(os.readlink(target));target.unlink()
            else:shutil.copy2(target,old)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,target)
    (home/'Pictures/Wallpapers').mkdir(parents=True,exist_ok=True)
    print(f'Installed files. Previous files are backed up in {backup}')
    print('Enable the documented user services, then log into Hyprland when ready.')

if __name__ == '__main__':main()
