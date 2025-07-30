# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from mpx_genai_sdk import Masterpiecex, AsyncMasterpiecex
from mpx_genai_sdk.types.shared import CreateResponseObject

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAssets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Masterpiecex) -> None:
        asset = client.assets.create(
            description="my description of the asset",
            name="asset1.glb",
            type="model/gltf-binary",
        )
        assert_matches_type(CreateResponseObject, asset, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Masterpiecex) -> None:
        response = client.assets.with_raw_response.create(
            description="my description of the asset",
            name="asset1.glb",
            type="model/gltf-binary",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(CreateResponseObject, asset, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Masterpiecex) -> None:
        with client.assets.with_streaming_response.create(
            description="my description of the asset",
            name="asset1.glb",
            type="model/gltf-binary",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(CreateResponseObject, asset, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAssets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncMasterpiecex) -> None:
        asset = await async_client.assets.create(
            description="my description of the asset",
            name="asset1.glb",
            type="model/gltf-binary",
        )
        assert_matches_type(CreateResponseObject, asset, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.assets.with_raw_response.create(
            description="my description of the asset",
            name="asset1.glb",
            type="model/gltf-binary",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(CreateResponseObject, asset, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.assets.with_streaming_response.create(
            description="my description of the asset",
            name="asset1.glb",
            type="model/gltf-binary",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(CreateResponseObject, asset, path=["response"])

        assert cast(Any, response.is_closed) is True
