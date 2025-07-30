"""Base class for the evaluation unit for evaluation services."""

from abc import ABC, abstractmethod

from openai.types.chat.chat_completion import ChatCompletion

from lego.lego_types import JSONDict
from lego.llm.mock import EvaluationRouter
from lego.llm.utils.parse import llm_tool_args, parse_json
from lego.rag.eval.prompt import (
    EVALUATE_QA_PROMPT,
    EVALUATE_QA_SYSTEM_MESSAGE,
    GENERATE_QA_PROMPT,
    GENERATE_QA_SYSTEM_MESSAGE,
)


class BaseQAUnit(ABC):
    """Evaluation unit for `mock.EvaluationService` derived classes."""

    def __init__(self, router: EvaluationRouter):
        self.router = router

    def llm_tool_call(
        self,
        messages: list[dict[str, str]],
        tools: JSONDict,
        tool_choice: JSONDict,
    ) -> ChatCompletion:
        """Make a call to the LLM router and parse response."""
        response = self.router(messages, tools=tools, tool_choice=tool_choice)
        response = llm_tool_args(response)
        return parse_json(response)

    def generate_qa(self, text: str) -> tuple[list[str], list[str]]:
        """Generate QA to the provided text."""
        generate_qa_params = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "description": (
                        "List of generated questions based on the provided text"
                    ),
                    "items": {"type": "string"},
                },
                "answers": {
                    "type": "array",
                    "description": (
                        "List of answers given in the order corresponding"
                        " to the generated questions"
                    ),
                    "items": {"type": "string"},
                },
            },
            "required": ["questions", "answers"],
        }
        tool_choice = {
            "type": "function",
            "function": {"name": "generate_qa"},
        }
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_qa",
                    "description": (  # fake description (we don't have this fn)
                        "Builds a quiz using questions and answers"
                        " retrieved from the provided text"
                    ),
                    "parameters": generate_qa_params,
                },
            },
        ]
        messages = [
            {
                "role": "system",
                "content": GENERATE_QA_SYSTEM_MESSAGE,
            },
            {
                "role": "user",
                "content": GENERATE_QA_PROMPT.format(text=text),
            },
        ]
        response = self.llm_tool_call(messages, tools, tool_choice)
        return response["questions"], response["answers"]

    @abstractmethod
    def predict_answers_with_source(
        self, questions: list[str], **sources
    ) -> list[str]:
        """Answer questions using the provided sources."""

    def evaluate_qa(
        self,
        questions: list[str],
        gold_answers: list[str],
        answers_from_kg: list[str],
    ) -> list[bool]:
        """Evaluate the quality of the answers predicted from triplets."""
        evaluate_qa_params = {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "description": (
                        "List of integers (range between 0 and 100) representing"
                        " the comparison results between gold answers and"
                        " predicted ones."
                    ),
                    "items": {"type": "integer"},
                }
            },
            "required": ["results"],
        }
        tool_choice = {
            "type": "function",
            "function": {"name": "evaluate_qa"},
        }
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "evaluate_qa",
                    "description": (  # fake description (we don't have this fn)
                        "Calculates the accuracy given the array of integers"
                    ),
                    "parameters": evaluate_qa_params,
                },
            },
        ]
        qaa_triplets = "\n".join(
            [
                f"{idx}."
                f"\n\tQuestion: {question}"  # Can be easily commented out
                f"\n\tGold answer: {gold_answer}"
                f"\n\tPredicted answer: {predicted_answer}"
                for idx, (
                    question,
                    gold_answer,
                    predicted_answer,
                ) in enumerate(
                    zip(questions, gold_answers, answers_from_kg), 1
                )
            ]
        )
        messages = [
            {
                "role": "system",
                "content": EVALUATE_QA_SYSTEM_MESSAGE,
            },
            {
                "role": "user",
                "content": EVALUATE_QA_PROMPT.format(
                    qaa_triplets=qaa_triplets
                ),
            },
        ]
        response = self.llm_tool_call(messages, tools, tool_choice)
        return response["results"]
