# 28-second showcase macro

Generate the synthetic test image and four-second video before recording:

```sh
python3 scripts/demo.py --prepare
```

Start GPU Screen Recorder, then run:

```sh
python3 scripts/demo.py
```

There is a five-second lead-in, followed by 28 seconds of desktop actions. Stop the recording after the showcase. This script does not start a recorder or capture the screen. `--dry-run` prints the timeline without changing anything. Ctrl+C cancels and runs restoration.

The macro uses a free workspace between 91 and 99. It shows the animated theme gallery, four color palettes, floating theme settings, the cooling/performance card, wallpaper picker, app launcher, gThumb image viewer, Satty editing, gThumb's video/Trim Video view and Video Trimmer with a 1–3 second selection. It restores the starting theme and workspace, and closes only new recognized demo windows on the demo workspace. Existing app windows are excluded from cleanup.

For live transitions, enable live mode beforehand with **Super + Shift + W**, link the demo palettes to your own scenes and open the theme gallery long enough for eligible caches to warm. The macro retains the starting still/live mode. Scenes not already prepared may load more slowly; a pending theme change causes the next preset to be skipped rather than overlapping changes. Restoration is outside the 28-second recording sequence.

The example media are generated test patterns. The Satty step opens the generated PNG; it does not take a screenshot. The cooling card is shown without changing hardware profiles. The cache policy is listed in the overview, not stress-tested. The final step starts selected-range playback through the GTK action API, addressed to the newly launched Video Trimmer process only. This requires PyGObject and gdbus. If the player is not ready, press Play manually. The macro does not synthesize clicks inside applications. Wallpaper titles and device labels shown by your own shell may appear in your recording, so review the video before publishing it.

Use the native customized Dank Island shell from this repository. The macro has been checked for syntax, timeline and asset generation; the full UI sequence needs a rehearsal on your running desktop. Commands and app identifiers can differ on other versions.
