from __future__ import annotations

from typing import Protocol

from radiator.models import TaskItem


class TaskSource(Protocol):
    def get_incomplete_tasks(
        self,
        maximum_tasks: int = 25,
    ) -> list[TaskItem]: ...

    def complete_task(
        self,
        task_list_id: str,
        task_id: str,
    ) -> None: ...
