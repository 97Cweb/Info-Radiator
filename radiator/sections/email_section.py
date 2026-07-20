from __future__ import annotations

from typing import Any

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget

from radiator.models import EmailItem
from radiator.sections.data_section import DataSection
from radiator.sources.email_source import EmailSource
from radiator.widgets.email_card import EmailCard


class EmailSection(DataSection):
    def __init__(
        self,
        source: EmailSource,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            title="EMAIL",
            refresh_interval_ms=5 * 60 * 1000,
            scrollable=True,
            parent=parent,
        )

        self.source = source
        self.add_header_button(
            text="+", callback=self._compose_email, tooltip="Compose email"
        )

    def fetch(self) -> list[EmailItem]:
        return self.source.get_unread_emails(
            maximum_emails=15,
        )

    def update(self, data: Any) -> None:
        emails: list[EmailItem] = data

        self.clear_items()

        if not emails:
            self.show_message("No unread email")
            return

        for email in emails:
            self.add_item(EmailCard(email))

    def _compose_email(self) -> None:
        QDesktopServices.openUrl(
            QUrl("https://mail.google.com/mail/u/0/#inbox?compose=new")
        )
