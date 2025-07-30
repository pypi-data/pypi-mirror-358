"""
QA evaluation service.

Generates QA for an article.
Predicts answers to the questions and compares them to gold ones.
Adds the comparison results for each question to the article
(as well as raw metrics).
"""

import copy
import traceback
from abc import ABC, abstractmethod

from lego.lego_types import JSONDict
from lego.logger import logger
from lego.rag.eval.constants import NO_INFO
from lego.rag.eval.exceptions import (
    QACreationFailed,
    QAEvaluationFailed,
    QALowAccuracyError,
    QAPredictionFailed,
)
from lego.rag.eval.utils import raw_metrics
from lego.rag.mock import EvaluationComponent


class BaseQAEvaluationService(ABC):
    """A service for adding QA and the evaluation results to an article."""

    def __init__(
        self,
        qa_component: EvaluationComponent,
        qa_section: str = "qa",
        min_accuracy_threshold: float = 0.2,
        from_scratch: bool = False,
    ):
        self.qa = qa_component
        self.qa_section = qa_section
        self.min_accuracy = min_accuracy_threshold
        self.from_scratch = from_scratch

    def __call__(  # noqa: WPS238 (too many raises in a function)
        self, article: JSONDict, inplace: bool = False
    ) -> JSONDict:
        """
        Add QA, predict answers, evaluate results, write them to the article.

        Does modifications in-place.
        If not specified otherwise with flag `inplace`.
        """
        if not inplace:
            article = copy.deepcopy(article)

        ## NOTE: Using exc{N} resolves flake8's WPS440
        ## (WPS440: Found block variables overlap)
        ## However, we don't need this.
        try:
            self.add_qa(article)
        except Exception as exc:
            logger.debug(traceback.format_exc())
            raise QACreationFailed from exc

        try:
            self.predict_answers(article)
        except Exception as exc:  # noqa: WPS440
            logger.debug(traceback.format_exc())
            raise QAPredictionFailed from exc

        try:
            accuracy = self.evaluate(article)
        except Exception as exc:  # noqa: WPS440
            logger.debug(traceback.format_exc())
            raise QAEvaluationFailed from exc

        if accuracy < self.min_accuracy:
            raise QALowAccuracyError(
                "QA accuracy is below the threshold:"
                f" {accuracy} < {self.min_accuracy}"
            )
        return article

    def add_qa(self, article: JSONDict):
        """
        Adds 'qa' section.

        with 'questions' and 'gold_answers'.

        Does it in-place.
        """
        if (
            not self.from_scratch
            and "qa" in article
            and "questions" in article["qa"]
            and article["qa"]["questions"]
        ):
            return

        logger.info("Generating QA..")
        questions, gold_answers = self.qa.generate_qa(article["body"])
        article["qa"] = {"questions": questions, "gold_answers": gold_answers}

    @abstractmethod
    def predict_answers(self, article: JSONDict):
        """
        Adds 'predicted_answers' subsection.

        Predict answers to the 'questions' subsection of 'qa' section.
        Add 'predicted_answers' subsection to the experiment's QA section.

        Does it in-place.
        """

    def evaluate(self, article: JSONDict) -> float:
        """
        Adds 'scores' and 'metrics' subsections.

        Add 'scores' and 'metrics' (with raw metrics) subsections
        into the experiment's QA section in-place.

        Does it in-place.
        Returns the accuracy score for the predicted answers.
        """
        scores = self.qa.evaluate_qa(
            article["qa"]["questions"],
            article["qa"]["gold_answers"],
            article[self.qa_section]["predicted_answers"],
        )
        article[self.qa_section]["scores"] = scores
        no_info = article[self.qa_section]["predicted_answers"].count(NO_INFO)

        metrics = raw_metrics(scores)
        metrics["no_info_cnt"] = no_info
        metrics["no_info_share"] = no_info / metrics["length"]

        article[self.qa_section]["metrics"] = metrics
        return metrics["accuracy"]
