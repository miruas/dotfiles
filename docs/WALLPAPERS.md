# Themes and wallpapers

Open the gallery with **Super + Alt + T**, then use **Settings**. Enable **Change Wallpaper With Theme** if desired. Each palette has independent still-image and live-scene fields. Put still images in `~/Pictures/Wallpapers`; bind Steam Workshop scenes using the picker. Artwork and subscriptions are deliberately not distributed.

When live mode is enabled, theme switching requests the linked live scene directly. It avoids applying the still image as an intermediate step. In still mode, only the linked still image is used. A first load or a released GPU cache can still take time to render; RAM copies alone cannot guarantee an instant GPU transition.

## RAM policy

The source daemon copies linked scene files and shared assets into a private `/dev/shm/wallpaper-ram-cache-<uid>` directory. It polls every five seconds. It clears the source cache when total system memory usage exceeds **50 decimal GB**, and rebuilds below **48 GB**. Disabling theme wallpaper links also releases the cache. The thresholds assume a 64 GB machine; edit the daemon before using it on a smaller system. RAM storage accelerates reads; it is not a cache of fully decoded GPU scenes.

## NVIDIA VRAM policy

The policy daemon checks GPU memory and AI processes every two seconds. Inactive renderers are eligible for prewarming when memory permits. It releases parked renderers above approximately **4 GiB** of relevant GPU load or when Ollama, LM Studio or their worker processes are detected. Recovery uses a projected **3.75 GiB** budget to avoid oscillation. The policy accounts for its own parked allocations; an initial cache cost estimate is refined at runtime.

Parked renderers retain GPU allocations and are stopped with signals. Promotion uses the patched engine's first-frame marker and layer handoff, without screenshot polling. If prewarming is blocked, the old live wallpaper remains visible while the new one prepares. Active rendering still consumes VRAM. Unsupported GPU metrics disable prewarming rather than assuming free memory. The AI process detector is name-based, not a universal workload detector.

Status is generated under `~/.local/state/theme-manager/`. Do not commit it. Cache contents and scene files are excluded from this repository. Workshop content compatibility varies; the Linux renderer is a separate upstream project and does not implement every Windows Wallpaper Engine feature.
