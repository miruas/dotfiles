#!/bin/bash
set -euo pipefail
mode="${1:-region}"
case "$mode" in region|full) ;; *) exit 2;; esac
mkdir -p "$HOME/Pictures/Screenshots"
target="$HOME/Pictures/Screenshots/screenshot_$(date +%Y-%m-%d_%H-%M-%S).png"
# Copy the original capture immediately, then open the editor.
# Only the editor's Save action creates a permanent file.
capture=$(mktemp "${XDG_RUNTIME_DIR:-/tmp}/dms-screenshot-XXXXXX.png")
trap 'rm -f -- "$capture"' EXIT
dms screenshot "$mode" --stdout --no-file --no-clipboard --no-notify > "$capture"
[ -s "$capture" ] || exit 0
wl-copy --type image/png < "$capture"
systemd-run --user --scope --collect --quiet --slice=app.slice --property=PartOf=graphical-session.target -- \
    satty --filename "$capture" --output-filename "$target"
