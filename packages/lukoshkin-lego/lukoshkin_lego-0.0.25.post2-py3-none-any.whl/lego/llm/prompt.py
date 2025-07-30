from collections.abc import Iterable

from lego.llm.types import Message


class ChatTemplate:
    """Separation tokens for messages-to-string conversion."""

    USER: tuple[str, str]
    SYSTEM: tuple[str, str]
    ASSISTANT: tuple[str, str]

    @classmethod
    def role_token_wrap(cls, role: str, content: str) -> str:
        """Wrap the role and content in the appropriate tokens."""
        if role == "user":
            return cls.USER[0] + content + cls.USER[1]
        if role == "system":
            return cls.SYSTEM[0] + content + cls.SYSTEM[1]
        if role == "assistant":
            return cls.ASSISTANT[0] + content + cls.ASSISTANT[1]

        raise ValueError(f"Unknown role: {role}")

    @classmethod
    def apply_chat_template(cls, prompt: Iterable[Message]) -> str:
        """Apply the chat template to the prompt."""
        return "".join(
            [
                cls.role_token_wrap(message["role"], message["content"])
                for message in prompt
                if message["content"]
            ]
        ).strip()


class ClaudeChatTemplate(ChatTemplate):
    """Claude chat template."""

    USER = ("Human: ", "\n\n")
    SYSTEM = ("System: ", "\n\n")
    ASSISTANT = ("Assistant: ", "\n\n")
