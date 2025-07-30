import string
from abc import ABC, abstractmethod

from lego.lego_types import JSONDict
from lego.messages.models import MessageDumpModel


class DefaultRoleMapper:
    """
    Default role mapper assigning an ASCII lowercase char.

    It cannot assign more than 28 roles.
    """

    def __init__(self) -> None:
        self.chars = string.ascii_lowercase
        self.role_map: dict[str, str] = {}

    def __call__(self, role: str) -> str:
        if role in self.role_map:
            return self.role_map[role]

        role = self.chars[len(self.role_map)]
        self.role_map[role] = role
        return role


class MessageDumpParser(ABC):
    def __init__(self, role_map: dict[str, str] | None = None):
        self.role_mapper = role_map or DefaultRoleMapper()
        self.cached_entities: dict[str, str] = {}

    @classmethod
    @abstractmethod
    def parse_json_response(
        cls, json_response: JSONDict
    ) -> list[MessageDumpModel]:
        """Parse the JSON response from the API into a standardized format."""

    def history_to_text(
        self,
        structured_history: list[MessageDumpModel],
        omit_dates: bool = True,
        omit_receiver: bool = False,
    ):
        text = []
        for message in structured_history:
            if message.text is None:
                continue

            sender = message.sender
            receiver = (
                ""
                if omit_receiver
                else (
                    f"to {message.receiver}"
                    if message.receiver_role
                    else "in the chat"
                )
            )
            if self.role_mapper:
                sender = self._entity_nick(sender, message.sender_role)
                if not omit_receiver:
                    receiver = self._entity_nick(
                        receiver, message.receiver_role
                    )
            date_stamp = "" if omit_dates else f"{message.sent_date}:"
            text.append(
                f"{date_stamp}{sender}{receiver}: {message.text.strip()}"
            )
        return "\n".join(text), {v: k for k, v in self.cached_entities.items()}

    def _role_nick(self, role: str) -> str:
        if isinstance(self.role_mapper, DefaultRoleMapper):
            return self.role_mapper(role)
        return self.role_mapper.get(role, role)

    def _entity_nick(self, name: str, role: str) -> str:
        if name in self.cached_entities:
            return self.cached_entities[name]

        self.cached_entities[name] = (
            f"{self._role_nick(role)}_{len(self.cached_entities)}"
        )
        return self.cached_entities[name]
