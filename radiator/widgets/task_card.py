from __future__ import annotations

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from radiator.models import TaskItem


class TaskCard(QFrame):
    completion_changed = Signal(str, bool)

    def __init__(
        self,
        item: TaskItem,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.item = item
        self.setObjectName("card")

        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(7, 7, 7, 7)
        outer_layout.setSpacing(7)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(item.completed)
        self.checkbox.toggled.connect(self._completion_toggled)
        outer_layout.addWidget(self.checkbox)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        self.title_label = QLabel(item.title)
        self.title_label.setObjectName("cardTitle")
        self.title_label.setWordWrap(True)
        text_layout.addWidget(self.title_label)

        if item.due:
            due_label = QLabel(f"Due {item.due.strftime('%a %-I:%M %p')}")
            due_label.setObjectName("secondaryText")
            text_layout.addWidget(due_label)

        outer_layout.addLayout(text_layout, 1)

        if item.url:
            open_button = QPushButton("↗")
            open_button.setObjectName("iconButton")
            open_button.setToolTip("Open in Google Tasks")
            open_button.clicked.connect(self._open_task)
            outer_layout.addWidget(open_button)

        self._update_completed_style()

    def _completion_toggled(self, completed: bool) -> None:
        self.item.completed = completed
        self._update_completed_style()
        self.completion_changed.emit(self.item.task_id, completed)

    def _update_completed_style(self) -> None:
        self.title_label.setProperty("completed", self.item.completed)

        self.title_label.style().unpolish(self.title_label)
        self.title_label.style().polish(self.title_label)

    def _open_task(self) -> None:
        if self.item.url:
            QDesktopServices.openUrl(QUrl(self.item.url))
