# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from ..types import llm_call_params, llm_image_query_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.shared.generate_response_object import GenerateResponseObject

__all__ = ["LlmsResource", "AsyncLlmsResource"]


class LlmsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LlmsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return LlmsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LlmsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return LlmsResourceWithStreamingResponse(self)

    def call(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        data_parms: llm_call_params.DataParms | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """
        This function allows you to call an LLM with a user and system prompt as well as
        a set of data parameters. Save the requestId from the response and use the
        status endpoint to check the status of the request and retrieve the output.

        Args:
          system_prompt: The system prompt to use for the LLM call

          user_prompt: The user prompt to use for the LLM call

          data_parms: The data parameters to use for the LLM call. These parameters are optional and
              will default to the values in the dataParms object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/llm/llm_call",
            body=maybe_transform(
                {
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "data_parms": data_parms,
                },
                llm_call_params.LlmCallParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )

    def image_query(
        self,
        *,
        image_urls: List[str],
        user_prompt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """
        This function allows you to query an image or a set of images with a prompt.
        Save the requestId from the response and use the status endpoint to check the
        status of the request and retrieve the output. The imageUrls is an array of one
        or more public URLs of the images to query. You can use the assets/create
        endpoint to upload your images. To get the public URL of the uploaded image,
        simply remove the parameters. eg. everything after and including the ? in the
        returned assetUrl from the assets/create response. Make sure you have uploaded
        the image to our servers before querying.

        Args:
          image_urls: The list of publicURLs of the images to query. Should be an array of strings.

          user_prompt: The user prompt to use for the LLM call

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/llm/image_query",
            body=maybe_transform(
                {
                    "image_urls": image_urls,
                    "user_prompt": user_prompt,
                },
                llm_image_query_params.LlmImageQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )


class AsyncLlmsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLlmsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLlmsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLlmsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return AsyncLlmsResourceWithStreamingResponse(self)

    async def call(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        data_parms: llm_call_params.DataParms | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """
        This function allows you to call an LLM with a user and system prompt as well as
        a set of data parameters. Save the requestId from the response and use the
        status endpoint to check the status of the request and retrieve the output.

        Args:
          system_prompt: The system prompt to use for the LLM call

          user_prompt: The user prompt to use for the LLM call

          data_parms: The data parameters to use for the LLM call. These parameters are optional and
              will default to the values in the dataParms object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/llm/llm_call",
            body=await async_maybe_transform(
                {
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "data_parms": data_parms,
                },
                llm_call_params.LlmCallParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )

    async def image_query(
        self,
        *,
        image_urls: List[str],
        user_prompt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """
        This function allows you to query an image or a set of images with a prompt.
        Save the requestId from the response and use the status endpoint to check the
        status of the request and retrieve the output. The imageUrls is an array of one
        or more public URLs of the images to query. You can use the assets/create
        endpoint to upload your images. To get the public URL of the uploaded image,
        simply remove the parameters. eg. everything after and including the ? in the
        returned assetUrl from the assets/create response. Make sure you have uploaded
        the image to our servers before querying.

        Args:
          image_urls: The list of publicURLs of the images to query. Should be an array of strings.

          user_prompt: The user prompt to use for the LLM call

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/llm/image_query",
            body=await async_maybe_transform(
                {
                    "image_urls": image_urls,
                    "user_prompt": user_prompt,
                },
                llm_image_query_params.LlmImageQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )


class LlmsResourceWithRawResponse:
    def __init__(self, llms: LlmsResource) -> None:
        self._llms = llms

        self.call = to_raw_response_wrapper(
            llms.call,
        )
        self.image_query = to_raw_response_wrapper(
            llms.image_query,
        )


class AsyncLlmsResourceWithRawResponse:
    def __init__(self, llms: AsyncLlmsResource) -> None:
        self._llms = llms

        self.call = async_to_raw_response_wrapper(
            llms.call,
        )
        self.image_query = async_to_raw_response_wrapper(
            llms.image_query,
        )


class LlmsResourceWithStreamingResponse:
    def __init__(self, llms: LlmsResource) -> None:
        self._llms = llms

        self.call = to_streamed_response_wrapper(
            llms.call,
        )
        self.image_query = to_streamed_response_wrapper(
            llms.image_query,
        )


class AsyncLlmsResourceWithStreamingResponse:
    def __init__(self, llms: AsyncLlmsResource) -> None:
        self._llms = llms

        self.call = async_to_streamed_response_wrapper(
            llms.call,
        )
        self.image_query = async_to_streamed_response_wrapper(
            llms.image_query,
        )
