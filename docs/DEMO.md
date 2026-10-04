# Fast 20-second showcase macro

Start GPU Screen Recorder, then press **Super + Alt + M**. The demo starts immediately with no preparation countdown. You can also run `dotfiles-demo` or `python3 scripts/demo.py`. `--dry-run` prints the timeline without changing anything; `--countdown N` adds an optional lead-in. The script does not start a recorder or capture the screen. A lock prevents overlapping runs.

## Sequence

| Time | Scene |
| --- | --- |
| 0–2 s | Workspace 3: normal Super+T terminal, Firefox website and Mission Center |
| 2–4.7 s | Rapid rearrangement, split, floating, movement, resizing, tiling and fullscreen |
| 4.7–10.4 s | Workspace 4: animated theme gallery and purple, yellow, red, blue live wallpapers |
| 10.4–13.4 s | Live wallpaper off using the Super+Shift+W action; black/white and white/black still wallpapers |
| 13.4–14.2 s | Unobstructed still wallpaper |
| 14.2–17.4 s | Back to workspace 3: application colors, Control Center and theme/wallpaper settings |
| 17.4–20 s | Workspace 4: closing black/white palette and clean desktop shot |

Workspace 4 must be empty so application windows do not cover the wallpapers. Existing windows are never closed by cleanup. Only newly opened demo windows on workspaces 3/4 are tracked. The macro restores the starting theme, workspace, live on/off mode and exact theme-link settings after the sequence. Ctrl+C from a terminal also runs restoration. Restoration takes place outside the 20-second recording sequence.

## Wallpaper setup

Link live scenes for **purple**, **yellow**, **red** and **blue**, plus still images for **black-white** and **white-black** through the theme settings. Install the patched wallpaper engine and enable its plugin. The macro temporarily enables **Change Wallpaper With Theme**, starts live mode behind the application scene, then turns it off before the monochrome palettes. It restores the previous setting and live mode afterward.

No countdown or separate preparation step is required. Cached scenes transition fastest; loading a scene for the first time or a released GPU cache can delay a transition. Theme submission retries briefly instead of overlapping busy requests. Without linked wallpaper content, changing the palette cannot demonstrate a wallpaper change.

## Applications and website

Alacritty uses the same launcher and terminal configuration as Super+T, without custom demo text. Firefox opens a new window containing one website tab. Mission Center uses a separate demo application ID. Windows that appear on another workspace are moved to workspace 3 before choreography begins. Existing Firefox windows and tabs remain outside cleanup.

The public repository defaults to `https://example.org`. Configure a website locally using `DOTFILES_DEMO_URL` or `--url`, without committing a personal domain:

```sh
DOTFILES_DEMO_URL=https://example.org dotfiles-demo
python3 scripts/demo.py --url https://example.org
```

The normal terminal prompt, Mission Center process list, browser UI, wallpaper titles and device labels can appear in the recording. Review it before publishing. No media viewer, screenshot editor or Video Trimmer is launched. The hardware card is shown without changing fan or performance profiles.

A local rehearsal verified workspace 4 with a yellow palette and live mode on during the color sequence, white/black with live mode off during the monochrome sequence, preservation of original windows, cleanup of new windows, and exact restoration of theme-link settings plus the starting theme/workspace. No screen capture was used.
