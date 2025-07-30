from typing import Literal, Type

from pydantic import BaseModel

from lego.llm.types import ChatCompletion, LegoLLMRouter, Messages
from lego.llm.utils import json_compose as jc
from lego.llm.utils.parse import llm_msg_content, llm_tool_args


class JSONMediator:
    """Mediator for raw JSON input/output."""

    def __init__(
        self,
        router: LegoLLMRouter,
        structured_type: (
            Literal["response_format", "schema_prefill", "tool_calling"] | None
        ) = "response_format",
        **structured_call_kwargs,
    ):
        self.router = router
        self.structured_type = structured_type
        self.kwargs = structured_call_kwargs

    async def __call__(
        self,
        messages: Messages,
        *args,
        response_model: Type[BaseModel] | None = None,
        **kwargs,
    ) -> ChatCompletion:
        """Convert a JSON string to a dictionary."""
        if response_model is None:
            return await self.router(messages, *args, **kwargs)

        if self.structured_type == "tool_calling":
            return await self.router(
                messages,
                *args,
                tools=[jc.model_to_tool(response_model)],
                tool_choice=self.kwargs.get(
                    "tool_choice", jc.forced_tool_choice(response_model)
                ),
                **kwargs,
            )
        if self.structured_type == "response_format":
            opt_field_handling = kwargs.get("optional_field_handling")
            response_format = (
                jc.response_format(
                    response_model,
                    optional_field_handling=opt_field_handling,
                )
                if opt_field_handling
                else jc.response_format(response_model)
            )
            return await self.router(
                messages, *args, response_format=response_format, **kwargs
            )
        if self.structured_type == "schema_prefill":
            messages = jc.schema_prefill(messages, response_model)
            response = await self.router(
                messages,
                *args,
                **kwargs,
            )
            content = llm_msg_content(response)
            prefill = messages[-1]["content"]
            if content.startswith(prefill):
                return response

            response.choices[0].message["content"] = prefill + content
            return response

        raise ValueError(
            "`structured_type` attribute should be set to either"
            " 'response_format', 'schema_prefill', or 'tool_calling'."
        )

    def extract_model(
        self, pymodel: Type[BaseModel], response: ChatCompletion
    ) -> Type[BaseModel]:
        """Extract the model from the response."""
        json_string = (
            llm_tool_args(response)
            if self.structured_type == "tool_calling"
            else llm_msg_content(response)
        )
        return jc.read_model(pymodel, json_string)
