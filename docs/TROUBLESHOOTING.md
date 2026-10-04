# Troubleshooting and privacy

## Session starts with a blank screen

Switch to a TTY and inspect `hyprctl configerrors` and the user service journal. Confirm that Hyprland supports Lua, DMS core matches 1.6.2, the pinned shell source and submodule are present, and `DMS_SHELL_DIR` resolves to the installed shell. Use another available desktop session while repairing. Do not repeatedly start competing shell instances.

## Applications disappear with the shell

Applications launch through `launch-app.sh`, using uwsm when available or a separate systemd app scope. Keep this launcher in DMS's launch prefix. Avoid attaching applications to the lifetime of a transient shell process. User services remain tied to the graphical session so logging out still stops session components.

## Screenshot editing or shortcuts fail

Confirm the Print key binding in `keybinds.lua`, Satty and wl-clipboard availability, and the DMS core version. The region capture copies the original image immediately; saving an edited copy is a separate Satty action. This repository's validation never triggers screen capture.

## Wallpaper transition stalls

Check that the patched engine is installed with its libraries/resources and that the plugin uses `wallpaper-ram-launch`. Check user journals for the RAM and GPU policy daemons and generated state under `~/.local/state/theme-manager`. Check your own workshop scene paths. A released cache requires GPU preparation again; warming cannot make unsupported content work.

## Gaming

The desktop uses no blur and a flat mouse acceleration profile. This does not guarantee higher FPS or fix Vulkan/driver failures. CS2 Vulkan errors, Wine game compatibility and Sober issues remain application/driver concerns. Do not change NVIDIA driver versions, game launch flags or device permissions merely by copying these dotfiles. GPU Screen Recorder remains an optional independent service.

## Privacy boundaries

Only desktop preferences, source code, templates, overlays and patches are included. No screenshots, account credentials, SSH material, API tokens, private application settings, mount UUIDs, monitor serials, hardware device UIDs, user wallpaper lists, Steam subscriptions, fan-state files or overclock curves are exported.

`@HOME@` is rendered on installation, not committed as a real user path. Root credentials are generated only by the explicitly invoked hardware setup. Installed programs generate normal local state outside this repository. GitHub publication still identifies the repository owner through GitHub itself; that is separate from the configuration contents.
