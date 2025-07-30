"""Settings for the llm package components."""

from collections.abc import Callable
from typing import TypedDict

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings
from tenacity import RetryCallState, retry_base
from tenacity.stop import stop_base
from tenacity.wait import wait_base

from lego.constants import ANYSCALE_MODELS, OPENAI_MODELS
from lego.lego_types import JSONDict
from lego.settings import APIKeys, settings_config


class OpenAILikeProvider(BaseSettings):
    """Settings for an LLM provider."""

    ## With `extra="ignore"`, we can put many settings in one .env file.
    model_config = settings_config(None)

    api_keys: APIKeys
    base_url: str | None = None

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_keys(cls, api_keys: str) -> APIKeys:
        """Parse the API keys."""
        return APIKeys.from_list_string(api_keys)

    @property
    def api_key(self) -> str:
        """Get the current API key."""
        return self.api_keys.api_key


class CustomLLMChatSettings(BaseModel):
    """Settings for LLM chat service."""

    model: str
    temperature: float = 0
    timeout: int = 200
    max_tokens: int = 3000
    seed: int = 0

    def compl_kwargs(self, messages: list[dict[str, str]]) -> JSONDict:
        """Compose the request payload."""
        return {
            "messages": messages,
            "temperature": self.temperature,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
            "timeout": self.timeout,
        }


class LlamaLLMChatSettings(BaseModel):
    """Settings for LLM chat service."""

    model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    temperature: float = 0
    max_tokens: int = 3000

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        """Validate the model name."""
        if value not in ANYSCALE_MODELS | OPENAI_MODELS:
            raise ValueError("Model not supported.")
        return value


class RetrialPolicy(TypedDict):
    """Policy of retrials after a failed request."""

    retry: retry_base
    wait: wait_base
    stop: stop_base
    before_sleep: Callable[[RetryCallState], None]
