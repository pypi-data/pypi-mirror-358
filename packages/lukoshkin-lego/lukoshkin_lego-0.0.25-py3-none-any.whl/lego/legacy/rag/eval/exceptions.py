"""Exceptions related to the RAG pipeline evaluation."""


class QACreationFailed(Exception):
    """Failed to create QA for an article."""


class QAPredictionFailed(Exception):
    """Failed to predict answers from extracted ontology."""


class QAEvaluationFailed(Exception):
    """Failed to assess predicted answers with an LLM."""


class QALowAccuracyError(Exception):
    """Predicted answers are of low accuracy."""
