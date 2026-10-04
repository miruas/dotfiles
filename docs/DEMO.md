# 24-second showcase macro

Start GPU Screen Recorder, then run:

```sh
python3 scripts/demo.py
```

On the configured desktop, the local shortcut command is `dotfiles-demo`.

There is a five-second lead-in, followed by 24 seconds of desktop actions. Stop the recording after the showcase. No asset preparation is needed. This script does not start a recorder or capture the screen. `--dry-run` prints the timeline without changing anything. Ctrl+C cancels and runs restoration.

The macro uses a free workspace between 91 and 99. It shows the animated theme gallery, six color palettes, floating theme settings, the cooling/performance card, wallpaper picker and app launcher, then returns to the theme gallery for the closing transitions. It restores the starting theme and workspace, and closes only new recognized demo windows on the demo workspace. Existing app windows are excluded from cleanup. It does not launch media viewers, screenshot editors or Video Trimmer.

For live transitions, enable live mode beforehand with **Super + Shift + W**, link the demo palettes to your own scenes and open the theme gallery long enough for eligible caches to warm. The macro retains the starting still/live mode. Scenes not already prepared may load more slowly; a pending theme change causes the next preset to be skipped rather than overlapping changes. Restoration is outside the 24-second recording sequence.

The cooling card is shown without changing hardware profiles. The cache policy is listed in the overview, not stress-tested. Wallpaper titles and device labels shown by your own shell may appear in your recording, so review the video before publishing it.

Use the native customized Dank Island shell from this repository. The macro has been checked for syntax and timeline; the full UI sequence needs a rehearsal on your running desktop. Commands and app identifiers can differ on other versions.
