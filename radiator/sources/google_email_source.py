from __future__ import annotations

from radiator.models import EmailItem
from radiator.services.google_gmail import get_unread_emails


class GoogleEmailSource:
    def get_unread_emails(
        self,
        maximum_emails: int = 15,
    ) -> list[EmailItem]:
        return get_unread_emails(
            maximum_emails=maximum_emails,
        )
