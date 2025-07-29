# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.user import apikey_create_params, apikey_update_params
from ..._base_client import make_request_options
from ...types.user.apikey_create_response import ApikeyCreateResponse
from ...types.user.apikey_delete_response import ApikeyDeleteResponse
from ...types.user.apikey_update_response import ApikeyUpdateResponse

__all__ = ["ApikeyResource", "AsyncApikeyResource"]


class ApikeyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ApikeyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return ApikeyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApikeyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return ApikeyResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        access_level: Literal[0, 1],
        document_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        project_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        table_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApikeyCreateResponse:
        """
        Create an API key for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/user/apikey",
            body=maybe_transform(
                {
                    "access_level": access_level,
                    "document_restrictions": document_restrictions,
                    "name": name,
                    "project_restrictions": project_restrictions,
                    "table_restrictions": table_restrictions,
                },
                apikey_create_params.ApikeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApikeyCreateResponse,
        )

    def update(
        self,
        api_key_id: str,
        *,
        access_level: Literal[0, 1],
        document_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        project_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        table_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApikeyUpdateResponse:
        """
        Update an API key for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return self._put(
            f"/v1/user/apikey/{api_key_id}",
            body=maybe_transform(
                {
                    "access_level": access_level,
                    "document_restrictions": document_restrictions,
                    "name": name,
                    "project_restrictions": project_restrictions,
                    "table_restrictions": table_restrictions,
                },
                apikey_update_params.ApikeyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApikeyUpdateResponse,
        )

    def delete(
        self,
        api_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApikeyDeleteResponse:
        """
        Delete an API key for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return self._delete(
            f"/v1/user/apikey/{api_key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApikeyDeleteResponse,
        )


class AsyncApikeyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncApikeyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncApikeyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApikeyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncApikeyResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        access_level: Literal[0, 1],
        document_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        project_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        table_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApikeyCreateResponse:
        """
        Create an API key for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/user/apikey",
            body=await async_maybe_transform(
                {
                    "access_level": access_level,
                    "document_restrictions": document_restrictions,
                    "name": name,
                    "project_restrictions": project_restrictions,
                    "table_restrictions": table_restrictions,
                },
                apikey_create_params.ApikeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApikeyCreateResponse,
        )

    async def update(
        self,
        api_key_id: str,
        *,
        access_level: Literal[0, 1],
        document_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        project_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        table_restrictions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApikeyUpdateResponse:
        """
        Update an API key for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return await self._put(
            f"/v1/user/apikey/{api_key_id}",
            body=await async_maybe_transform(
                {
                    "access_level": access_level,
                    "document_restrictions": document_restrictions,
                    "name": name,
                    "project_restrictions": project_restrictions,
                    "table_restrictions": table_restrictions,
                },
                apikey_update_params.ApikeyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApikeyUpdateResponse,
        )

    async def delete(
        self,
        api_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApikeyDeleteResponse:
        """
        Delete an API key for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return await self._delete(
            f"/v1/user/apikey/{api_key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApikeyDeleteResponse,
        )


class ApikeyResourceWithRawResponse:
    def __init__(self, apikey: ApikeyResource) -> None:
        self._apikey = apikey

        self.create = to_raw_response_wrapper(
            apikey.create,
        )
        self.update = to_raw_response_wrapper(
            apikey.update,
        )
        self.delete = to_raw_response_wrapper(
            apikey.delete,
        )


class AsyncApikeyResourceWithRawResponse:
    def __init__(self, apikey: AsyncApikeyResource) -> None:
        self._apikey = apikey

        self.create = async_to_raw_response_wrapper(
            apikey.create,
        )
        self.update = async_to_raw_response_wrapper(
            apikey.update,
        )
        self.delete = async_to_raw_response_wrapper(
            apikey.delete,
        )


class ApikeyResourceWithStreamingResponse:
    def __init__(self, apikey: ApikeyResource) -> None:
        self._apikey = apikey

        self.create = to_streamed_response_wrapper(
            apikey.create,
        )
        self.update = to_streamed_response_wrapper(
            apikey.update,
        )
        self.delete = to_streamed_response_wrapper(
            apikey.delete,
        )


class AsyncApikeyResourceWithStreamingResponse:
    def __init__(self, apikey: AsyncApikeyResource) -> None:
        self._apikey = apikey

        self.create = async_to_streamed_response_wrapper(
            apikey.create,
        )
        self.update = async_to_streamed_response_wrapper(
            apikey.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            apikey.delete,
        )
