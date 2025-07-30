"""Synthetic sugar functions for Graph RAG evaluation."""

from kg_llm.kg_types import JSONLike
from kg_llm.llm.prompts import (
    ANSWER_USING_TRIPLETS_PROMPT,
    ANSWER_USING_TRIPLETS_SYSTEM_MESSAGE,
    ANSWER_USING_TRIPLETS_UI_SYSTEM_MESSAGE,
    EVALUATE_QA_PROMPT,
    EVALUATE_QA_SYSTEM_MESSAGE,
    GENERATE_QA_PROMPT,
    GENERATE_QA_SYSTEM_MESSAGE,
)
from kg_llm.llm.utils import llm_tool_arguments, parse_json
from kg_llm.mocks import EvaluationRouter, LLMRouter
from kg_llm.models import TripletModel
from openai.types.chat.chat_completion import ChatCompletion


def llm_tool_call(
    router: LLMRouter,
    messages: list[dict[str, str]],
    tools: JSONLike,
    tool_choice: JSONLike,
) -> ChatCompletion:
    """Make a call to the LLM router and parse response."""
    response = router(messages, tools=tools, tool_choice=tool_choice)
    response = llm_tool_arguments(response)
    return parse_json(response)


def generate_qa(
    router: EvaluationRouter, text: str
) -> tuple[list[str], list[str]]:
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
    response = llm_tool_call(router, messages, tools, tool_choice)
    return response["questions"], response["answers"]


def answer_using_triplets(
    router: EvaluationRouter,
    questions: list[str],
    triplets: list[TripletModel],
    attributes: dict[str, dict[str, str]] | None = None,
    ui_mode: bool = False,
) -> list[str]:
    """Answer questions using triplets extracted from a text."""
    answer_using_triplets_params = {
        "type": "object",
        "properties": {
            "answers": {
                "type": "array",
                "description": (
                    "List of answers obtained with the use of provided"
                    " triplets and given in the order corresponding to"
                    " previously generated questions"
                ),
                "items": {"type": "string"},
            },
        },
        "required": ["answers"],
    }
    tool_choice = {
        "type": "function",
        "function": {"name": "answers_from_triplets"},
    }
    tools = [
        {
            "type": "function",
            "function": {
                "name": "answers_from_triplets",
                "description": (  # fake description (we don't have this fn)
                    "builds a UI form containing answers that were obtained"
                    " using triplets extracted from some text"
                ),
                "parameters": answer_using_triplets_params,
            },
        },
    ]
    triplets = [triplet.to_str() for triplet in triplets]
    attributes_plugin = ""
    if attributes:
        attributes_plugin = "\n\nAnd here are the attributes:\n"
        attributes_plugin += "\n".join(
            [
                f"{entity}: {properties}"
                for entity, properties in attributes.items()
            ]
        )
    messages = [
        {
            "role": "system",
            "content": (
                ANSWER_USING_TRIPLETS_UI_SYSTEM_MESSAGE
                if ui_mode
                else ANSWER_USING_TRIPLETS_SYSTEM_MESSAGE
            ),
        },
        {
            "role": "user",
            "content": ANSWER_USING_TRIPLETS_PROMPT.format(
                questions="\n".join(questions),
                triplets="\n".join(triplets),
                attributes_plugin=attributes_plugin,
            ),
        },
    ]
    response = llm_tool_call(router, messages, tools, tool_choice)
    return response["answers"]


def evaluate_qa(
    router: EvaluationRouter,
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
            for idx, (question, gold_answer, predicted_answer) in enumerate(
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
            "content": EVALUATE_QA_PROMPT.format(qaa_triplets=qaa_triplets),
        },
    ]
    response = llm_tool_call(router, messages, tools, tool_choice)
    return response["results"]
