from __future__ import annotations

from radiator.models import TaskItem
from radiator.services.google_tasks import (
    complete_task,
    get_incomplete_tasks,
)


class GoogleTaskSource:
    def get_incomplete_tasks(
        self,
        maximum_tasks: int = 25,
    ) -> list[TaskItem]:
        return get_incomplete_tasks(
            maximum_tasks=maximum_tasks,
        )

    def complete_task(
        self,
        task_list_id: str,
        task_id: str,
    ) -> None:
        complete_task(
            task_list_id=task_list_id,
            task_id=task_id,
        )
