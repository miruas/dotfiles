pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import qs.Common
import qs.Widgets
import qs.Services

FocusScope {
    id: root
    required property var controller
    property var presets: []
    property string selected: ""
    property string message: ""
    property bool busy: false
    property var wallpaperConfig: ({})
    property var readyImages: ({})
    readonly property var wallpaperEngine: PluginService.pluginDaemonInstances["linuxWallpaperEngine"] ?? null
    readonly property bool preparing: wallpaperEngine?.warming ?? false
    readonly property int preparedCount: { wallpaperEngine?.cacheRevision; return wallpaperEngine?.cacheReadyCount() ?? 0 }
    FileView {
        path: "@HOME@/.config/theme-manager/settings.json"
        onLoaded: {
            const config=JSON.parse(text());
            root.wallpaperConfig=config;
            if (!config.changeWallpaperWithTheme || !root.wallpaperEngine?.ready) return;
            const ids=Object.values(config.wallpapers || {}).map(x => x.live?.sceneId).filter(x => x);
            root.wallpaperEngine.warmScenes(ids.join(","));
        }
    }
    function focusFace() { root.forceActiveFocus(); return true; }
    function choose(id) {
        if (busy) return;
        busy = true; message = "Applying theme...";
        let wallpaperApplied = false;
        const links = root.wallpaperConfig.wallpapers?.[id] ?? {};
        if (root.wallpaperConfig.changeWallpaperWithTheme) {
            if (root.wallpaperEngine?.ready && links.live?.sceneId) {
                wallpaperApplied = root.wallpaperEngine.connectedMonitors().every(m => root.wallpaperEngine.ipcSet(links.live.sceneId,m).startsWith("Set "));
            } else if (!root.wallpaperEngine?.ready && links.image?.path && root.readyImages[id]) {
                SessionData.setWallpaperTransition("none");
                if (!SessionData.perMonitorWallpaper) SessionData.setPerMonitorWallpaper(true);
                for (const screen of Quickshell.screens) {
                    SessionData.setMonitorWallpaper(screen.name,links.image.path);
                    SessionData.setMonitorCyclingFolderPath(screen.name,"");
                }
                wallpaperApplied = true;
            }
        }
        submit.command = ["@HOME@/.config/hypr/launch-app.sh", "@HOME@/.local/bin/theme-manager", "--apply", id];
        if (wallpaperApplied) submit.command = submit.command.concat(["--wallpaper-applied"]);
        submit.running = true;
    }
    FileView {
        path: "@HOME@/.config/theme-manager/presets.json"
        onLoaded: root.presets = JSON.parse(text())
    }
    FileView {
        id: selectedFile
        path: "@HOME@/.config/theme-manager/selected"
        watchChanges: true
        onFileChanged: reload()
        onLoaded: root.selected = text().trim()
    }
    FileView {
        id: resultFile
        path: "@HOME@/.config/theme-manager/apply-status.json"
        watchChanges: true
        onFileChanged: reload()
        onLoaded: {
            const data = JSON.parse(text());
            root.busy = data.state === "running";
            root.message = data.message || "";
        }
    }
    IpcHandler {
        target: "themeGallery"
        function status(): string {
            return JSON.stringify({count:root.presets.length, selected:root.selected, busy:root.busy, preparing:root.preparing, prepared:root.preparedCount, message:root.message});
        }
        function apply(name: string): string {
            if (!root.presets.some(p => p.id === name)) return "UNKNOWN_THEME";
            if (root.busy) return "BUSY";
            root.choose(name);return "SUBMITTED";
        }
    }
    Process {
        id: submit
        onExited: (code, status) => {
            if (code !== 0) { root.busy = false; root.message = "Could not start the theme switch."; }
        }
    }
    Process {
        id: settings
        command: ["@HOME@/.config/hypr/launch-app.sh", "@HOME@/.local/bin/theme-manager", "--settings"]
    }
    Column {
        anchors.fill: parent
        anchors.margins: 22
        spacing: 14
        Row {
            width: parent.width
            spacing: 8
            StyledText {
                width: parent.width - settingsButton.width - closeButton.width - 16
                anchors.verticalCenter: parent.verticalCenter
                text: "Themes"
                font.pixelSize: Theme.fontSizeLarge
                font.weight: Font.DemiBold
                color: Theme.surfaceText
            }
            DankButton {
                id: settingsButton
                text: "Settings"
                iconName: "settings"
                onClicked: { settings.running = true; root.controller.requestCollapse(); }
            }
            DankButton {
                id: closeButton
                iconName: "close"
                width: 40
                horizontalPadding: 0
                onClicked: root.controller.requestCollapse()
            }
        }
        Flickable {
            id: gallery
            width: parent.width
            height: parent.height - 40 - footer.height - parent.spacing * 2
            contentWidth: width
            contentHeight: grid.height
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            Grid {
                id: grid
                width: parent.width
                columns: 3
                spacing: 12
                Repeater {
                    model: root.presets
                    delegate: Rectangle {
                        id: card
                        required property var modelData
                        readonly property bool chosen: root.selected === modelData.id
                        Image {
                            id: preparedImage
                            visible: false
                            source: root.wallpaperConfig.wallpapers?.[card.modelData.id]?.image?.path ?? ""
                            asynchronous: true
                            cache: true
                            sourceSize: Qt.size(Quickshell.screens[0]?.width ?? 1920,Quickshell.screens[0]?.height ?? 1080)
                            onStatusChanged: root.readyImages[card.modelData.id] = status === Image.Ready
                        }
                        width: (grid.width - grid.spacing * 2) / 3
                        height: 116
                        radius: 18
                        color: cardHover.hovered ? Theme.surfaceContainerHighest : Theme.surfaceContainer
                        border.width: chosen ? 2 : 0
                        border.color: Theme.primary
                        opacity: root.busy ? 0.65 : 1
                        scale: click.pressed ? 0.97 : 1
                        activeFocusOnTab: !root.busy
                        Behavior on scale { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
                        Behavior on color { ColorAnimation { duration: Theme.shortDuration } }
                        Keys.onReturnPressed: root.choose(modelData.id)
                        Keys.onSpacePressed: root.choose(modelData.id)
                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 7
                            Rectangle {
                                width: parent.width; height: 42; radius: 10
                                color: card.modelData.colors[0]
                                Row {
                                    anchors.fill: parent; anchors.margins: 7; spacing: 6
                                    Rectangle { width: 12; height: parent.height; radius: 4; color: card.modelData.colors[2] }
                                    Rectangle {
                                        width: parent.width - 18; height: parent.height; radius: 5
                                        color: card.modelData.colors[1]
                                        Column {
                                            anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 6; spacing: 4
                                            Rectangle { width: 42; height: 3; radius: 2; color: card.modelData.colors[2] }
                                            Rectangle { width: 64; height: 3; radius: 2; color: card.modelData.colors[3] }
                                        }
                                    }
                                }
                            }
                            StyledText { text: card.modelData.name; color: Theme.surfaceText; font.pixelSize: 13; font.weight: Font.DemiBold }
                            Row {
                                width: parent.width; spacing: 5
                                Repeater {
                                    model: card.modelData.colors
                                    delegate: Rectangle {
                                        required property string modelData
                                        width: 10; height: 10; radius: 5; color: modelData
                                    }
                                }
                                StyledText { text: card.modelData.light ? "LIGHT" : "DARK"; color: Theme.surfaceVariantText; font.pixelSize: 9 }
                            }
                        }
                        HoverHandler { id: cardHover }
                        TapHandler { id: click; enabled: !root.busy; onTapped: root.choose(card.modelData.id) }
                    }
                }
            }
        }
        Column {
            id: footer
            width: parent.width
            spacing: 8
            Rectangle { width: parent.width; height: 1; color: Theme.outlineVariant }
            StyledText {
                width: parent.width
                text: root.preparing ? "Background preparation: " + root.preparedCount + " / " + (root.wallpaperEngine?.cacheScenes.length ?? 0) : root.message || "Current theme: " + (root.presets.find(p => p.id === root.selected)?.name || root.selected) + "."
                color: Theme.surfaceText; font.pixelSize: 13; wrapMode: Text.WordWrap
            }
            StyledText {
                text: "Super + Alt + T to toggle. Esc to close."
                color: Theme.surfaceVariantText; font.pixelSize: 12
            }
        }
    }
    Keys.onEscapePressed: root.controller.requestCollapse()
    Component.onCompleted: root.controller.markVisualsReady("themes")
    Component.onDestruction: { root.controller.setVisualsReady("themes", false) }
}
