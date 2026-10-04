# Upstream revisions and licensing

| Component | Source | Revision |
| --- | --- | --- |
| DankMaterialShell | https://github.com/AvengeMedia/DankMaterialShell | 2db7646fe3ab47fddfdb8723f2da07d61a0d47ac (v1.6.2) |
| Dank QML Common | DMS submodule | 26396ce432d6c71c3f5367438f96f4a8d667e160 |
| DMS Wallpaper Engine plugin | https://github.com/sgtaziz/dms-wallpaperengine | e96718f5038f54546311a239ef0f6622f15c515a |
| linux-wallpaperengine | https://github.com/Almamu/linux-wallpaperengine | b016d7d1fdcf4e5fd2f9c9fa420a8aaa07fee02d |
| Video Trimmer | https://gitlab.gnome.org/YaLTeR/video-trimmer | 1c75471cc01ac3b58f2995814870ce5074932d3b (v26.03.1) |
| gThumb extension ABI | https://gitlab.gnome.org/GNOME/gthumb | 3.12.12 |

Original custom scripts, documentation and patches in this repository are GPL-3.0-or-later. DMS-derived QML retains its upstream MIT terms; see `licenses/DMS-MIT.txt`. The Linux wallpaper engine and Video Trimmer are GPL projects; their license texts are retained in `licenses/`. The gThumb bridge is source only and uses the GPL-compatible application API.

The pinned third-party wallpaper plugin repository does not provide a standalone license file. Its custom changes are distributed as a patch against the pinned upstream source, with upstream attribution retained; no license grant for the upstream project is inferred. Check the upstream project's terms before redistributing its full source.

No proprietary Steam assets, Workshop scenes, wallpaper artwork, binaries, CEF runtime or distribution packages are included. Builders fetch upstream source and retain its license obligations. Updating a pin requires reviewing and validating the overlays/patches against that new revision.
