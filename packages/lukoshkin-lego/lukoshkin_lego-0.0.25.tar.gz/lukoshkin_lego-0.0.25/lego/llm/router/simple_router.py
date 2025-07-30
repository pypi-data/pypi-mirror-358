"""
A simple router for OpenAI-like chat completion clients.

A bit useless, but may help when running a sync code within an async context.

Can be used with custom retrial policies.
Randomly selects a model to make a chat completion request.
"""

import random
from collections import Counter

from openai import OpenAI
from openai.types.chat import chat_completion as openai_types
from tenacity import RetryError, retry

from lego.llm.exceptions import RouterExhaustedRetries
from lego.llm.settings import CustomLLMChatSettings, RetrialPolicy
from lego.logger import logger


class OpenAILikeCompletion:
    """An OpenAI-like client configured to make chat completion requests."""

    def __init__(
        self, api_key: str, base_url: str, settings: CustomLLMChatSettings
    ):
        """
        Initialize the client.

        Args:
            settings - default settings for the client. They can be overridden
            by `kwargs` in the `__call__` method, however.
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.settings = settings

    def __call__(self, messages: list[dict[str, str]], **kwargs):
        """Make a chat completion request."""
        if "model" in kwargs:
            raise ValueError("The 'model' should have been set earlier.")

        compl_kwargs = self.settings.compl_kwargs(messages)
        compl_kwargs.update(kwargs)

        return self.client.chat.completions.create(**compl_kwargs)


class LLMRouter:
    """Simple load-balancer for OpenAI-like chat completion clients."""

    def __init__(
        self,
        base_services: list[OpenAILikeCompletion],
        base_retrial_policy: RetrialPolicy | None = None,
        fallback_services: list[OpenAILikeCompletion] | None = None,
        fallback_retrial_policy: RetrialPolicy | None = None,
    ):
        self.base_services = base_services
        self.base_call = (
            retry(**base_retrial_policy)(self._base_call)
            if base_retrial_policy
            else self._base_call
        )
        self.fallback_services = fallback_services
        self.fallback = (
            retry(**fallback_retrial_policy)(self._fallback)
            if fallback_services and fallback_retrial_policy
            else self._fallback
        )

    def __call__(
        self,
        messages: list[dict[str, str]],
        call_counter: Counter[str] | None = None,
        **compl_kwargs,
    ) -> openai_types.ChatCompletion:
        """
        Make a request to OpenAI API.

        If request or series of request retries eventually fails,
        use fallback clients.
        """
        try:
            return self.base_call(messages, call_counter, **compl_kwargs)
        except RetryError:
            logger.warning("Switching to FALLBACK services..")
            try:
                return self.fallback(messages, call_counter, **compl_kwargs)
            except RetryError as exc:
                raise RouterExhaustedRetries from exc

    def _base_call(
        self,
        messages: list[dict[str, str]],
        call_counter: Counter[str] | None = None,
        **compl_kwargs: str,
    ) -> openai_types.ChatCompletion:
        if call_counter is not None:
            call_counter["base_call"] += 1

        ## S311: random is not suitable for security/cryptographic purposes
        ## However, we are OK with that
        return random.choice(self.base_services)(  # noqa: S311
            messages, **compl_kwargs
        )

    def _fallback(
        self,
        messages: list[dict[str, str]],
        call_counter: Counter[str] | None = None,
        **compl_kwargs: str,
    ) -> openai_types.ChatCompletion:
        if self.fallback_services is None:
            raise RetryError("And no fallbacks are available.")

        if call_counter is not None:
            call_counter["fallback"] += 1

        ## S311: random is not suitable for security/cryptographic purposes
        ## However, we are OK with that
        return random.choice(self.fallback_services)(  # noqa: S311
            messages, **compl_kwargs
        )
