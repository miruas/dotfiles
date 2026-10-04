#!/bin/sh
set -eu
# UWSM handles its own service and environment teardown.
if uwsm check is-active compositor-only; then
    exit 0
fi
systemctl --user stop dank-hyprland.service udiskie-hyprland.service
systemctl --user stop hyprland-dank-session.target
systemctl --user unset-environment WAYLAND_DISPLAY DISPLAY HYPRLAND_INSTANCE_SIGNATURE XDG_CURRENT_DESKTOP
