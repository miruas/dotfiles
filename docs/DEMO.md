# 29-second showcase macro

Start GPU Screen Recorder, then press **Super + Alt + M**. Alternatively, run `dotfiles-demo` on the configured desktop, or `python3 scripts/demo.py` from this repository.

There is a five-second lead-in, followed by 29 seconds of desktop actions. Stop the recording after the showcase. This script does not start a recorder or capture the screen. `--dry-run` prints the timeline without changing anything. Ctrl+C in a terminal cancels and runs restoration. A lock prevents overlapping runs.

The macro opens one normal Alacritty terminal using exactly the launcher and terminal configuration used by **Super + T**, without custom demo panels or a replacement shell. Alongside it, Firefox opens the configured website in a new window containing one tab, and Mission Center opens a separate demo instance. The terminal's colors update with the shell palette. These three application windows are rearranged for the desktop showcase.

## Website setting

The public repository defaults to `https://example.org`. Set your own website locally without committing a personal domain:

```sh
DOTFILES_DEMO_URL=https://example.org dotfiles-demo
# Or:
python3 scripts/demo.py --url https://example.org
```

The local launcher can also export `DOTFILES_DEMO_URL` before starting the script. Firefox uses the normal profile and opens a new window, so existing browser windows and tabs remain outside cleanup. Mission Center uses a separate application ID to avoid taking over an existing instance. Both applications must be installed.

| Time | Scene |
| --- | --- |
| 0–3 s | Normal terminal, Firefox website and Mission Center tile into place |
| 3–12 s | Animated theme gallery; purple, yellow, red and blue colors |
| 12–14 s | Reorder application windows and rotate the split |
| 14–17 s | Float, center, move and resize Mission Center, then return it to tiling |
| 17–19 s | Fullscreen Firefox and restore its tiled position |
| 19–21 s | Floating theme settings |
| 21–24 s | Cooling and performance card |
| 24–26 s | Wallpaper picker |
| 26–29 s | Theme gallery and black/white closing palette |

The macro uses a free workspace between 91 and 99. It restores the starting theme and workspace, and closes only new recognized demo windows on that workspace. Existing app windows are excluded from cleanup. It does not launch media viewers, screenshot editors or Video Trimmer. The cooling card is shown without changing hardware profiles.

For live transitions, enable live mode beforehand with **Super + Shift + W**, link the demo palettes to your own scenes and open the theme gallery long enough for eligible caches to warm. The macro retains the starting still/live mode. Scenes not already prepared may load more slowly; a pending theme change causes the next preset to be skipped rather than overlapping changes. Restoration is outside the 29-second recording sequence.

The normal terminal prompt, Mission Center process list, browser UI, wallpaper titles and device labels may appear in your recording. Review the video before publishing it. Use the native customized Dank Island shell from this repository. Window choreography uses the [Hyprland Lua dispatcher API](https://wiki.hypr.land/configuring/code-snippets/). Commands and app identifiers can differ on other versions.

A local rehearsal verified the normal terminal, Firefox and Mission Center on the same demo workspace, Mission Center floating, preservation of existing windows, cleanup of new windows, and restoration of the starting theme/workspace. No screen capture was used for verification.
