# Installation and rollback

## Dependencies

Use the exported versions in the README. Install the distribution packages for Hyprland, DMS, Quickshell, uwsm, Alacritty, Dolphin, udiskie/UDisks2, PipeWire/WirePlumber, NetworkManager, BlueZ, wl-clipboard, Satty, Python, PyGObject, GTK 4 and Git. Enable your normal network, Bluetooth and audio services. DMS manages their UI; it does not replace the underlying daemons. Noto Sans, Noto Sans Mono, DejaVu Sans and the Breeze cursor are used.

`gsr-ui` is optional. Remove it from the start-session service list if GPU Screen Recorder UI is not installed. gThumb and Video Trimmer are optional media components. The wallpaper policy requires `nvidia-smi`; without usable GPU metrics it disables inactive VRAM prewarming. The active wallpaper renderer still needs its own GPU memory.

Ensure `en_US.UTF-8` is generated before starting the session. The shipped session environment is English. To change the entire operating system language, edit `/etc/locale.gen`, run `sudo locale-gen`, then `sudo localectl set-locale LANG=en_US.UTF-8`. This is a manual system-wide choice.

## Stage and review

From the repository root, run `python3 install.py --stage ./staged-home`. It fetches the pinned DMS sources and submodule plus the wallpaper plugin, then renders `@HOME@` placeholders. It does not build DMS core: install the matching core package separately.

Inspect `.config/hypr`, `.config/DankMaterialShell`, `.config/theme-manager` and the user services. The display configuration uses automatic preferred modes; set your refresh rate and outputs locally. The templates assume a normal home path without quote characters.

The installer uses real file copies. Changes to installed files do not change the repository. Existing managed files are backed up under `~/.local/state/dotfiles/backups/<timestamp>/`. Unmanaged files remain in place. Review old DMS service drop-ins to avoid an older `DMS_SHELL_DIR` override taking precedence.

Install with `python3 install.py --stage ./staged-home-install --apply`. Then:

```sh
systemctl --user daemon-reload
systemctl --user enable wallpaper-ram-cache.service wallpaper-gpu-cache-policy.service
mkdir -p "$HOME/Pictures/Wallpapers"
```

The session launcher starts DMS, udiskie and the optional recorder. The cache services belong to `graphical-session.target`. Log out and choose the Hyprland session supplied by your distribution, preferably its uwsm variant. Keep another desktop session available for recovery. Do not start Plasma or KWin inside Hyprland; using a KDE application does not start the Plasma desktop.

For live wallpapers, first build the engine using `./build-wallpaper-engine.sh`, install Steam Wallpaper Engine, subscribe to your own supported scenes and enable the DMS plugin in its settings. The builder needs a C++20 compiler, CMake, Ninja/Make, Wayland development tools, OpenGL/GLEW/GLUT, SDL2, MPV/FFmpeg, PulseAudio, DBus, FreeType, LZ4, zlib and the upstream submodules. It downloads a large CEF runtime. `BUILD_JOBS=4` is the default. Nothing is built automatically by the desktop installer.

The wallpaper plugin is initially disabled and theme wallpaper links are empty. Configure these through the theme settings. The optional Profile Manager card requires `--profile-ui` and the separate manual hardware setup.

## Restore previous files

Exit the Hyprland session before restoring. Copy the backed-up files to their corresponding home paths, remove files newly introduced by this repository that you no longer want, and run `systemctl --user daemon-reload`. Disable the two cache services if reverting them. A backup contains only files that were replaced, not a full home snapshot. The installer never changes disk mounts, root services, boot settings or package versions.
