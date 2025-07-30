# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from mpx_genai_sdk import Masterpiecex, AsyncMasterpiecex
from mpx_genai_sdk.types.shared import CreateResponseObject, GenerateResponseObject

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestComponents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_optimize(self, client: Masterpiecex) -> None:
        component = client.components.optimize(
            asset_request_id="xxxxxxx",
            object_type="humanoid",
            output_file_format="FBX",
            target_ratio=0.5,
        )
        assert_matches_type(CreateResponseObject, component, path=["response"])

    @parametrize
    def test_raw_response_optimize(self, client: Masterpiecex) -> None:
        response = client.components.with_raw_response.optimize(
            asset_request_id="xxxxxxx",
            object_type="humanoid",
            output_file_format="FBX",
            target_ratio=0.5,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(CreateResponseObject, component, path=["response"])

    @parametrize
    def test_streaming_response_optimize(self, client: Masterpiecex) -> None:
        with client.components.with_streaming_response.optimize(
            asset_request_id="xxxxxxx",
            object_type="humanoid",
            output_file_format="FBX",
            target_ratio=0.5,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(CreateResponseObject, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_text2image(self, client: Masterpiecex) -> None:
        component = client.components.text2image(
            prompt="prompt",
        )
        assert_matches_type(GenerateResponseObject, component, path=["response"])

    @parametrize
    def test_method_text2image_with_all_params(self, client: Masterpiecex) -> None:
        component = client.components.text2image(
            prompt="prompt",
            aspect_ratio="aspectRatio",
            lora_id="loraId",
            lora_scale=0,
            lora_weights="loraWeights",
            megapixels=0,
            num_images=0,
            num_steps=0,
            output_format="outputFormat",
            seed=0,
        )
        assert_matches_type(GenerateResponseObject, component, path=["response"])

    @parametrize
    def test_raw_response_text2image(self, client: Masterpiecex) -> None:
        response = client.components.with_raw_response.text2image(
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(GenerateResponseObject, component, path=["response"])

    @parametrize
    def test_streaming_response_text2image(self, client: Masterpiecex) -> None:
        with client.components.with_streaming_response.text2image(
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(GenerateResponseObject, component, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncComponents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_optimize(self, async_client: AsyncMasterpiecex) -> None:
        component = await async_client.components.optimize(
            asset_request_id="xxxxxxx",
            object_type="humanoid",
            output_file_format="FBX",
            target_ratio=0.5,
        )
        assert_matches_type(CreateResponseObject, component, path=["response"])

    @parametrize
    async def test_raw_response_optimize(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.components.with_raw_response.optimize(
            asset_request_id="xxxxxxx",
            object_type="humanoid",
            output_file_format="FBX",
            target_ratio=0.5,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(CreateResponseObject, component, path=["response"])

    @parametrize
    async def test_streaming_response_optimize(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.components.with_streaming_response.optimize(
            asset_request_id="xxxxxxx",
            object_type="humanoid",
            output_file_format="FBX",
            target_ratio=0.5,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(CreateResponseObject, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_text2image(self, async_client: AsyncMasterpiecex) -> None:
        component = await async_client.components.text2image(
            prompt="prompt",
        )
        assert_matches_type(GenerateResponseObject, component, path=["response"])

    @parametrize
    async def test_method_text2image_with_all_params(self, async_client: AsyncMasterpiecex) -> None:
        component = await async_client.components.text2image(
            prompt="prompt",
            aspect_ratio="aspectRatio",
            lora_id="loraId",
            lora_scale=0,
            lora_weights="loraWeights",
            megapixels=0,
            num_images=0,
            num_steps=0,
            output_format="outputFormat",
            seed=0,
        )
        assert_matches_type(GenerateResponseObject, component, path=["response"])

    @parametrize
    async def test_raw_response_text2image(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.components.with_raw_response.text2image(
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(GenerateResponseObject, component, path=["response"])

    @parametrize
    async def test_streaming_response_text2image(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.components.with_streaming_response.text2image(
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(GenerateResponseObject, component, path=["response"])

        assert cast(Any, response.is_closed) is True
