from __future__ import annotations

from pathlib import Path
from collections.abc import Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"
TOKEN_PATH = PROJECT_ROOT / "token.json"

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/gmail.readonly",
]


class GoogleAuthError(RuntimeError):
    """Raised when Google authentication fails."""


def get_google_credentials() -> Credentials:
    """
    Load, refresh, or create Google OAuth credentials.

    The same token file is shared by Calendar, Tasks, Gmail, and other
    Google services used by Info Radiator.
    """

    credentials: Credentials | None = None

    try:
        if TOKEN_PATH.exists():
            credentials = Credentials.from_authorized_user_file(
                str(TOKEN_PATH),
                GOOGLE_SCOPES,
            )

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        if not credentials or not credentials.valid:
            if not CREDENTIALS_PATH.exists():
                raise GoogleAuthError(
                    f"Google credentials were not found at {CREDENTIALS_PATH}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                GOOGLE_SCOPES,
            )

            credentials = flow.run_local_server(
                port=0,
                open_browser=True,
            )

        TOKEN_PATH.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

        return credentials

    except GoogleAuthError:
        raise

    except Exception as error:
        raise GoogleAuthError(f"Could not authenticate with Google: {error}") from error
