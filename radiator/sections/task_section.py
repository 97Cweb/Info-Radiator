from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget

from radiator.models import TaskItem
from radiator.sections.refreshable_section import DataSection
from radiator.sources.task_source import TaskSource
from radiator.widgets.task_card import TaskCard


class TaskActionSignals(QObject):
    succeeded = Signal()
    failed = Signal(str)


class CompleteTaskWorker(QRunnable):
    def __init__(
        self,
        source: TaskSource,
        task: TaskItem,
    ) -> None:
        super().__init__()

        self.source = source
        self.task = task
        self.signals = TaskActionSignals()

    @Slot()
    def run(self) -> None:
        if self.task.task_list_id is None:
            self.signals.failed.emit("Task has no task-list ID")
            return

        try:
            self.source.complete_task(
                task_list_id=self.task.task_list_id,
                task_id=self.task.id,
            )
        except Exception as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.succeeded.emit()


class TaskSection(DataSection):
    def __init__(
        self,
        source: TaskSource,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            title="TASKS",
            refresh_interval_ms=5 * 60 * 1000,
            parent=parent,
        )

        self.source = source
        self._action_thread_pool = QThreadPool.globalInstance()
        self.add_header_button(
            text="+", callback=self._create_task, tooltip="Create task"
        )

    def fetch(self) -> list[TaskItem]:
        return self.source.get_incomplete_tasks(
            maximum_tasks=25,
        )

    def update(self, data: Any) -> None:
        tasks: list[TaskItem] = data

        self.clear_items()

        if not tasks:
            self.show_message("No incomplete tasks")
            return

        tasks_by_parent: dict[str | None, list[TaskItem]] = {}

        for task in tasks:
            tasks_by_parent.setdefault(task.parent_id, []).append(task)

        rendered_ids: set[str] = set()

        for task in tasks:
            if task.parent_id is not None:
                continue

            self._add_task_tree(
                task=task,
                tasks_by_parent=tasks_by_parent,
                rendered_ids=rendered_ids,
                depth=0,
            )

        # Defensive fallback for orphaned subtasks whose parent was not returned.
        for task in tasks:
            if task.id not in rendered_ids:
                self._add_task_tree(
                    task=task,
                    tasks_by_parent=tasks_by_parent,
                    rendered_ids=rendered_ids,
                    depth=0,
                )

    def _add_task_tree(
        self,
        task: TaskItem,
        tasks_by_parent: dict[str | None, list[TaskItem]],
        rendered_ids: set[str],
        depth: int,
    ) -> None:
        if task.id in rendered_ids:
            return

        rendered_ids.add(task.id)

        card = TaskCard(
            task=task,
            indent_level=depth,
        )

        card.completion_requested.connect(self._complete_task)

        self.add_item(card)

        for child in tasks_by_parent.get(task.id, []):
            self._add_task_tree(
                task=child,
                tasks_by_parent=tasks_by_parent,
                rendered_ids=rendered_ids,
                depth=depth + 1,
            )

    @Slot(object)
    def _complete_task(self, task: TaskItem) -> None:
        self.set_status("Updating…")

        worker = CompleteTaskWorker(
            source=self.source,
            task=task,
        )

        worker.signals.succeeded.connect(self._task_completed)
        worker.signals.failed.connect(self._task_completion_failed)

        self._action_thread_pool.start(worker)

    @Slot()
    def _task_completed(self) -> None:
        self.refresh()

    @Slot(str)
    def _task_completion_failed(self, message: str) -> None:
        print(f"Could not complete task: {message}")
        self.set_status("Error")

    def _create_task(self) -> None:
        QDesktopServices.openUrl(
            QUrl("https://calendar.google.com/calendar/u/0/r/tasks")
        )
