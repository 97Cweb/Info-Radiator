from __future__ import annotations

from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from radiator.models import TaskItem
from radiator.services.google_auth import (
    GoogleAuthError,
    get_google_credentials,
)


class GoogleTasksError(RuntimeError):
    """Raised when Google Tasks data cannot be loaded or updated."""


def get_incomplete_tasks(
    maximum_tasks: int = 25,
) -> list[TaskItem]:
    try:
        credentials = get_google_credentials()

        service = build(
            "tasks",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

        task_lists_response = service.tasklists().list().execute()
        task_lists = task_lists_response.get("items", [])

        tasks: list[TaskItem] = []

        for task_list in task_lists:
            task_list_id = task_list["id"]

            response = (
                service.tasks()
                .list(
                    tasklist=task_list_id,
                    showCompleted=False,
                    showHidden=False,
                    maxResults=maximum_tasks,
                )
                .execute()
            )

            for task in response.get("items", []):
                tasks.append(
                    TaskItem(
                        id=task["id"],
                        task_list_id=task_list_id,
                        title=task.get("title", "Untitled task"),
                        due=_parse_google_datetime(task.get("due")),
                        notes=task.get("notes"),
                        url=task.get("webViewLink"),
                        completed=task.get("status") == "completed",
                        parent_id=task.get("parent"),
                        position=task.get("position", ""),
                    )
                )

        tasks.sort(
            key=lambda task: (
                task.task_list_id or "",
                task.position,
            )
        )

        return tasks[:maximum_tasks]

    except GoogleAuthError as error:
        raise GoogleTasksError(str(error)) from error

    except HttpError as error:
        raise GoogleTasksError(f"Google Tasks API request failed: {error}") from error

    except Exception as error:
        raise GoogleTasksError(f"Could not access Google Tasks: {error}") from error


def complete_task(
    task_list_id: str,
    task_id: str,
) -> None:
    try:
        credentials = get_google_credentials()

        service = build(
            "tasks",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

        task = (
            service.tasks()
            .get(
                tasklist=task_list_id,
                task=task_id,
            )
            .execute()
        )

        task["status"] = "completed"

        service.tasks().update(
            tasklist=task_list_id,
            task=task_id,
            body=task,
        ).execute()

    except GoogleAuthError as error:
        raise GoogleTasksError(str(error)) from error

    except HttpError as error:
        raise GoogleTasksError(f"Could not complete Google task: {error}") from error

    except Exception as error:
        raise GoogleTasksError(f"Could not complete task: {error}") from error


def _parse_google_datetime(
    value: str | None,
) -> datetime | None:
    if not value:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()
