from __future__ import annotations

import base64
from datetime import datetime
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from radiator.models import EmailItem
from radiator.services.google_auth import (
    GoogleAuthError,
    get_google_credentials,
)


class GoogleGmailError(RuntimeError):
    """Raised when Gmail data cannot be loaded."""


def get_unread_emails(
    maximum_emails: int = 15,
) -> list[EmailItem]:
    try:
        credentials = get_google_credentials()

        service = build(
            "gmail",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                labelIds=["INBOX", "UNREAD"],
                maxResults=maximum_emails,
            )
            .execute()
        )

        message_refs = response.get("messages", [])
        emails: list[EmailItem] = []

        for message_ref in message_refs:
            message = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_ref["id"],
                    format="metadata",
                    metadataHeaders=[
                        "From",
                        "Subject",
                        "Date",
                    ],
                )
                .execute()
            )

            headers = {
                header["name"].casefold(): header["value"]
                for header in message.get("payload", {}).get("headers", [])
            }

            message_id = message["id"]
            thread_id = message["threadId"]

            emails.append(
                EmailItem(
                    id=message_id,
                    thread_id=thread_id,
                    sender=_decode_header(headers.get("from", "Unknown sender")),
                    subject=_decode_header(headers.get("subject", "(No subject)")),
                    snippet=message.get("snippet", ""),
                    received_at=_parse_email_datetime(headers.get("date")),
                    url=f"https://mail.google.com/mail/u/0/#inbox/{message_id}",
                    unread="UNREAD" in message.get("labelIds", []),
                )
            )

        emails.sort(
            key=lambda email: email.received_at,
            reverse=True,
        )

        return emails

    except GoogleAuthError as error:
        raise GoogleGmailError(str(error)) from error

    except HttpError as error:
        raise GoogleGmailError(f"Gmail API request failed: {error}") from error

    except Exception as error:
        raise GoogleGmailError(f"Could not access Gmail: {error}") from error


def _decode_header(value: str) -> str:
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def _parse_email_datetime(
    value: str | None,
) -> datetime:
    if not value:
        return datetime.min.astimezone()

    try:
        parsed = parsedate_to_datetime(value)

        if parsed.tzinfo is None:
            return parsed.astimezone()

        return parsed.astimezone()

    except (TypeError, ValueError, OverflowError):
        return datetime.min.astimezone()
