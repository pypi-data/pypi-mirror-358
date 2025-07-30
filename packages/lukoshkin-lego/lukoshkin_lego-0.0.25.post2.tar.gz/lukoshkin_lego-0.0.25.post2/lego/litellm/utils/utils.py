from typing import Any

from litellm import Router

from lego.litellm.settings import (
    CustomLLMChatSettings,
    LiteLLMProxyModel,
    LiteLLMSettings,
    OpenAILikeProvider,
)
from lego.llm.utils.build import openai_like_provider
from lego.settings import AmazonAccess


def build_model_with_provider(
    model: str,
    provider: OpenAILikeProvider,
    model_alias: str = "default",
    model_settings: dict[str, Any] | None = None,
    proxy_settings: dict[str, str | int] | None = None,
) -> LiteLLMProxyModel:
    """Build a snapshot of a model with a `provider`."""
    return LiteLLMProxyModel(
        provider=provider,
        model_settings=CustomLLMChatSettings(
            model=model, **(model_settings or {})
        ),
        proxy_settings=LiteLLMSettings(
            model_alias=model_alias, **(proxy_settings or {})
        ),
    )


def build_bedrock_model(
    model: str,
    model_alias: str = "default",
    model_settings: dict[str, Any] | None = None,
    proxy_settings: dict[str, str | int] | None = None,
) -> LiteLLMProxyModel:
    """Build a snapshot of a Bedrock model."""
    return build_model_with_provider(
        model,
        AmazonAccess(),
        model_alias=model_alias,
        model_settings=model_settings,
        proxy_settings=proxy_settings,
    )


def build_openai_model(
    model: str,
    model_alias: str = "default",
    model_settings: dict[str, Any] | None = None,
    proxy_settings: dict[str, str | int] | None = None,
) -> LiteLLMProxyModel:
    """Build a snapshot of an OpenAI model."""
    openai_provider = openai_like_provider("openai")
    openai_provider = OpenAILikeProvider(api_key=openai_provider.api_key)
    return build_model_with_provider(
        model,
        openai_provider,
        model_alias=model_alias,
        model_settings=model_settings,
        proxy_settings=proxy_settings,
    )


class LiteLLMRouter(Router):
    """
    A compatibility wrapper around the `Router` class.

    FIXME: I need to come up with something better than this.
    I mean, it's OK for sync tasks, but when switching to async,
    I'll need to restructure it a bit.
    """

    def __init__(
        self,
        models: list[LiteLLMProxyModel],
        default_model_choice: str = "default",
        **kwargs,
    ):
        super().__init__(
            model_list=[model.serialize() for model in models],
            **kwargs,
        )
        self.default_model_choice = default_model_choice

    async def __call__(self, messages: list[dict[str, str]], **kwargs):
        model = kwargs.pop("model", None) or self.default_model_choice
        return await self.acompletion(model=model, messages=messages, **kwargs)

    def sync_call(self, messages: list[dict[str, str]], **kwargs):
        model = kwargs.pop("model", None) or self.default_model_choice
        return self.completion(model=model, messages=messages, **kwargs)


def build_litellm_router(
    models: list[LiteLLMProxyModel],
    default_model_choice: str = "default",
    **kwargs,
) -> Router:
    """Build a Bedrock model from a Pydantic model."""
    return LiteLLMRouter(
        models=models,
        default_model_choice=default_model_choice,
        **kwargs,
    )
