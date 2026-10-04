# 28-second showcase macro

Start GPU Screen Recorder, then press **Super + Alt + M**. Alternatively, run `dotfiles-demo` on the configured desktop, or `python3 scripts/demo.py` from this repository.

There is a five-second lead-in, followed by 28 seconds of desktop actions. Stop the recording after the showcase. This script does not start a recorder or capture the screen. `--dry-run` prints the timeline without changing anything. Ctrl+C in a terminal cancels and runs restoration. A lock prevents overlapping runs.

The macro opens three Alacritty terminals in succession, like repeatedly using **Super + T**. They use the normal terminal configuration and live color reload, so their backgrounds, text and ANSI swatches change with the shell palette. The terminal contents are neutral demo panels, without a username, hostname, command history or personal files.

| Time | Scene |
| --- | --- |
| 0–2 s | Three terminals tile into place |
| 2–11 s | Animated theme gallery; purple, yellow, red and blue colors across the shell and terminals |
| 11–13 s | Reorder terminals and rotate the split |
| 13–15 s | Float, center, move and resize a terminal, then return it to tiling |
| 16–18 s | Fullscreen a terminal and restore its tiled position |
| 18–20 s | Floating theme settings |
| 20–23 s | Cooling and performance card |
| 23–25 s | Wallpaper picker |
| 25–28 s | Theme gallery and black/white closing palette |

The macro uses a free workspace between 91 and 99. It restores the starting theme and workspace, and closes only new recognized demo windows on that workspace. Existing app windows are excluded from cleanup. It does not launch media viewers, screenshot editors or Video Trimmer. The cooling card is shown without changing hardware profiles.

For live transitions, enable live mode beforehand with **Super + Shift + W**, link the demo palettes to your own scenes and open the theme gallery long enough for eligible caches to warm. The macro retains the starting still/live mode. Scenes not already prepared may load more slowly; a pending theme change causes the next preset to be skipped rather than overlapping changes. Restoration is outside the 28-second recording sequence.

Wallpaper titles and device labels shown by your own shell may appear in your recording, so review the video before publishing it. Use the native customized Dank Island shell from this repository. Window choreography uses the [Hyprland Lua dispatcher API](https://wiki.hypr.land/configuring/code-snippets/). Commands and app identifiers can differ on other versions.

A local rehearsal verified three tiled terminals, the floating and fullscreen stages, cleanup of all demo terminals, and restoration of the starting theme and workspace. No screen capture was used for verification.
