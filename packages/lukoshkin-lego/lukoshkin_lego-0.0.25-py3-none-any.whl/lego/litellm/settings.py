from typing import TypedDict, cast

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from lego.settings import AmazonAccess, nonone_serialize, settings_config


class OpenAILikeProvider(BaseSettings):
    """Settings for an LLM provider."""

    model_config = settings_config(None)

    api_key: str
    base_url: str | None = None


class ModelListComponent(TypedDict):
    """A component in the LiteLLM model list."""

    model_name: str
    litellm_params: dict[str, str]


class CustomLLMChatSettings(BaseModel, extra="allow"):  # type: ignore[call-arg]
    """Settings for LLM chat service."""

    model: str
    temperature: float | None = None
    timeout: int | None = None
    max_tokens: int | None = None
    seed: int | None = None


class LiteLLMSettings(BaseModel, extra="allow"):  # type: ignore[call-arg]
    """Settings for the LiteLLM model."""

    model_alias: str = "default"
    num_retries: int | None = None
    allowed_fails: int | None = None
    cooldown: int | None = None


class LiteLLMProxyModel(BaseModel):
    provider: AmazonAccess | OpenAILikeProvider
    model_settings: CustomLLMChatSettings
    proxy_settings: LiteLLMSettings = LiteLLMSettings()

    def serialize(
        self, target: str = "router"
    ) -> ModelListComponent | dict[str, str]:
        """Serialize the model list component."""
        provider: dict[str, str] = self._serialize_component(self.provider)
        model_settings = self._serialize_component(self.model_settings)
        proxy_settings = self._serialize_component(self.proxy_settings)
        model_alias = proxy_settings.pop("model_alias")
        if target == "router":
            return ModelListComponent(
                {
                    "model_name": model_alias,
                    "litellm_params": {
                        **provider,
                        **model_settings,
                        **proxy_settings,
                    },
                }
            )
        if target == "completion":
            return cast(
                dict[str, str],
                {
                    "model": model_alias,
                    **provider,
                    **model_settings,
                },
            )
        raise ValueError(f"Invalid target: {target}")

    def _serialize_component(
        self, component: BaseModel | BaseSettings
    ) -> dict[str, str]:
        json_dict = nonone_serialize(component.model_dump())
        if prefix := component.model_config.get("env_prefix"):
            return {f"{prefix}{key}": val for key, val in json_dict.items()}
        return json_dict
