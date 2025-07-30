"""
An example of how tool calling can be used with a router:

```python
    router(
        prompt,  # type: list[dict[str, str]]
        tools=[model_to_tool(SomePydanticModel)],
        tool_choice=[forced_tool_choice(SomePydanticModel)],
    )
```
"""

import copy
import json
from typing import Literal, Type, TypedDict

from pydantic import BaseModel, Field, create_model

from lego.lego_types import JSONDict
from lego.llm.types import Messages
from lego.llm.utils.parse import parse_json
from lego.logger import logger


class ResponseFormat(TypedDict):
    """Response format parameter for structured output OpenAI API calls."""

    type: str
    json_schema: JSONDict


def pydantic_model_for_response_format(
    pydantic_model: Type[BaseModel],
    optional_field_handling: Literal[
        "drop", "convert", "keep", "error"
    ] = "keep",
) -> Type[BaseModel]:
    """Prepare `pydantic_model` for use with the response format feature."""
    new_model_dict = {}
    if optional_field_handling not in {"drop", "convert", "keep", "error"}:
        raise ValueError(
            "Invalid value for `optional_field_handling`"
            f": {optional_field_handling}"
        )
    for name, field in pydantic_model.model_fields.items():
        if field.is_required():
            new_model_dict[name] = (field.annotation, field)
            continue

        if optional_field_handling == "drop":
            continue

        if optional_field_handling == "keep":
            new_model_dict[name] = (field.annotation, field)
            continue

        if optional_field_handling == "error":
            raise ValueError(
                f"Field '{name}' is optional, and thus, is not suitable"
                " for the use with the response format feature."
            )
        new_model_dict[name] = (
            field.annotation,
            Field(..., title=field.title, description=field.description),
        )
    return create_model(pydantic_model.__name__, **new_model_dict)


def _additional_properties_false(schema: JSONDict) -> None:
    """Add 'additionalProperties=False' in-place and at every level."""
    if schema.get("type") == "object":
        schema["additionalProperties"] = False

    if "properties" in schema:
        for _, prop_schema in schema["properties"].items():
            _additional_properties_false(prop_schema)

    if schema.get("type") == "array" and "items" in schema:
        _additional_properties_false(schema["items"])


def additional_properties_false(schema: JSONDict) -> JSONDict:
    """Recursively add to the schema 'additionalProperties': False."""
    schema = copy.deepcopy(schema)
    _additional_properties_false(schema)
    return schema


def response_format(
    pymodel: Type[BaseModel],
    strict: bool = True,
    optional_field_handling: Literal[
        "drop", "convert", "keep", "error"
    ] = "error",
) -> ResponseFormat:
    """Create OpenAI-like response_format parameter from a Pydantic model."""
    pymodel = pydantic_model_for_response_format(
        pymodel, optional_field_handling
    )
    json_schema = pymodel.model_json_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            "name": pymodel.__name__,
            "strict": strict,
            "schema": (
                additional_properties_false(json_schema)
                if strict
                else json_schema
            ),
        },
    }


def read_model(model: Type[BaseModel], model_json: str) -> BaseModel:
    """Create a pydantic model from a JSON string."""
    return model.model_validate(parse_json(model_json))


def model_to_tool(model: BaseModel) -> JSONDict:
    """Convert a Pydantic model to a tool."""
    json_schema = model.model_json_schema()
    desc = json_schema.pop("description", None)
    if desc is None:
        raise ValueError(f"Please add a docstring for {model.__name__}")

    return {
        "type": "function",
        "function": {
            "name": model.__class__.__name__,
            "description": desc,
            "parameters": json_schema,
        },
    }


def forced_tool_choice(tool: JSONDict | BaseModel) -> JSONDict:
    """Convert a tool or Pydantic model to a tool choice."""
    ## OR with `issubclass` to take into account models created with `create_model`
    if isinstance(tool, BaseModel) or issubclass(tool, BaseModel):
        return {
            "type": "function",
            "function": {"name": tool.__class__.__name__},
        }
    return {
        "type": "function",
        "function": {"name": tool["function"]["name"]},
    }


def schema_prefill(messages: Messages, pymodel: Type[BaseModel]) -> Messages:
    """Prefill a JSON schema with default values."""
    messages = copy.deepcopy(messages)
    if not messages or not isinstance(messages[-1], dict):
        raise ValueError("The `messages` structure is invalid.")

    if messages[-1]["role"] == "assistant":
        raise ValueError(
            "The last message should come from the user, not the LLM"
        )
    if messages[-1]["role"] in {"system", "developer"}:
        logger.warning(
            "The role of the last message is not 'user'\n"
            f"It is '{messages[-1]["role"]}'"
        )
    content = (
        "\n\nNOTE: Your response should follow the schema:\n"
        + json.dumps(pymodel.model_json_schema())
    )
    if isinstance(messages[-1]["content"], str):
        messages[-1]["content"] = messages[-1]["content"].rstrip() + content
    elif isinstance(messages[-1]["content"], list):
        messages[-1]["content"].append({"type": "text", "text": content})
    else:
        raise ValueError(
            "The last message content should be a string or a list of dicts"
        )
    field = next(iter(pymodel.model_fields))
    messages.append({"role": "assistant", "content": f'{{"{field}":'})
    return messages
