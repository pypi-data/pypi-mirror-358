"""Mocks used in the llm package."""

from abc import ABC, abstractmethod
from collections import Counter


class LLMRouter(ABC):
    """Load-balancer for LLMs."""

    @abstractmethod
    def __call__(
        self,
        messages: list[dict[str, str]],
        call_counter: Counter[str] | None = None,
        **compl_kwargs,
    ):
        """Make a request to OpenAI-like API."""


class ExtractionRouter(LLMRouter):
    """Load-balancer for extraction LLM services."""


class EvaluationRouter(LLMRouter):
    """Load-balancer for evaluation LLM services."""
