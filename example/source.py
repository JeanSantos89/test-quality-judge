"""Toy password-reset module, used only as fixture for the example run."""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

TOKEN_TTL_MINUTES = 30


@dataclass
class ResetToken:
    email: str
    token: str
    expires_at: datetime
    used: bool = False


class PasswordResetService:
    def __init__(self):
        self._tokens: dict[str, ResetToken] = {}

    def request_reset(self, email: str) -> str:
        token = secrets.token_urlsafe(16)
        self._tokens[token] = ResetToken(
            email=email,
            token=token,
            expires_at=datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES),
        )
        return token

    def reset_password(self, token: str, new_password: str) -> bool:
        record = self._tokens.get(token)
        if record is None or record.used or record.expires_at < datetime.utcnow():
            return False
        record.used = True
        return True
