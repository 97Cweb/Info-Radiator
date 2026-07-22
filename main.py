from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMenu,
    QStyle,
    QSystemTrayIcon,
)

from radiator.window import RadiatorWindow


def create_tray_icon(
    app: QApplication,
    window: RadiatorWindow,
) -> QSystemTrayIcon:
    """
    Create the system-tray icon and its menu.

    The tray icon remains available even when the Radiator window is hidden.
    """
    icon = app.style().standardIcon(
        QStyle.StandardPixmap.SP_ComputerIcon
    )

    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("Info Radiator")

    menu = QMenu()

    show_action = QAction("Show Radiator", menu)
    show_action.triggered.connect(window.show_radiator)
    menu.addAction(show_action)

    hide_action = QAction("Hide Radiator", menu)
    hide_action.triggered.connect(window.hide)
    menu.addAction(hide_action)

    refresh_action = QAction("Refresh", menu)
    refresh_action.triggered.connect(window.refresh_data)
    menu.addAction(refresh_action)

    menu.addSeparator()

    quit_action = QAction("Quit", menu)

    def quit_application() -> None:
        window.allow_close()
        tray.hide()
        app.quit()

    quit_action.triggered.connect(quit_application)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)

    # A normal click restores the Radiator if it was hidden.
    tray.activated.connect(
        lambda reason: (
            window.show_radiator()
            if reason == QSystemTrayIcon.ActivationReason.Trigger
            else None
        )
    )

    tray.show()
    return tray


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Info Radiator")

    # Hiding the main window must not terminate the whole application.
    app.setQuitOnLastWindowClosed(False)

    window = RadiatorWindow()
    tray = create_tray_icon(app, window)

    # Keep a reference so Python does not garbage-collect the tray icon.
    app.tray_icon = tray  # type: ignore[attr-defined]

    # Wait until Qt has received the desktop's monitor geometry.
    QTimer.singleShot(250, window.show_radiator)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
