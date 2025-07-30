import json
from typing import Type

import pytest
from pydantic import BaseModel, Field, ValidationError, create_model

from lego.litellm.utils.utils import (
    build_bedrock_model,
    build_litellm_router,
    build_openai_model,
)
from lego.llm.utils import json_compose
from lego.llm.utils.json_mediator import JSONMediator
from lego.llm.utils.parse import llm_stream_content

TEST_PROMPTS = {
    "complex_question": [
        {
            "role": "user",
            "content": (
                "Where is the beginning of the end which ends with the beginning?"
            ),
        }
    ],
    "nlq_to_sql_prompt": [
        {
            "role": "user",
            "content": "generate a example of NLQ-to-SQL conversion",
        }
    ],
}
SQL_PAIR_EXAMPLE_DICT = {
    "nlq": (str, "A natural language query to convert."),
    "sql": (str, "The corresponding SQL query."),
    "details": (str, "Some additional details about the query use cases"),
}


def create_model_from_dict(
    name: str,
    model_dict: dict[str, tuple[type, str]],
    model_docstring: str | None = None,
) -> Type[BaseModel]:
    return create_model(
        name,
        **{
            field: (field_type, Field(..., description=description))
            for field, (field_type, description) in model_dict.items()
        },
        __doc__=model_docstring,
    )


@pytest.fixture
def router_openai_gpt4o():
    return build_litellm_router(
        [build_openai_model("gpt-4o")],
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def router_openai_o1():
    return build_litellm_router(
        [build_openai_model("o1")],
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def router_openai_o1mini():
    return build_litellm_router(
        [build_openai_model("o1-mini")],
        num_retries=1,
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def router_haiku3():
    return build_litellm_router(
        [
            build_bedrock_model(
                "anthropic.claude-3-haiku-20240307-v1:0",
                model_settings={"temperature": 0.2},
                proxy_settings={"num_retries": 2},
            )
        ],
        num_retries=1,
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def router_haiku35():
    return build_litellm_router(
        [build_bedrock_model("us.anthropic.claude-3-5-haiku-20241022-v1:0")],
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def router_sonnet37():
    return build_litellm_router(
        [
            build_bedrock_model(
                "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                model_settings={
                    "temperature": 1,
                    "thinking": {
                        "type": "enabled",
                        "budget_tokens": 1024,
                    },
                },
                proxy_settings={"num_retries": 2},
            )
        ],
        num_retries=1,
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def nlq_sql_pymodel():
    return create_model_from_dict(
        "SQLPairExample",
        SQL_PAIR_EXAMPLE_DICT,
        "Generate an example of NLQ-to-SQL conversion.",
    )


@pytest.mark.asyncio
async def test_routers_call_method(
    router_haiku3, router_sonnet37, router_openai_o1mini
):
    """Test __call__ methods of Anthropic and OpenAI models."""
    complex_question = TEST_PROMPTS["complex_question"]
    await router_openai_o1mini(complex_question)
    await router_haiku3(complex_question, temperature=0)
    stream_response = await router_sonnet37(complex_question, stream=True)
    answer, reasoning = await llm_stream_content(stream_response)
    assert answer, "Empty response from the model"
    assert reasoning, "No reasoning prompt found"


def test_schema_prefill(nlq_sql_pymodel):
    """Test assistant prefill with `json_compose.schema_prefill` method."""
    messages = TEST_PROMPTS["nlq_to_sql_prompt"]
    messages = json_compose.schema_prefill(messages, nlq_sql_pymodel)
    assert messages[-2]["content"].endswith(
        json.dumps(nlq_sql_pymodel.model_json_schema())
    )
    assert messages[-1]["role"] == "assistant"
    first_key = next(iter(SQL_PAIR_EXAMPLE_DICT))
    assert messages[-1]["content"] == f'{{"{first_key}":'


@pytest.mark.asyncio
async def test_json_mediator(
    router_haiku3, router_haiku35, router_openai_gpt4o, nlq_sql_pymodel
):
    messages = TEST_PROMPTS["nlq_to_sql_prompt"]

    for method, router, kwargs in zip(
        ("response_format", "tool_calling", "schema_prefill"),
        (router_openai_gpt4o, router_haiku35, router_haiku3),
        ({"optional_field_handling": "convert"}, {"tool_choice": "auto"}, {}),
    ):
        router = JSONMediator(router, structured_type=method, **kwargs)
        response = await router(messages, response_model=nlq_sql_pymodel)
        try:
            router.extract_model(nlq_sql_pymodel, response)
        except ValidationError:
            assert False, f"Response validation failed for '{method}'"


@pytest.mark.asyncio
async def test_json_mediator_with_reasoning_models(
    router_sonnet37, router_openai_o1, nlq_sql_pymodel
):
    messages = TEST_PROMPTS["nlq_to_sql_prompt"]

    for name, router in zip(
        ("sonnet3.7", "o1-mini"), (router_sonnet37, router_openai_o1)
    ):
        router = JSONMediator(
            router,
            structured_type="tool_calling",
            tool_choice="auto",
        )
        response = await router(messages, response_model=nlq_sql_pymodel)
        try:
            router.extract_model(nlq_sql_pymodel, response)
        except ValidationError:
            assert False, f"Response validation failed for '{name}'"
