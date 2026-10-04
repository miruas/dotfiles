# Shortcuts

Only `keybinds.lua` is loaded for shortcuts. The shipped `dms/binds.lua` is an upstream reference and is not loaded by the main configuration.

| Keys | Action |
| --- | --- |
| Super + Enter / T | Alacritty |
| Super + E | Dolphin |
| Super + Space | App launcher |
| Super + V | Clipboard |
| Super + B | Control Center |
| Super + N | Notifications |
| Super + comma | DMS settings |
| Super + X | Power menu |
| Super + L | Lock |
| Super + Shift + / | Shortcut help |
| Super + Shift + E | Log out |
| Print / Super + Shift + S | Select screenshot region, copy, edit |
| Super + Print | Full screenshot, copy, edit |
| Super + Q | Close focused window |
| Super + F | Fullscreen toggle |
| Super + Shift + F | Maximized toggle |
| Super + Shift + Space | Floating toggle |
| Super + J | Toggle split |
| Super + arrows | Focus neighboring window |
| Super + Shift + arrows | Move window |
| Super + 1–9 / 0 | Workspace 1–9 / 10 |
| Super + Shift + 1–9 / 0 | Move window to workspace |
| Super + left drag | Move window |
| Super + right drag | Resize window |
| Super + W | Live wallpaper picker |
| Super + Shift + W | Live wallpaper on/off |
| Super + Alt + W | Still wallpaper browser |
| Super + Alt + T | Theme gallery toggle |
| Super + Ctrl + Shift + S | Display power toggle |
| Audio and media keys | Volume, mute, microphone and playback |

The pointer focuses the window underneath it; Super + Q closes that window. Settings, Satty, gThumb and supported video players open floating.

Edit `~/.config/hypr/keybinds.lua` with any text editor. Edit `hyprland.lua` for input and general behavior, `windowrules.lua` for floating rules, and `dms/outputs.lua` for monitors. DMS can regenerate its own color/layout files. Run `hyprctl reload` after manual changes and check `hyprctl configerrors` if something fails.
