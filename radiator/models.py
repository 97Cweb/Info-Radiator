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
    task_id: str
    title: str
    due: datetime | None = None
    completed: bool = False
    url: str | None = None


@dataclass(slots=True)
class EmailItem:
    sender: str
    subject: str
    snippet: str
    received: datetime
    unread: bool = False
    url: str | None = None
