local function cmd(keys, command, options)
    hl.bind(keys, hl.dsp.exec_cmd(command), options)
end
cmd("SUPER + Return", "@HOME@/.config/hypr/launch-app.sh alacritty --config-file @HOME@/.config/hypr/terminal.toml")
cmd("SUPER + T", "@HOME@/.config/hypr/launch-app.sh alacritty --config-file @HOME@/.config/hypr/terminal.toml")
cmd("SUPER + E", "@HOME@/.config/hypr/launch-app.sh dolphin")
cmd("SUPER + space", "dms ipc call spotlight toggle")
cmd("SUPER + V", "dms ipc call clipboard toggle")
cmd("SUPER + B", "dms ipc call control-center toggle")
cmd("SUPER + N", "dms ipc call notifications toggle")
cmd("SUPER + comma", "dms ipc call settings focusOrToggle")
cmd("SUPER + X", "dms ipc call powermenu toggle")
cmd("SUPER + L", "dms ipc call lock lock")
cmd("SUPER + SHIFT + Slash", "dms ipc call keybinds toggle hyprland")
cmd("SUPER + SHIFT + E", "@HOME@/.config/hypr/logout.sh")
cmd("Print", "@HOME@/.config/hypr/screenshot.sh region", {allow_input_capture = true})
cmd("SUPER + Print", "@HOME@/.config/hypr/screenshot.sh full", {allow_input_capture = true})
hl.bind("SUPER + Q", hl.dsp.window.close())
hl.bind("SUPER + F", hl.dsp.window.fullscreen({mode = "fullscreen", action = "toggle"}))
hl.bind("SUPER + SHIFT + F", hl.dsp.window.fullscreen({mode = "maximized", action = "toggle"}))
hl.bind("SUPER + SHIFT + space", hl.dsp.window.float({action = "toggle"}))
hl.bind("SUPER + J", hl.dsp.layout("togglesplit"))
for _, direction in ipairs({"left", "right", "up", "down"}) do
    hl.bind("SUPER + " .. direction, hl.dsp.focus({direction = direction}))
    hl.bind("SUPER + SHIFT + " .. direction, hl.dsp.window.move({direction = direction}))
end
for i = 1, 10 do
    local key = i % 10
    hl.bind("SUPER + " .. key, hl.dsp.focus({workspace = i}))
    hl.bind("SUPER + SHIFT + " .. key, hl.dsp.window.move({workspace = i}))
end
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), {mouse = true})
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), {mouse = true})
cmd("XF86AudioRaiseVolume", "dms ipc call audio increment 3", {locked = true, repeating = true})
cmd("XF86AudioLowerVolume", "dms ipc call audio decrement 3", {locked = true, repeating = true})
cmd("XF86AudioMute", "dms ipc call audio mute", {locked = true})
cmd("XF86AudioMicMute", "dms ipc call audio micmute", {locked = true})
cmd("XF86AudioPlay", "dms ipc call mpris playPause", {locked = true})
cmd("XF86AudioPause", "dms ipc call mpris playPause", {locked = true})
cmd("XF86AudioNext", "dms ipc call mpris next", {locked = true})
cmd("XF86AudioPrev", "dms ipc call mpris previous", {locked = true})

-- Live wallpaper selection and stop/start.
cmd("SUPER + W", "@HOME@/.config/hypr/launch-app.sh @HOME@/.local/bin/theme-manager --live-picker")
cmd("SUPER + SHIFT + W", "@HOME@/.config/hypr/launch-app.sh @HOME@/.local/bin/theme-manager --toggle-live")

cmd("SUPER + SHIFT + S", "@HOME@/.config/hypr/screenshot.sh region", {allow_input_capture = true})

-- One-click color presets
cmd("SUPER + ALT + T", "@HOME@/.config/hypr/launch-app.sh @HOME@/.local/bin/theme-manager")

-- Static wallpaper browser
cmd("SUPER + ALT + W", "dms ipc call dash toggle wallpaper")


-- Toggle display power after releasing the shortcut keys.
hl.bind("SUPER + CTRL + SHIFT + S", function()
    hl.timer(function()
        hl.dispatch(hl.dsp.dpms({ action = "toggle" }))
    end, { timeout = 10, type = "oneshot" })
end, { allow_input_capture = true })

-- Run the desktop showcase macro.
cmd("SUPER + ALT + M", "@HOME@/.config/hypr/launch-app.sh @HOME@/.local/bin/dotfiles-demo")
