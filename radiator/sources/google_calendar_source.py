from __future__ import annotations

from radiator.models import CalendarItem
from radiator.services.google_calendar import get_upcoming_events


class GoogleCalendarSource:
    def get_upcoming_events(
        self,
        maximum_events: int,
        days_ahead: int,
    ) -> list[CalendarItem]:
        return get_upcoming_events(
            maximum_events=maximum_events,
            days_ahead=days_ahead,
        )
