# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from mpx_genai_sdk import Masterpiecex, AsyncMasterpiecex
from mpx_genai_sdk.types.shared import GenerateResponseObject

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFunctions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_general(self, client: Masterpiecex) -> None:
        function = client.functions.create_general(
            prompt="cute dog",
        )
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    def test_raw_response_create_general(self, client: Masterpiecex) -> None:
        response = client.functions.with_raw_response.create_general(
            prompt="cute dog",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function = response.parse()
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    def test_streaming_response_create_general(self, client: Masterpiecex) -> None:
        with client.functions.with_streaming_response.create_general(
            prompt="cute dog",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function = response.parse()
            assert_matches_type(GenerateResponseObject, function, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_imageto3d(self, client: Masterpiecex) -> None:
        function = client.functions.imageto3d()
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    def test_method_imageto3d_with_all_params(self, client: Masterpiecex) -> None:
        function = client.functions.imageto3d(
            image_request_id="<requestId from /assets/create>",
            image_url="https://.../image.png",
            seed=0,
            texture_size=0,
        )
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    def test_raw_response_imageto3d(self, client: Masterpiecex) -> None:
        response = client.functions.with_raw_response.imageto3d()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function = response.parse()
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    def test_streaming_response_imageto3d(self, client: Masterpiecex) -> None:
        with client.functions.with_streaming_response.imageto3d() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function = response.parse()
            assert_matches_type(GenerateResponseObject, function, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFunctions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_general(self, async_client: AsyncMasterpiecex) -> None:
        function = await async_client.functions.create_general(
            prompt="cute dog",
        )
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    async def test_raw_response_create_general(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.functions.with_raw_response.create_general(
            prompt="cute dog",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function = await response.parse()
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    async def test_streaming_response_create_general(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.functions.with_streaming_response.create_general(
            prompt="cute dog",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function = await response.parse()
            assert_matches_type(GenerateResponseObject, function, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_imageto3d(self, async_client: AsyncMasterpiecex) -> None:
        function = await async_client.functions.imageto3d()
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    async def test_method_imageto3d_with_all_params(self, async_client: AsyncMasterpiecex) -> None:
        function = await async_client.functions.imageto3d(
            image_request_id="<requestId from /assets/create>",
            image_url="https://.../image.png",
            seed=0,
            texture_size=0,
        )
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    async def test_raw_response_imageto3d(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.functions.with_raw_response.imageto3d()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function = await response.parse()
        assert_matches_type(GenerateResponseObject, function, path=["response"])

    @parametrize
    async def test_streaming_response_imageto3d(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.functions.with_streaming_response.imageto3d() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function = await response.parse()
            assert_matches_type(GenerateResponseObject, function, path=["response"])

        assert cast(Any, response.is_closed) is True
