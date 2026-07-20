from __future__ import annotations
from time import strftime
from typing import override

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QMouseEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from radiator.models import CalendarItem


class CalendarCard(QFrame):
    opened = Signal(CalendarItem)

    def __init__(self, item: CalendarItem, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.item = item
        self.setObjectName("card")
        self.setCursor(self.cursor())
        self.setToolTip("Open in Google Calendar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 7, 9, 7)
        layout.setSpacing(3)

        title = QLabel(item.title)
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        if item.all_day:
            time_text = item.start.strftime("%A - All day")
        elif item.end is None:
            time_text = item.start.strftime("%-I:%M %p")
        else:
            time_text = (
                f"{item.start.strftime('%-I:%M %p')} - {item.end.strftime('%-I:%M %p')}"
            )

        time_label = QLabel(time_text)
        time_label.setObjectName("secondaryText")
        layout.addWidget(time_label)

        if item.location:
            location = QLabel(item.location)
            location.setObjectName("secondaryText")
            location.setWordWrap(True)
            layout.addWidget(location)

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.opened.emit(self.item)

            if self.item.url:
                QDesktopServices.openUrl(QUrl(self.item.url))

        super().mousePressEvent(event)
