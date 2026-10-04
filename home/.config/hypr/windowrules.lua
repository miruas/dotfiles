-- Photo viewers and video players open as movable floating windows.
hl.window_rule({
    name = "media-viewers-floating",
    match = { class = "^(org[.]kde[.]gwenview|gwenview|org[.]kde[.]haruna|haruna|mpv|vlc|Vlc|org[.]gnome[.]gThumb|gthumb|org[.]gnome[.]gitlab[.]YaLTeR[.]VideoTrimmer|video-trimmer|aurora-media|io[.]github[.]daniacosta_dev[.]AuroraMediaPlayer)$" },
    float = true,
})

hl.window_rule({ match = { class = "^local[.]dotfiles[.]ThemeManager$" }, float = true })

-- Screenshot editor and standalone theme settings stay movable.
hl.window_rule({
    name = "screenshot-editor-floating",
    match = { class = "^(com[.]gabm[.]satty|satty)$" },
    float = true,
})
