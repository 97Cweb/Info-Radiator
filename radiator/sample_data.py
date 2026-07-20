from __future__ import annotations

from datetime import datetime, timedelta

from radiator.models import CalendarItem, EmailItem, TaskItem


def sample_calendar_items() -> list[CalendarItem]:
    now = datetime.now().replace(second=0, microsecond=0)

    return [
        CalendarItem(
            title="Work on Info Radiator",
            start=now + timedelta(minutes=30),
            end=now + timedelta(hours=2),
            location="Workshop",
            url="https://calendar.google.com/",
        ),
        CalendarItem(
            title="Review train physics",
            start=now + timedelta(hours=4),
            url="https://calendar.google.com/",
        ),
    ]


def sample_tasks() -> list[TaskItem]:
    now = datetime.now().replace(second=0, microsecond=0)

    return [
        TaskItem(
            task_id="task-1",
            title="Finish switchstand model",
            due=now + timedelta(hours=2),
            url="https://tasks.google.com/",
        ),
        TaskItem(
            task_id="task-2",
            title="Check glue on G-scale lever",
            due=now + timedelta(days=1),
            url="https://tasks.google.com/",
        ),
        TaskItem(
            task_id="task-3",
            title="Plan Gmail integration",
            url="https://tasks.google.com/",
        ),
    ]


def sample_emails() -> list[EmailItem]:
    now = datetime.now().replace(second=0, microsecond=0)

    return [
        EmailItem(
            sender="Example Sender",
            subject="The parts have shipped",
            snippet="Your order is on its way and should arrive shortly.",
            received=now - timedelta(minutes=18),
            unread=True,
            url="https://mail.google.com/",
        ),
        EmailItem(
            sender="Project Update",
            subject="Switch-and-Shunt notes",
            snippet="Here are the latest notes from the physics work.",
            received=now - timedelta(hours=2),
            unread=False,
            url="https://mail.google.com/",
        ),
    ]
