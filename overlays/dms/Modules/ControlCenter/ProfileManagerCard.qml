pragma ComponentBehavior: Bound
import QtQuick
import Quickshell.Io
import qs.Common
import qs.Widgets

Rectangle {
    id: root

    property bool busy: false
    property string errorText: ""
    readonly property string fanMode: state.fan || ""
    property bool monitoring: false
    property string outputText: ""
    property string pendingOperation: ""
    property string pendingValue: ""
    readonly property string performanceMode: state.performance || ""
    property string queuedOperation: ""
    property string queuedValue: ""
    property var state: ({})

    function formatTemp(value) {
        return value === undefined || value === null ? "—" : Math.round(value) + "°";
    }
    function query(operation, value) {
        if (request.running) {
            if (operation !== "status") {
                queuedOperation = operation;
                queuedValue = value;
                busy = true;
            }
            return;
        }
        pendingOperation = operation;
        pendingValue = value || "";
        busy = operation !== "status";
        outputText = "";
        if (busy)
            errorText = "";
        request.command = operation === "status" ? ["/usr/local/bin/dank-profilectl", "status"] : ["/usr/local/bin/dank-profilectl", operation, value];
        request.running = true;
    }

    border.color: Theme.withAlpha(Theme.outline, 0.18)
    border.width: 1
    color: Theme.nestedSurface
    implicitHeight: body.implicitHeight + 32
    radius: Theme.cornerRadius

    Component.onCompleted: {
        if (monitoring)
            query("status", "");
    }
    onMonitoringChanged: {
        if (monitoring)
            query("status", "");
    }

    Process {
        id: request

        stdout: StdioCollector {
            onStreamFinished: root.outputText = text
        }

        onExited: (code, status) => {
            try {
                const result = JSON.parse(root.outputText);
                if (result.ok) {
                    root.state = result;
                    root.errorText = "";
                } else
                    root.errorText = result.error || "Could not apply profile.";
            } catch (e) {
                root.errorText = "Profile service unavailable.";
            }
            root.busy = false;
            root.pendingValue = "";
            root.pendingOperation = "";
            if (root.queuedOperation) {
                const operation = root.queuedOperation;
                const value = root.queuedValue;
                root.queuedOperation = "";
                root.queuedValue = "";
                Qt.callLater(() => root.query(operation, value));
            }
        }
    }
    IpcHandler {
        function fan(mode: string): string {
            if (["silent", "turbo", "bios"].indexOf(mode) < 0)
                return "UNKNOWN_PROFILE";
            root.query("fan", mode);
            return "APPLYING";
        }
        function performance(mode: string): string {
            if (["low", "max"].indexOf(mode) < 0)
                return "UNKNOWN_PROFILE";
            root.query("performance", mode);
            return "APPLYING";
        }
        function status(): string {
            return JSON.stringify({
                state: root.state,
                busy: root.busy,
                error: root.errorText
            });
        }

        target: "profile-manager"
    }
    Timer {
        interval: 2500
        repeat: true
        running: root.monitoring && !root.busy

        onTriggered: root.query("status", "")
    }
    Column {
        id: body

        spacing: 12
        width: root.width - 32
        x: 16
        y: 16

        Item {
            height: 25
            width: parent.width

            Row {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 8

                DankIcon {
                    color: Theme.surfaceText
                    name: "tune"
                    size: 20
                }
                StyledText {
                    color: Theme.surfaceText
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    text: "Profile Manager"
                }
            }
        }
        Row {
            spacing: 6
            width: parent.width

            Repeater {
                model: [
                    {
                        label: "CPU",
                        value: root.formatTemp(root.state.cpu_temp),
                        icon: "memory"
                    },
                    {
                        label: "GPU",
                        value: root.formatTemp(root.state.gpu_temp),
                        icon: "developer_board"
                    },
                    {
                        label: "AIO",
                        value: root.state.fan_rpm === undefined ? "—" : root.state.fan_rpm + " RPM",
                        icon: "air"
                    }
                ]

                delegate: Rectangle {
                    required property var modelData

                    color: Theme.withAlpha(Theme.surfaceContainerHighest, 0.5)
                    height: 35
                    radius: 10
                    width: (body.width - 12) / 3

                    Row {
                        anchors.centerIn: parent
                        spacing: 6

                        DankIcon {
                            anchors.verticalCenter: parent.verticalCenter
                            color: Theme.surfaceVariantText
                            name: modelData.icon
                            size: 14
                        }
                        StyledText {
                            anchors.verticalCenter: parent.verticalCenter
                            color: Theme.surfaceVariantText
                            font.pixelSize: 11
                            text: modelData.label
                        }
                        StyledText {
                            anchors.verticalCenter: parent.verticalCenter
                            color: Theme.surfaceText
                            font.pixelSize: 12
                            font.weight: Font.Medium
                            text: modelData.value
                        }
                    }
                }
            }
        }
        Column {
            spacing: 6
            width: parent.width

            Row {
                width: parent.width

                StyledText {
                    color: Theme.surfaceVariantText
                    font.letterSpacing: 1.3
                    font.pixelSize: 10
                    text: "COOLING"
                }
            }
            ProfileSegment {
                busy: root.busy
                options: [
                    {
                        value: "silent",
                        label: "Silent",
                        icon: "bedtime"
                    },
                    {
                        value: "turbo",
                        label: "Turbo",
                        icon: "bolt"
                    },
                    {
                        value: "bios",
                        label: "BIOS Controlled",
                        icon: "settings"
                    }
                ]
                selected: root.fanMode
                width: parent.width

                onChosen: value => root.query("fan", value)
            }
        }
        Column {
            spacing: 6
            width: parent.width

            Row {
                width: parent.width

                StyledText {
                    color: Theme.surfaceVariantText
                    font.letterSpacing: 1.3
                    font.pixelSize: 10
                    text: "PERFORMANCE"
                }
            }
            ProfileSegment {
                busy: root.busy
                options: [
                    {
                        value: "low",
                        label: "Low Performance",
                        icon: "eco"
                    },
                    {
                        value: "max",
                        label: "Max Performance",
                        icon: "speed"
                    }
                ]
                selected: root.performanceMode
                width: parent.width

                onChosen: value => root.query("performance", value)
            }
        }
        StyledText {
            color: Theme.error
            elide: Text.ElideRight
            font.pixelSize: 10
            maximumLineCount: 3
            text: root.errorText
            visible: root.errorText.length > 0
            width: parent.width
            wrapMode: Text.Wrap
        }
    }
}
