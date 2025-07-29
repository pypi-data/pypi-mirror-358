# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.document import duplicate_global_params, duplicate_duplicate_params
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.document.duplicate_global_response import DuplicateGlobalResponse

__all__ = ["DuplicateResource", "AsyncDuplicateResource"]


class DuplicateResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DuplicateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return DuplicateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DuplicateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return DuplicateResourceWithStreamingResponse(self)

    def duplicate(
        self,
        document_id: str,
        *,
        target_project_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        duplicate_linked_tables: Optional[bool] | NotGiven = NOT_GIVEN,
        duplicate_permissions: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Duplicate an existing document, potentially in a different hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/document/{document_id}/duplicate",
            body=maybe_transform(
                {
                    "target_project_id": target_project_id,
                    "context": context,
                    "duplicate_linked_tables": duplicate_linked_tables,
                    "duplicate_permissions": duplicate_permissions,
                },
                duplicate_duplicate_params.DuplicateDuplicateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def global_(
        self,
        *,
        process_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        project_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DuplicateGlobalResponse:
        """
        Duplicate an existing document, optionally into a different hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/document/duplicate",
            body=maybe_transform(
                {
                    "process_id": process_id,
                    "context": context,
                    "project_id": project_id,
                },
                duplicate_global_params.DuplicateGlobalParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DuplicateGlobalResponse,
        )


class AsyncDuplicateResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDuplicateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDuplicateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDuplicateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncDuplicateResourceWithStreamingResponse(self)

    async def duplicate(
        self,
        document_id: str,
        *,
        target_project_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        duplicate_linked_tables: Optional[bool] | NotGiven = NOT_GIVEN,
        duplicate_permissions: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Duplicate an existing document, potentially in a different hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/document/{document_id}/duplicate",
            body=await async_maybe_transform(
                {
                    "target_project_id": target_project_id,
                    "context": context,
                    "duplicate_linked_tables": duplicate_linked_tables,
                    "duplicate_permissions": duplicate_permissions,
                },
                duplicate_duplicate_params.DuplicateDuplicateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def global_(
        self,
        *,
        process_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        project_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DuplicateGlobalResponse:
        """
        Duplicate an existing document, optionally into a different hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/document/duplicate",
            body=await async_maybe_transform(
                {
                    "process_id": process_id,
                    "context": context,
                    "project_id": project_id,
                },
                duplicate_global_params.DuplicateGlobalParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DuplicateGlobalResponse,
        )


class DuplicateResourceWithRawResponse:
    def __init__(self, duplicate: DuplicateResource) -> None:
        self._duplicate = duplicate

        self.duplicate = to_raw_response_wrapper(
            duplicate.duplicate,
        )
        self.global_ = to_raw_response_wrapper(
            duplicate.global_,
        )


class AsyncDuplicateResourceWithRawResponse:
    def __init__(self, duplicate: AsyncDuplicateResource) -> None:
        self._duplicate = duplicate

        self.duplicate = async_to_raw_response_wrapper(
            duplicate.duplicate,
        )
        self.global_ = async_to_raw_response_wrapper(
            duplicate.global_,
        )


class DuplicateResourceWithStreamingResponse:
    def __init__(self, duplicate: DuplicateResource) -> None:
        self._duplicate = duplicate

        self.duplicate = to_streamed_response_wrapper(
            duplicate.duplicate,
        )
        self.global_ = to_streamed_response_wrapper(
            duplicate.global_,
        )


class AsyncDuplicateResourceWithStreamingResponse:
    def __init__(self, duplicate: AsyncDuplicateResource) -> None:
        self._duplicate = duplicate

        self.duplicate = async_to_streamed_response_wrapper(
            duplicate.duplicate,
        )
        self.global_ = async_to_streamed_response_wrapper(
            duplicate.global_,
        )
