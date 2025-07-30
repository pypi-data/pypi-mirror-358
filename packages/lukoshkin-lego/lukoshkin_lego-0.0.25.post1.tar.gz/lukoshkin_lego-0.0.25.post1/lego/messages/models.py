from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, field_validator


class MessageDumpModel(BaseModel):
    text: str | None  # can be none if it's audio or media
    sender: str
    sender_role: str = "user"
    receiver: str = ""
    receiver_role: str | None = None
    sent_date: str | None
    other: dict[str, Any] | None = None

    @field_validator("sent_date")
    @classmethod
    def validate_date(cls, value):
        if value is None:
            return None

        try:
            datetime.fromisoformat(value)
        except ValueError:
            logger.warning(f"Invalid date format: {value}")
