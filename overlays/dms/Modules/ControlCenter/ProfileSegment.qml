pragma ComponentBehavior: Bound
import QtQuick
import qs.Common
import qs.Widgets

Rectangle {
    id: root

    property bool busy: false
    readonly property real cellWidth: (width - 6) / options.length
    required property var options
    property string selected: ""
    readonly property int selectedIndex: options.findIndex(o => o.value === selected)

    signal chosen(string value)

    border.color: Theme.withAlpha(Theme.outline, 0.14)
    border.width: 1
    color: Theme.surfaceContainerLowest
    height: 48
    radius: 24

    Rectangle {
        color: Theme.primary
        height: root.height - 6
        opacity: root.busy ? 0.6 : 1
        radius: height / 2
        visible: root.selectedIndex >= 0
        width: root.cellWidth
        x: 3 + Math.max(0, root.selectedIndex) * root.cellWidth
        y: 3

        Behavior on opacity {
            NumberAnimation {
                duration: 180
            }
        }
        Behavior on x {
            NumberAnimation {
                duration: 260
                easing.type: Easing.OutCubic
            }
        }
    }
    Row {
        x: 3
        y: 3

        Repeater {
            model: root.options

            delegate: Rectangle {
                id: button

                required property var modelData
                readonly property bool selected: root.selected === modelData.value

                Accessible.description: selected ? "Selected" : "Select profile"
                Accessible.name: modelData.label
                Accessible.role: Accessible.Button
                activeFocusOnTab: true
                border.color: Theme.primary
                border.width: activeFocus ? 1 : 0
                color: mouse.containsMouse && !selected ? Theme.withAlpha(Theme.primary, 0.08) : "transparent"
                height: root.height - 6
                radius: height / 2
                scale: mouse.pressed ? 0.96 : 1
                width: root.cellWidth

                Behavior on color {
                    ColorAnimation {
                        duration: 160
                    }
                }
                Behavior on scale {
                    NumberAnimation {
                        duration: 120
                        easing.type: Easing.OutCubic
                    }
                }

                Accessible.onPressAction: {
                    if (!root.busy)
                        root.chosen(modelData.value);
                }
                Keys.onReturnPressed: {
                    if (!root.busy)
                        root.chosen(modelData.value);
                }
                Keys.onSpacePressed: {
                    if (!root.busy)
                        root.chosen(modelData.value);
                }

                Row {
                    anchors.centerIn: parent
                    spacing: 6

                    DankIcon {
                        anchors.verticalCenter: parent.verticalCenter
                        color: button.selected ? Theme.primaryText : Theme.surfaceVariantText
                        name: button.modelData.icon
                        size: 17

                        Behavior on color {
                            ColorAnimation {
                                duration: 160
                            }
                        }
                    }
                    StyledText {
                        anchors.verticalCenter: parent.verticalCenter
                        color: button.selected ? Theme.primaryText : Theme.surfaceText
                        font.pixelSize: 12
                        font.weight: Font.Medium
                        text: button.modelData.label

                        Behavior on color {
                            ColorAnimation {
                                duration: 160
                            }
                        }
                    }
                }
                MouseArea {
                    id: mouse

                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    enabled: !root.busy
                    hoverEnabled: true

                    onClicked: root.chosen(button.modelData.value)
                }
            }
        }
    }
}
