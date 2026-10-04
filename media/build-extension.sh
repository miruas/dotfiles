#!/bin/sh
set -eu
cd "$(dirname "$0")"
gcc -shared -fPIC -O2 -Wall -Wextra -Wno-unused-parameter -Wno-deprecated-declarations -o libtrim_bridge.so trim_bridge.c $(pkg-config --cflags --libs gthumb gio-unix-2.0)
printf '%s\n' 'Built libtrim_bridge.so. Install it and trim_bridge.extension in /usr/lib/gthumb/extensions/.'
