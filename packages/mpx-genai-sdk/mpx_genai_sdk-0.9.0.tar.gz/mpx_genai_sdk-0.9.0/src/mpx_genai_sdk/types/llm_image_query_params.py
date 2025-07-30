# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["LlmImageQueryParams"]


class LlmImageQueryParams(TypedDict, total=False):
    image_urls: Required[Annotated[List[str], PropertyInfo(alias="imageUrls")]]
    """The list of publicURLs of the images to query. Should be an array of strings."""

    user_prompt: Required[Annotated[str, PropertyInfo(alias="userPrompt")]]
    """The user prompt to use for the LLM call"""
