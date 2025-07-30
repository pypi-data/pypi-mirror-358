from typing import Any, NewType, Protocol, TypedDict

from openai.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel, model_validator

Message = NewType("Message", dict[str, str | list[dict[str, Any]]])
Messages = NewType("Messages", list[Message])


class LegoLLMRouter(Protocol):
    """Protocol for LLM routers available in Lego."""

    def __call__(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,  # type: ignore[misc]
    ) -> Any:
        """Make a ChatCompletion request."""


class _Delta(TypedDict, total=False):
    content: str
    role: str


class _Choice(TypedDict, total=False):
    delta: _Delta
    index: int
    finish_reason: str | None


class StreamChunk(TypedDict, total=False):
    """The protocol for a stream chunk from OpenAI's ChatCompletion."""

    choices: list[_Choice]


class TextChunk(BaseModel):
    """Either a text from an output block or thinking one"""

    content: str = ""
    reasoning_content: str | None = None
    is_reasoning: bool = False

    @model_validator(mode="after")
    def check_just_one_set(self):
        if self.content and self.reasoning_content:
            raise ValueError(
                "Only one of `content` and `reasoning_content` can be set"
            )
        self.is_reasoning = self.reasoning_content is not None
        return self

    def __str__(self) -> str:
        return self.reasoning_content or self.content
