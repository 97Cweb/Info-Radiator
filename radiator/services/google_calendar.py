from __future__ import annotations

from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from radiator.models import CalendarItem
from radiator.services.google_auth import (
    GoogleAuthError,
    get_google_credentials,
)


class GoogleCalendarError(RuntimeError):
    """Raised when calendar data cannot be loaded."""


def get_upcoming_events(
    maximum_events: int = 10,
    days_ahead: int = 7,
) -> list[CalendarItem]:
    try:
        credentials = get_google_credentials()

        service = build(
            "calendar",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )

        now = datetime.now(timezone.utc)
        end = now + timedelta(days=days_ahead)

        response = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=end.isoformat(),
                maxResults=maximum_events,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

    except HttpError as error:
        raise GoogleCalendarError(
            f"Google Calendar API request failed: {error}"
        ) from error

    except Exception as error:
        raise GoogleCalendarError(
            f"Could not access Google Calendar: {error}"
        ) from error

    events: list[CalendarItem] = []

    for event in response.get("items", []):
        start_data = event.get("start", {})
        end_data = event.get("end", {})
        start = _parse_google_datetime(start_data)
        end_time = _parse_google_datetime(end_data)

        if start is None:
            continue

        events.append(
            CalendarItem(
                title=event.get("summary", "Untitled event"),
                start=start,
                end=end_time,
                location=event.get("location"),
                url=event.get("htmlLink"),
                all_day="date" in start_data,
            )
        )

    return events


def _parse_google_datetime(
    value: dict[str, str],
) -> datetime | None:
    """
    Convert either a timed Google Calendar value:

        {"dateTime": "2026-07-20T13:00:00-04:00"}

    or an all-day value:

        {"date": "2026-07-20"}
    """

    date_time_text = value.get("dateTime")

    if date_time_text:
        parsed = datetime.fromisoformat(date_time_text.replace("Z", "+00:00"))

        return parsed.astimezone()

    date_text = value.get("date")

    if date_text:
        return datetime.fromisoformat(date_text)

    return None
