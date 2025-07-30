# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["LlmCallParams", "DataParms"]


class LlmCallParams(TypedDict, total=False):
    system_prompt: Required[Annotated[str, PropertyInfo(alias="systemPrompt")]]
    """The system prompt to use for the LLM call"""

    user_prompt: Required[Annotated[str, PropertyInfo(alias="userPrompt")]]
    """The user prompt to use for the LLM call"""

    data_parms: Annotated[DataParms, PropertyInfo(alias="dataParms")]
    """The data parameters to use for the LLM call.

    These parameters are optional and will default to the values in the dataParms
    object.
    """


class DataParms(TypedDict, total=False):
    max_tokens: Annotated[float, PropertyInfo(alias="maxTokens")]
    """The max tokens to use for the LLM call."""

    temperature: float
    """The temperature to use for the LLM call. A value between 0 and 2."""
