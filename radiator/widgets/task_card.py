from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from radiator.models import TaskItem


class TaskCard(QFrame):
    completion_requested = Signal(object)

    def __init__(
        self,
        task: TaskItem,
        indent_level: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.task = task
        self.setObjectName("taskCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        main_layout = QHBoxLayout(self)
        left_margin = 8 + indent_level * 18
        main_layout.setContentsMargins(left_margin, 7, 8, 7)
        main_layout.setSpacing(8)

        if indent_level > 0:
            branch_label = QLabel("↳")
            branch_label.setObjectName("subtaskMarker")

            main_layout.addWidget(
                branch_label,
                alignment=Qt.AlignmentFlag.AlignTop,
            )

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(task.completed)
        self.checkbox.setToolTip("Mark task complete")

        self.checkbox.clicked.connect(self._completion_clicked)

        main_layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title_label = QLabel(task.title)
        title_label.setObjectName("taskTitle")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)

        if task.due is not None:
            due_label = QLabel(task.due.strftime("Due %A, %B %-d"))
            due_label.setObjectName("secondaryText")
            text_layout.addWidget(due_label)

        if task.notes:
            notes_label = QLabel(task.notes)
            notes_label.setObjectName("secondaryText")
            notes_label.setWordWrap(True)
            text_layout.addWidget(notes_label)

        main_layout.addLayout(text_layout, 1)

    def _completion_clicked(self, checked: bool) -> None:
        if not checked:
            return
        self.checkbox.setEnabled(False)
        self.completion_requested.emit(self.task)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.task.url:
            QDesktopServices.openUrl(QUrl(self.task.url))
            event.accept()
            return

        super().mousePressEvent(event)
