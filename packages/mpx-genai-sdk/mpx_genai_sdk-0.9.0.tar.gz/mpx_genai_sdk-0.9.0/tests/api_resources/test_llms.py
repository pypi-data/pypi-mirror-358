# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from mpx_genai_sdk import Masterpiecex, AsyncMasterpiecex
from mpx_genai_sdk.types.shared import GenerateResponseObject

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLlms:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_call(self, client: Masterpiecex) -> None:
        llm = client.llms.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
        )
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    def test_method_call_with_all_params(self, client: Masterpiecex) -> None:
        llm = client.llms.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
            data_parms={
                "max_tokens": 0,
                "temperature": 0,
            },
        )
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    def test_raw_response_call(self, client: Masterpiecex) -> None:
        response = client.llms.with_raw_response.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm = response.parse()
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    def test_streaming_response_call(self, client: Masterpiecex) -> None:
        with client.llms.with_streaming_response.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm = response.parse()
            assert_matches_type(GenerateResponseObject, llm, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_image_query(self, client: Masterpiecex) -> None:
        llm = client.llms.image_query(
            image_urls=["string"],
            user_prompt="userPrompt",
        )
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    def test_raw_response_image_query(self, client: Masterpiecex) -> None:
        response = client.llms.with_raw_response.image_query(
            image_urls=["string"],
            user_prompt="userPrompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm = response.parse()
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    def test_streaming_response_image_query(self, client: Masterpiecex) -> None:
        with client.llms.with_streaming_response.image_query(
            image_urls=["string"],
            user_prompt="userPrompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm = response.parse()
            assert_matches_type(GenerateResponseObject, llm, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLlms:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_call(self, async_client: AsyncMasterpiecex) -> None:
        llm = await async_client.llms.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
        )
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    async def test_method_call_with_all_params(self, async_client: AsyncMasterpiecex) -> None:
        llm = await async_client.llms.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
            data_parms={
                "max_tokens": 0,
                "temperature": 0,
            },
        )
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    async def test_raw_response_call(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.llms.with_raw_response.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm = await response.parse()
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    async def test_streaming_response_call(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.llms.with_streaming_response.call(
            system_prompt="systemPrompt",
            user_prompt="userPrompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm = await response.parse()
            assert_matches_type(GenerateResponseObject, llm, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_image_query(self, async_client: AsyncMasterpiecex) -> None:
        llm = await async_client.llms.image_query(
            image_urls=["string"],
            user_prompt="userPrompt",
        )
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    async def test_raw_response_image_query(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.llms.with_raw_response.image_query(
            image_urls=["string"],
            user_prompt="userPrompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        llm = await response.parse()
        assert_matches_type(GenerateResponseObject, llm, path=["response"])

    @parametrize
    async def test_streaming_response_image_query(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.llms.with_streaming_response.image_query(
            image_urls=["string"],
            user_prompt="userPrompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            llm = await response.parse()
            assert_matches_type(GenerateResponseObject, llm, path=["response"])

        assert cast(Any, response.is_closed) is True
