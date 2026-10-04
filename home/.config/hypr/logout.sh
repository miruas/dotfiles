#!/bin/sh
set -eu
if uwsm check is-active compositor-only; then
    exec uwsm stop
fi
"$HOME/.config/hypr/stop-session.sh"
exec hyprctl dispatch 'hl.dsp.exit()'
