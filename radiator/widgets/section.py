from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class SectionWidget(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("section")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 8, 10, 10)
        self._layout.setSpacing(6)

        self._header_layout = QHBoxLayout()
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")

        self.status_label = QLabel("")
        self.status_label.setObjectName("sectionStatus")

        self._header_layout.addWidget(self.title_label)
        self._header_layout.addStretch(1)
        self._header_layout.addWidget(self.status_label)

        self._layout.addLayout(self._header_layout)

        self._content = QVBoxLayout()
        self._content.setContentsMargins(0, 0, 0, 0)
        self._content.setSpacing(6)

        self._layout.addLayout(self._content)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def add_item(self, widget: QWidget) -> None:
        self._content.addWidget(widget)

    def clear_items(self) -> None:
        while self._content.count():
            item = self._content.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def add_header_button(
        self,
        text: str,
        callback: Callable[[], None],
        tooltip: str | None = None,
    ) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("sectionActionButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        if tooltip:
            button.setToolTip(tooltip)

        button.clicked.connect(callback)

        index = self._header_layout.indexOf(self.status_label)
        self._header_layout.insertWidget(index, button)
