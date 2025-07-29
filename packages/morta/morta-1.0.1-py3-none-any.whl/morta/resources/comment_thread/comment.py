# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ..._base_client import make_request_options
from ...types.comment_thread import comment_create_params, comment_update_params
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.comment_thread.comment_create_response import CommentCreateResponse
from ...types.comment_thread.comment_delete_response import CommentDeleteResponse
from ...types.comment_thread.comment_update_response import CommentUpdateResponse

__all__ = ["CommentResource", "AsyncCommentResource"]


class CommentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CommentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return CommentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CommentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return CommentResourceWithStreamingResponse(self)

    def create(
        self,
        comment_thread_id: str,
        *,
        comment_text: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentCreateResponse:
        """
        Create a new comment within a specific comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return self._post(
            f"/v1/comment_thread/{comment_thread_id}/comment",
            body=maybe_transform(
                {
                    "comment_text": comment_text,
                    "context": context,
                },
                comment_create_params.CommentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentCreateResponse,
        )

    def update(
        self,
        comment_id: str,
        *,
        comment_thread_id: str,
        comment_text: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentUpdateResponse:
        """
        Update a specific comment within a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        if not comment_id:
            raise ValueError(f"Expected a non-empty value for `comment_id` but received {comment_id!r}")
        return self._put(
            f"/v1/comment_thread/{comment_thread_id}/comment/{comment_id}",
            body=maybe_transform(
                {
                    "comment_text": comment_text,
                    "context": context,
                },
                comment_update_params.CommentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentUpdateResponse,
        )

    def delete(
        self,
        comment_id: str,
        *,
        comment_thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentDeleteResponse:
        """
        Delete a specific comment within a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        if not comment_id:
            raise ValueError(f"Expected a non-empty value for `comment_id` but received {comment_id!r}")
        return self._delete(
            f"/v1/comment_thread/{comment_thread_id}/comment/{comment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentDeleteResponse,
        )


class AsyncCommentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCommentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCommentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCommentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncCommentResourceWithStreamingResponse(self)

    async def create(
        self,
        comment_thread_id: str,
        *,
        comment_text: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentCreateResponse:
        """
        Create a new comment within a specific comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        return await self._post(
            f"/v1/comment_thread/{comment_thread_id}/comment",
            body=await async_maybe_transform(
                {
                    "comment_text": comment_text,
                    "context": context,
                },
                comment_create_params.CommentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentCreateResponse,
        )

    async def update(
        self,
        comment_id: str,
        *,
        comment_thread_id: str,
        comment_text: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentUpdateResponse:
        """
        Update a specific comment within a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        if not comment_id:
            raise ValueError(f"Expected a non-empty value for `comment_id` but received {comment_id!r}")
        return await self._put(
            f"/v1/comment_thread/{comment_thread_id}/comment/{comment_id}",
            body=await async_maybe_transform(
                {
                    "comment_text": comment_text,
                    "context": context,
                },
                comment_update_params.CommentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentUpdateResponse,
        )

    async def delete(
        self,
        comment_id: str,
        *,
        comment_thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommentDeleteResponse:
        """
        Delete a specific comment within a comment thread

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not comment_thread_id:
            raise ValueError(f"Expected a non-empty value for `comment_thread_id` but received {comment_thread_id!r}")
        if not comment_id:
            raise ValueError(f"Expected a non-empty value for `comment_id` but received {comment_id!r}")
        return await self._delete(
            f"/v1/comment_thread/{comment_thread_id}/comment/{comment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommentDeleteResponse,
        )


class CommentResourceWithRawResponse:
    def __init__(self, comment: CommentResource) -> None:
        self._comment = comment

        self.create = to_raw_response_wrapper(
            comment.create,
        )
        self.update = to_raw_response_wrapper(
            comment.update,
        )
        self.delete = to_raw_response_wrapper(
            comment.delete,
        )


class AsyncCommentResourceWithRawResponse:
    def __init__(self, comment: AsyncCommentResource) -> None:
        self._comment = comment

        self.create = async_to_raw_response_wrapper(
            comment.create,
        )
        self.update = async_to_raw_response_wrapper(
            comment.update,
        )
        self.delete = async_to_raw_response_wrapper(
            comment.delete,
        )


class CommentResourceWithStreamingResponse:
    def __init__(self, comment: CommentResource) -> None:
        self._comment = comment

        self.create = to_streamed_response_wrapper(
            comment.create,
        )
        self.update = to_streamed_response_wrapper(
            comment.update,
        )
        self.delete = to_streamed_response_wrapper(
            comment.delete,
        )


class AsyncCommentResourceWithStreamingResponse:
    def __init__(self, comment: AsyncCommentResource) -> None:
        self._comment = comment

        self.create = async_to_streamed_response_wrapper(
            comment.create,
        )
        self.update = async_to_streamed_response_wrapper(
            comment.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            comment.delete,
        )
