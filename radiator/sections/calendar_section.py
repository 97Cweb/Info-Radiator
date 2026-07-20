from __future__ import annotations

from datetime import date
from typing import Any

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QWidget

from radiator.models import CalendarItem
from radiator.sections.data_section import DataSection
from radiator.sources.calendar_source import CalendarSource
from radiator.widgets.calendar_card import CalendarCard


class CalendarSection(DataSection):
    def __init__(
        self,
        source: CalendarSource,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            title="UP NEXT",
            refresh_interval_ms=5 * 60 * 1000,
            parent=parent,
        )
        self.source = source

        self.add_header_button(
            text="+",
            callback=self._create_event,
            tooltip="Create event",
        )

    def fetch(self) -> list[CalendarItem]:
        return self.source.get_upcoming_events(
            maximum_events=20,
            days_ahead=7,
        )

    def update(self, data: Any) -> None:
        events: list[CalendarItem] = data

        self.clear_items()

        if not events:
            self.show_message("No upcoming events")
            return

        current_date: date | None = None

        for event in events:
            event_date = event.start.date()

            if event_date != current_date:
                current_date = event_date

                heading = QLabel(self._day_heading(event_date))
                heading.setObjectName("calendarDayHeading")

                self.add_item(heading)

            self.add_item(CalendarCard(event))

    def _create_event(self) -> None:
        QDesktopServices.openUrl(
            QUrl("https://calendar.google.com/calendar/render?action=TEMPLATE")
        )

    @staticmethod
    def _day_heading(event_date: date) -> str:
        today = date.today()
        difference = (event_date - today).days

        if difference == 0:
            return "TODAY"

        if difference == 1:
            return "TOMORROW"

        if 2 <= difference <= 6:
            return f"THIS {event_date.strftime('%A').upper()}"

        if 7 <= difference <= 13:
            return f"NEXT {event_date.strftime('%A').upper()}"

        return event_date.strftime("%A, %B %-d").upper()
