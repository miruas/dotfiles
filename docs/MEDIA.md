# Media tools

Install gThumb 3.12.12 and Video Trimmer 26.03.1. gThumb handles images, GIFs and video browsing. Video Trimmer is a separate focused editor.

## Trim Video button

Build the source extension with `cd media && ./build-extension.sh`. It needs the matching gThumb development headers, GCC, GTK 3 and gio-unix pkg-config metadata. Manually install `libtrim_bridge.so` and `trim_bridge.extension` in your distribution's gThumb extension directory, normally `/usr/lib/gthumb/extensions/`, using root privileges. This path is distribution-specific.

Enable **Video Trimmer Bridge** in gThumb's extension preferences. The button is shown for video files. It launches Video Trimmer through its desktop entry and closes only the originating viewer window after a successful launch. An error keeps the viewer open. Restart gThumb after installing the extension. Do not copy binaries between incompatible gThumb versions.

## Selected-range playback

Run `./media/build-video-trimmer.sh` with Rust/Cargo, GTK 4/libadwaita, GStreamer development libraries and the matching 26.03.1 distribution resources installed. The script fetches the pinned upstream revision, applies `selected-preview.patch`, and installs a local executable under `~/.local/opt/video-trimmer-selected/`. The desktop template and local wrapper select this executable. Keep the distribution package installed for its dependencies and resources.

Playback seeks to the selection start when outside the interval, and pauses at the selected end. Pressing Play again starts the interval again. Manual paused scrubbing remains available outside the selection. Video timestamps/frame scheduling can produce a small endpoint tolerance; this does not change the exported cut boundaries.

## Defaults

Set gThumb as the preferred image and video viewer through your file manager, or set the MIME types you use explicitly:

```sh
xdg-mime default org.gnome.gThumb.desktop image/png
xdg-mime default org.gnome.gThumb.desktop image/jpeg
xdg-mime default org.gnome.gThumb.desktop image/gif
xdg-mime default org.gnome.gThumb.desktop image/webp
xdg-mime default org.gnome.gThumb.desktop video/mp4
xdg-mime default org.gnome.gThumb.desktop video/webm
```

The installer does not overwrite your full MIME database. The Hyprland rules make both applications float by default.
