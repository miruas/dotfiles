#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
build_root=${XDG_CACHE_HOME:-$HOME/.cache}/dotfiles-build/linux-wallpaperengine
prefix=$HOME/.local/opt/linux-wallpaperengine
[ ! -e "$build_root" ] || { echo 'Build directory already exists; inspect it before rebuilding.' >&2; exit 1; }
git clone --recursive https://github.com/Almamu/linux-wallpaperengine.git "$build_root"
git -C "$build_root" checkout --detach b016d7d1fdcf4e5fd2f9c9fa420a8aaa07fee02d
git -C "$build_root" submodule update --init --recursive
git -C "$build_root" apply "$root/patches/linux-wallpaperengine.patch"
cmake -S "$build_root" -B "$build_root/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$build_root/build" -j "${BUILD_JOBS:-4}"
mkdir -p "$prefix"
cmake --install "$build_root/build" --prefix "$prefix"
echo 'Install the matching engine assets alongside the binary if your build outputs them. Steam Wallpaper Engine provides the shared assets.'
