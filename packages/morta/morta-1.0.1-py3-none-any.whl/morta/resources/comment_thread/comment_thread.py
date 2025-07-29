# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...types import (
    comment_thread_list_params,
    comment_thread_create_params,
    comment_thread_get_stats_params,
)
from .comment import (
    CommentResource,
    AsyncCommentResource,
    CommentResourceWithRawResponse,
    AsyncCommentResourceWithRawResponse,
    CommentResourceWithStreamingResponse,
    AsyncCommentResourceWithStreamingResponse,
)
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
from ..._base_client import make_request_options
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.comment_thread_list_response import CommentThreadListResponse
from ...types.comment_thread_create_response import CommentThreadCreateResponse
from ...types.comment_thread_delete_response import CommentThreadDeleteResponse
from ...types.comment_thread_reopen_response import CommentThreadReopenResponse
from ...types.comment_thread_resolve_response import CommentThreadResolveResponse
from ...types.comment_thread_retrieve_response import CommentThreadRetrieveResponse
from ...types.comment_thread_get_stats_response import CommentThreadGetStatsResponse

__all__ = ["CommentThreadResource", "AsyncCommentThreadResource"]


class CommentThreadResource(SyncAPIResource):
    @cached_property
    def comment(self) -> CommentResource:
        return CommentResource(self._client)

    @cached_property
    def with_raw_response(self) -> CommentThreadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return CommentThreadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CommentThreadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return CommentThreadResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        comment_text: str,
        reference_id: str,
        reference_type: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        main_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadCreateResponse:
        """
        Create a new comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/comment_thread",
            body=maybe_transform(
                {
                    "comment_text": comment_text,
                    "reference_id": reference_id,
                    "reference_type": reference_type,
                    "context": context,
                    "main_reference_id": main_reference_id,
                },
                comment_thread_create_params.CommentThreadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadCreateResponse,
        )

    def retrieve(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadRetrieveResponse:
        """
        Retrieve a specific comment thread by its ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return self._get(
            f"/v1/comment_thread/{comment_thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadRetrieveResponse,
        )

    def list(
        self,
        *,
        reference_id: str,
        reference_type: Literal["process_section", "table", "table_view"],
        main_reference: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadListResponse:
        """
        Retrieve all comment threads associated with a specific reference

        Args:
          reference_id: UUID of the reference associated with the comment threads

          reference_type: Type of the reference (process_section, table, or table_view) associated with
              the comment threads

          main_reference: Optional main reference for additional filtering

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/comment_thread",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "reference_id": reference_id,
                        "reference_type": reference_type,
                        "main_reference": main_reference,
                    },
                    comment_thread_list_params.CommentThreadListParams,
                ),
            ),
            cast_to=CommentThreadListResponse,
        )

    def delete(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadDeleteResponse:
        """
        Delete a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return self._delete(
            f"/v1/comment_thread/{comment_thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadDeleteResponse,
        )

    def get_stats(
        self,
        *,
        reference_type: Literal["process_section", "table", "table_view"],
        main_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadGetStatsResponse:
        """
        Retrieve statistics for comment threads based on reference type and main
        reference ID

        Args:
          reference_type: Type of the reference (process_section, table, or table_view) for which to
              gather statistics

          main_reference_id: UUID of the main reference for which to gather statistics

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/comment_thread/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "reference_type": reference_type,
                        "main_reference_id": main_reference_id,
                    },
                    comment_thread_get_stats_params.CommentThreadGetStatsParams,
                ),
            ),
            cast_to=CommentThreadGetStatsResponse,
        )

    def reopen(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadReopenResponse:
        """
        Reopen a previously resolved comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return self._put(
            f"/v1/comment_thread/{comment_thread_id}/reopen",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadReopenResponse,
        )

    def resolve(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadResolveResponse:
        """
        Resolve a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return self._put(
            f"/v1/comment_thread/{comment_thread_id}/resolve",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadResolveResponse,
        )


class AsyncCommentThreadResource(AsyncAPIResource):
    @cached_property
    def comment(self) -> AsyncCommentResource:
        return AsyncCommentResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCommentThreadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCommentThreadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCommentThreadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncCommentThreadResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        comment_text: str,
        reference_id: str,
        reference_type: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        main_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadCreateResponse:
        """
        Create a new comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/comment_thread",
            body=await async_maybe_transform(
                {
                    "comment_text": comment_text,
                    "reference_id": reference_id,
                    "reference_type": reference_type,
                    "context": context,
                    "main_reference_id": main_reference_id,
                },
                comment_thread_create_params.CommentThreadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadCreateResponse,
        )

    async def retrieve(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadRetrieveResponse:
        """
        Retrieve a specific comment thread by its ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return await self._get(
            f"/v1/comment_thread/{comment_thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadRetrieveResponse,
        )

    async def list(
        self,
        *,
        reference_id: str,
        reference_type: Literal["process_section", "table", "table_view"],
        main_reference: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadListResponse:
        """
        Retrieve all comment threads associated with a specific reference

        Args:
          reference_id: UUID of the reference associated with the comment threads

          reference_type: Type of the reference (process_section, table, or table_view) associated with
              the comment threads

          main_reference: Optional main reference for additional filtering

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/comment_thread",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "reference_id": reference_id,
                        "reference_type": reference_type,
                        "main_reference": main_reference,
                    },
                    comment_thread_list_params.CommentThreadListParams,
                ),
            ),
            cast_to=CommentThreadListResponse,
        )

    async def delete(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadDeleteResponse:
        """
        Delete a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return await self._delete(
            f"/v1/comment_thread/{comment_thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadDeleteResponse,
        )

    async def get_stats(
        self,
        *,
        reference_type: Literal["process_section", "table", "table_view"],
        main_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadGetStatsResponse:
        """
        Retrieve statistics for comment threads based on reference type and main
        reference ID

        Args:
          reference_type: Type of the reference (process_section, table, or table_view) for which to
              gather statistics

          main_reference_id: UUID of the main reference for which to gather statistics

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/comment_thread/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "reference_type": reference_type,
                        "main_reference_id": main_reference_id,
                    },
                    comment_thread_get_stats_params.CommentThreadGetStatsParams,
                ),
            ),
            cast_to=CommentThreadGetStatsResponse,
        )

    async def reopen(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadReopenResponse:
        """
        Reopen a previously resolved comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return await self._put(
            f"/v1/comment_thread/{comment_thread_id}/reopen",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadReopenResponse,
        )

    async def resolve(
        self,
        comment_thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentThreadResolveResponse:
        """
        Resolve a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return await self._put(
            f"/v1/comment_thread/{comment_thread_id}/resolve",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentThreadResolveResponse,
        )


class CommentThreadResourceWithRawResponse:
    def __init__(self, comment_thread: CommentThreadResource) -> None:
        self._comment_thread = comment_thread

        self.create = to_raw_response_wrapper(
            comment_thread.create,
        )
        self.retrieve = to_raw_response_wrapper(
            comment_thread.retrieve,
        )
        self.list = to_raw_response_wrapper(
            comment_thread.list,
        )
        self.delete = to_raw_response_wrapper(
            comment_thread.delete,
        )
        self.get_stats = to_raw_response_wrapper(
            comment_thread.get_stats,
        )
        self.reopen = to_raw_response_wrapper(
            comment_thread.reopen,
        )
        self.resolve = to_raw_response_wrapper(
            comment_thread.resolve,
        )

    @cached_property
    def comment(self) -> CommentResourceWithRawResponse:
        return CommentResourceWithRawResponse(self._comment_thread.comment)


class AsyncCommentThreadResourceWithRawResponse:
    def __init__(self, comment_thread: AsyncCommentThreadResource) -> None:
        self._comment_thread = comment_thread

        self.create = async_to_raw_response_wrapper(
            comment_thread.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            comment_thread.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            comment_thread.list,
        )
        self.delete = async_to_raw_response_wrapper(
            comment_thread.delete,
        )
        self.get_stats = async_to_raw_response_wrapper(
            comment_thread.get_stats,
        )
        self.reopen = async_to_raw_response_wrapper(
            comment_thread.reopen,
        )
        self.resolve = async_to_raw_response_wrapper(
            comment_thread.resolve,
        )

    @cached_property
    def comment(self) -> AsyncCommentResourceWithRawResponse:
        return AsyncCommentResourceWithRawResponse(self._comment_thread.comment)


class CommentThreadResourceWithStreamingResponse:
    def __init__(self, comment_thread: CommentThreadResource) -> None:
        self._comment_thread = comment_thread

        self.create = to_streamed_response_wrapper(
            comment_thread.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            comment_thread.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            comment_thread.list,
        )
        self.delete = to_streamed_response_wrapper(
            comment_thread.delete,
        )
        self.get_stats = to_streamed_response_wrapper(
            comment_thread.get_stats,
        )
        self.reopen = to_streamed_response_wrapper(
            comment_thread.reopen,
        )
        self.resolve = to_streamed_response_wrapper(
            comment_thread.resolve,
        )

    @cached_property
    def comment(self) -> CommentResourceWithStreamingResponse:
        return CommentResourceWithStreamingResponse(self._comment_thread.comment)


class AsyncCommentThreadResourceWithStreamingResponse:
    def __init__(self, comment_thread: AsyncCommentThreadResource) -> None:
        self._comment_thread = comment_thread

        self.create = async_to_streamed_response_wrapper(
            comment_thread.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            comment_thread.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            comment_thread.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            comment_thread.delete,
        )
        self.get_stats = async_to_streamed_response_wrapper(
            comment_thread.get_stats,
        )
        self.reopen = async_to_streamed_response_wrapper(
            comment_thread.reopen,
        )
        self.resolve = async_to_streamed_response_wrapper(
            comment_thread.resolve,
        )

    @cached_property
    def comment(self) -> AsyncCommentResourceWithStreamingResponse:
        return AsyncCommentResourceWithStreamingResponse(self._comment_thread.comment)
