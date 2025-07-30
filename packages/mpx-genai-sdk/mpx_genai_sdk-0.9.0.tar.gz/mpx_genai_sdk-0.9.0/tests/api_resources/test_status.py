# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from mpx_genai_sdk import Masterpiecex, AsyncMasterpiecex
from mpx_genai_sdk.types import StatusResponseObject

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStatus:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Masterpiecex) -> None:
        status = client.status.retrieve(
            "requestId",
        )
        assert_matches_type(StatusResponseObject, status, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Masterpiecex) -> None:
        response = client.status.with_raw_response.retrieve(
            "requestId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        status = response.parse()
        assert_matches_type(StatusResponseObject, status, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Masterpiecex) -> None:
        with client.status.with_streaming_response.retrieve(
            "requestId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            status = response.parse()
            assert_matches_type(StatusResponseObject, status, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Masterpiecex) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `request_id` but received ''"):
            client.status.with_raw_response.retrieve(
                "",
            )


class TestAsyncStatus:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMasterpiecex) -> None:
        status = await async_client.status.retrieve(
            "requestId",
        )
        assert_matches_type(StatusResponseObject, status, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.status.with_raw_response.retrieve(
            "requestId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        status = await response.parse()
        assert_matches_type(StatusResponseObject, status, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.status.with_streaming_response.retrieve(
            "requestId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            status = await response.parse()
            assert_matches_type(StatusResponseObject, status, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMasterpiecex) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `request_id` but received ''"):
            await async_client.status.with_raw_response.retrieve(
                "",
            )
