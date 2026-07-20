from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CalendarItem:
    title: str
    start: datetime
    end: datetime | None = None
    location: str | None = None
    url: str | None = None
    all_day: bool = False


@dataclass(slots=True)
class TaskItem:
    id: str
    title: str
    due: datetime | None = None
    notes: str | None = None
    url: str | None = None
    completed: bool = False
    task_list_id: str | None = None
    parent_id: str | None = None
    position: str = ""


@dataclass(slots=True)
class EmailItem:
    id: str
    thread_id: str
    sender: str
    subject: str
    snippet: str
    received_at: datetime
    unread: bool = False
    url: str | None = None
