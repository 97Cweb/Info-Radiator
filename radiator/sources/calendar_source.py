from __future__ import annotations

from typing import Protocol

from radiator.models import CalendarItem


class CalendarSource(Protocol):
    """
    Anything capable of supplying calendar items.

    A Protocol does not require inheritance. Any class with a matching
    get_upcoming_events() method can be used as a CalendarSource.
    """

    def get_upcoming_events(
        self,
        maximum_events: int,
        days_ahead: int,
    ) -> list[CalendarItem]: ...
