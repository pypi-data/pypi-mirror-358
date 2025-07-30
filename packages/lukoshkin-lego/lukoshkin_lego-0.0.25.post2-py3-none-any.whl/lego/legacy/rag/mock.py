"""Mocks used across the rag submodule."""

from abc import ABC, abstractmethod

from lego.lego_types import OneOrMany
from lego.llm.settings import LlamaLLMChatSettings
from lego.rag.models import SetupConfig


class CollectionSet(ABC):
    """Basic ingestion and retrieval functionality without LLMs."""

    @abstractmethod
    def update_collection(self, collection: str, cfg: SetupConfig):
        """Register a new collection or update existing one."""

    @abstractmethod
    def drop_collection(self, collection: OneOrMany[str]):
        """Drop a collection by name."""

    @abstractmethod
    def prepare_to_ingest(self, collections: OneOrMany[str] | None = None):
        """Create indexes for the provided collections."""

    @abstractmethod
    def ingest_documents(
        self,
        documents: OneOrMany[dict[str, str]],
        collection: str,
    ):
        """Add data to the specified collection in the DB."""


class SourcedQueryEngine(ABC):
    """Wrapper for the LLM model and the retrieval engine."""

    @abstractmethod
    def query(
        self,
        query: str,
        collections: OneOrMany[str],
        similarity_top_k: int = 5,
        llm_settings: LlamaLLMChatSettings | None = None,
    ) -> str:
        """Generate response from relevant text chunks from `collections`."""


class EvaluationComponent:
    """Mock evaluation service."""

    @abstractmethod
    def generate_qa(self, text: str) -> tuple[list[str], list[str]]:
        """Generate QA (questions and answers to them) to the provided text."""

    @abstractmethod
    def predict_answers_with_source(
        self, questions: list[str], **sources
    ) -> list[str]:
        """Answer questions using source (RAG, KG, and similar)."""

    @abstractmethod
    def evaluate_qa(
        self,
        questions: list[str],
        gold_answers: list[str],
        predicted_answers: list[str],
    ) -> list[bool]:
        """Assess the quality of the predicted answers."""
