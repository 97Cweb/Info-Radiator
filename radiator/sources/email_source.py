from __future__ import annotations

from typing import Protocol

from radiator.models import EmailItem


class EmailSource(Protocol):
    def get_unread_emails(
        self,
        maximum_emails: int = 15,
    ) -> list[EmailItem]: ...
