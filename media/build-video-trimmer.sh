#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
build_root=${XDG_CACHE_HOME:-$HOME/.cache}/dotfiles-build/video-trimmer
prefix=$HOME/.local/opt/video-trimmer-selected
[ ! -e "$build_root" ] || { echo 'Build directory already exists; inspect it before rebuilding.' >&2; exit 1; }
git clone https://gitlab.gnome.org/YaLTeR/video-trimmer.git "$build_root"
git -C "$build_root" checkout --detach 1c75471cc01ac3b58f2995814870ce5074932d3b
git -C "$build_root" apply "$root/selected-preview.patch"
mkdir -p "$prefix"
PREFIX="$prefix" SOURCE="$build_root" python3 - <<'PY'
import json,os
from pathlib import Path
values={'PKGDATADIR':os.environ['PREFIX'],'LOCALEDIR':'/usr/share/locale','VERSION':'26.03.1-selected-preview','NAME_SUFFIX':'','APP_ID':'org.gnome.gitlab.YaLTeR.VideoTrimmer','G_LOG_DOMAIN':'VideoTrimmer','PROFILE':''}
(Path(os.environ['SOURCE'])/'src/config.rs').write_text(''.join(f'pub static {k}: &str = {json.dumps(v)};\n' for k,v in values.items()))
PY
cargo build --release --locked --manifest-path "$build_root/Cargo.toml"
cp "$build_root/target/release/video-trimmer" "$prefix/video-trimmer"
# Resources must come from the matching installed 26.03.1 package.
cp /usr/share/video-trimmer/video-trimmer.gresource "$prefix/"
echo 'Selected-range Video Trimmer installed. Keep the distribution package for its data and dependencies.'
