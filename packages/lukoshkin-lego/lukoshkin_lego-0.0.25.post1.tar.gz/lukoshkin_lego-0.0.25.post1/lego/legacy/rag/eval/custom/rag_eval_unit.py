"""Wrapper for evaluation QA scripts."""

from lego.llm.mock import EvaluationRouter
from lego.rag.eval.custom.base_unit import BaseQAUnit
from lego.rag.mock import SourcedQueryEngine


class QAComponent(BaseQAUnit):
    """Base component for `mocks.EvaluationService` derived classes."""

    def __init__(
        self, router: EvaluationRouter, rag_engine: SourcedQueryEngine
    ):
        super().__init__(router)
        self.rag_engine = rag_engine

    def predict_answers_with_source(self, questions: list[str]) -> list[str]:
        """Answer questions using triplets extracted from the article."""
        return [self.rag_engine.query(q).response for q in questions]
