# Hyprland + Dank dotfiles

A compact, keyboard-driven desktop with DankMaterialShell, an animated theme gallery inside Dank Island, linked still/live wallpapers, floating media viewers and optional hardware profiles.

This repository exports a working desktop configuration as portable templates. Personal paths, wallpaper subscriptions, device identifiers, account data and runtime state have been removed. It does not include wallpaper artwork or compiled applications.

- Flat mouse acceleration, focus follows the pointer, small window gaps and English session locale.
- Twelve coordinated palettes: black/white, white/black, purple, yellow, red, blue, green, pink, orange, teal, cream and light lavender.
- **Super + Alt + T** opens and closes the native animated theme gallery. Settings open as a floating window.
- Each theme can have a still image and a Steam Wallpaper Engine scene. Still stays still; live stays live when changing themes.
- RAM source caching and adaptive NVIDIA VRAM prewarming, with automatic release under memory pressure or AI workloads.
- DMS screenshots copy immediately to the clipboard and open Satty for editing.
- gThumb views photos, GIFs and videos; an optional **Trim Video** button hands videos to a patched Video Trimmer that plays only the selected interval.
- An optional Control Center card manages cooling and CPU/GPU performance through a restricted local root bridge.

## Compatibility

The exported baseline uses **Hyprland 0.56.2 with Lua configuration**, **DMS 1.6.2**, **Quickshell 0.3.1**, gThumb 3.12.12 and Video Trimmer 26.03.1. It was used on Arch/CachyOS with AMD CPU and NVIDIA GPU. Older Hyprland releases using only `hyprland.conf` cannot load these Lua files. Other versions and hardware require adaptation; this is not a universal installer.

Upstream UI and application source revisions are pinned. The repository stores custom overlays and patches rather than an entire fork of each application. Shell/core versions must match. A source pin does not pin system packages.

## Start here

Read [installation and rollback](docs/INSTALL.md), then stage the configuration without changing the running desktop:

```sh
python3 install.py --stage ./staged-home
```

Review that directory. To install into your home directory with backups:

```sh
python3 install.py --stage ./staged-home-install --apply
```

Use a new empty staging directory for each invocation. Installation does not install packages, restart the shell, log you out, enable hardware controls or change global system language. Follow the setup guide for services and optional components.

## Guides

- [Shortcuts and configuration](docs/SHORTCUTS.md)
- [Themes, wallpaper links and memory policy](docs/WALLPAPERS.md)
- [Media viewer and selected-range video trimming](docs/MEDIA.md)
- [Optional cooling and performance profiles](docs/PROFILE-MANAGER.md)
- [Troubleshooting and privacy](docs/TROUBLESHOOTING.md)
- [Upstream revisions and licensing](docs/UPSTREAM.md)

Run `python3 scripts/validate.py` before publishing local changes. Never commit generated state, hardware mappings, tokens, Steam contents or application databases.
