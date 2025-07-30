"""Adaptation of the `BaseQAEvaluationService` to the RAG pipeline."""

from lego.lego_types import JSONDict
from lego.rag.eval.custom.base_service import BaseQAEvaluationService


class QAEvaluationService(BaseQAEvaluationService):
    """RAG evaluation service."""

    def predict_answers(self, article: JSONDict):
        """
        Adds 'predicted_answers' subsection.

        Predict answers to the 'questions' subsection of 'qa' section.
        Add 'predicted_answers' subsection to the experiment's QA section.

        Does it in-place.
        """
        questions = article["qa"]["questions"]
        article[self.qa_section] = article.get(self.qa_section, {})
        qa_section = article[self.qa_section]

        predicted_answers = self.qa.predict_answers_with_source(questions)
        qa_section["predicted_answers"] = predicted_answers
