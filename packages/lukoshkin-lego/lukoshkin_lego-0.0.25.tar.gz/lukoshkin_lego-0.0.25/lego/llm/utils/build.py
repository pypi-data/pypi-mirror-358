"""Likely common components between different containers."""

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)
from tenacity import (
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from lego.llm import router
from lego.llm.settings import (
    CustomLLMChatSettings,
    OpenAILikeProvider,
    RetrialPolicy,
)
from lego.logger import logger

AVAILABLE_PROVIDERS = {
    "gpt-4": ("openai", "gpt-4o"),
    "gpt-3.5": ("openai", "gpt-3.5-turbo"),
    "gpt-mini": ("openai", "gpt-4o-mini"),
    "mixtral": ("anyscale", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
}


def openai_like_provider(provider_alias: str) -> OpenAILikeProvider:
    """A function to register an LLM provider."""
    return OpenAILikeProvider(_env_prefix=f"{provider_alias}_")


def build_openai_model(
    llm_alias: str | tuple[str, str],
    key_idx: int,
    use_async: bool = False,
    **compl_kwargs,
) -> router.OpenAILikeCompletion | router.AsyncChatCompletion:
    """
    Build ChatCompletion model.

    Args:
        llm_alias: The alias mapping to a provider and a supported model.
        key_idx: The index of the key to use if the provider has multiple keys.
    """
    provider, model = (
        AVAILABLE_PROVIDERS[llm_alias]
        if isinstance(llm_alias, str)
        else llm_alias
    )
    provider = openai_like_provider(provider)
    settings = CustomLLMChatSettings(model=model, **compl_kwargs)
    router_kwargs = {
        "api_key": provider.api_keys[key_idx],
        "base_url": provider.base_url,
        "settings": settings,
    }
    return (
        router.AsyncChatCompletion(**router_kwargs)
        if use_async
        else router.OpenAILikeCompletion(**router_kwargs)
    )


def build_generic_router(
    core_llm_service: str | tuple[str, str],
    fallback_llm_service: str | tuple[str, str],
    use_async: bool = True,
) -> router.LLMRouter | router.AsyncLLMRouter:
    """
    A function to choose router setup.

    Valid aliases:
    - gpt-4 (OpenAI's gpt-4o)
    - gpt-3.5 (OpenAI's gpt-3.5-turbo-0125)
    - mixtral (Anyscale's mistralai/Mixtral-8x7B-Instruct-v0.1)

    The idea of this function is to quickly set up a router with
    some sane settings where the only configurable part is the type of
    models used for base and fallback calls. And it is assumed that, one
    specifies different aliases.
    """

    def before_sleep_loguru(case: str):
        def retry_logger(retry_state):
            logger.debug(retry_state.outcome.exception())
            logger.warning(
                f"Retrying {case}.. Attempt #{retry_state.attempt_number}\n"
            )

        return retry_logger

    base_retrial_policy = RetrialPolicy(
        retry=retry_if_exception_type(
            (
                APIConnectionError,
                APIError,
                APITimeoutError,
                InternalServerError,
                RateLimitError,
            )
        ),
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_loguru("base call"),
    )
    fallback_retrial_policy = RetrialPolicy(
        retry=retry_if_exception_type(
            (
                APIConnectionError,
                APIError,
                APITimeoutError,
                InternalServerError,
                RateLimitError,
            )
        ),
        wait=wait_random_exponential(min=1, max=20),
        stop=stop_after_attempt(2),
        before_sleep=before_sleep_loguru("fallback"),
    )
    base_services = [
        build_openai_model(core_llm_service, i, use_async=use_async)
        for i in range(3)
    ]
    fallback_services = [
        build_openai_model(fallback_llm_service, i, use_async=use_async)
        for i in range(2)
    ]
    router_kwargs = {
        "base_services": base_services,
        "base_retrial_policy": base_retrial_policy,
        "fallback_services": fallback_services,
        "fallback_retrial_policy": fallback_retrial_policy,
    }
    return (
        router.AsyncLLMRouter(**router_kwargs)
        if use_async
        else router.LLMRouter(**router_kwargs)
    )
