from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QMouseEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from radiator.models import EmailItem


class EmailCard(QFrame):
    def __init__(
        self,
        item: EmailItem,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.item = item
        self.setObjectName("unreadCard" if item.unread else "card")
        self.setToolTip("Open in Gmail")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 7, 9, 7)
        layout.setSpacing(3)

        sender = QLabel(item.sender)
        sender.setObjectName("emailSender")
        sender.setWordWrap(True)
        layout.addWidget(sender)

        subject = QLabel(item.subject)
        subject.setObjectName("cardTitle")
        subject.setWordWrap(True)
        layout.addWidget(subject)

        snippet = QLabel(item.snippet)
        snippet.setObjectName("secondaryText")
        snippet.setWordWrap(True)
        snippet.setMaximumHeight(42)
        layout.addWidget(snippet)

        received = QLabel(item.received_at.strftime("%-I:%M %p"))
        received.setObjectName("timestamp")
        layout.addWidget(received)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.item.url:
            QDesktopServices.openUrl(QUrl(self.item.url))

        super().mousePressEvent(event)
