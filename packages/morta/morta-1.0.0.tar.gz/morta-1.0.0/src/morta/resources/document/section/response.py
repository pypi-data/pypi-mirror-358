# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.document.section import response_create_params, response_submit_params, response_update_params
from ....types.base_request_context_param import BaseRequestContextParam
from ....types.document.section.response_reset_response import ResponseResetResponse
from ....types.document.section.response_create_response import ResponseCreateResponse
from ....types.document.section.response_delete_response import ResponseDeleteResponse
from ....types.document.section.response_submit_response import ResponseSubmitResponse
from ....types.document.section.response_update_response import ResponseUpdateResponse
from ....types.document.section.response_restore_response import ResponseRestoreResponse

__all__ = ["ResponseResource", "AsyncResponseResource"]


class ResponseResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ResponseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return ResponseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResponseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return ResponseResourceWithStreamingResponse(self)

    def create(
        self,
        document_section_id: str,
        *,
        document_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        type: Optional[Literal["Flexible", "File Upload", "Table", "Signature", "Selection"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseCreateResponse:
        """
        Create a new response for a document section.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        return self._post(
            f"/v1/document/{document_id}/section/{document_section_id}/response",
            body=maybe_transform(
                {
                    "context": context,
                    "type": type,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseCreateResponse,
        )

    def update(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        enable_submission: Optional[bool] | NotGiven = NOT_GIVEN,
        pdf_include_response: Optional[bool] | NotGiven = NOT_GIVEN,
        reset_after_response: Optional[bool] | NotGiven = NOT_GIVEN,
        type: Optional[Literal["Flexible", "File Upload", "Table", "Signature", "Selection"]] | NotGiven = NOT_GIVEN,
        type_options: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseUpdateResponse:
        """
        Update an existing response for a document section.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}",
            body=maybe_transform(
                {
                    "context": context,
                    "enable_submission": enable_submission,
                    "pdf_include_response": pdf_include_response,
                    "reset_after_response": reset_after_response,
                    "type": type,
                    "type_options": type_options,
                },
                response_update_params.ResponseUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseUpdateResponse,
        )

    def delete(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseDeleteResponse:
        """
        Delete a specific document response.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return self._delete(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseDeleteResponse,
        )

    def reset(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseResetResponse:
        """
        Reset an existing document response to its initial state.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}/reset",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseResetResponse,
        )

    def restore(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseRestoreResponse:
        """
        Restore a previously deleted document response.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseRestoreResponse,
        )

    def submit(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        response: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseSubmitResponse:
        """
        Submit a document response, marking it as completed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}/submit",
            body=maybe_transform(
                {
                    "context": context,
                    "response": response,
                },
                response_submit_params.ResponseSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseSubmitResponse,
        )


class AsyncResponseResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncResponseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncResponseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResponseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncResponseResourceWithStreamingResponse(self)

    async def create(
        self,
        document_section_id: str,
        *,
        document_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        type: Optional[Literal["Flexible", "File Upload", "Table", "Signature", "Selection"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseCreateResponse:
        """
        Create a new response for a document section.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        return await self._post(
            f"/v1/document/{document_id}/section/{document_section_id}/response",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "type": type,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseCreateResponse,
        )

    async def update(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        enable_submission: Optional[bool] | NotGiven = NOT_GIVEN,
        pdf_include_response: Optional[bool] | NotGiven = NOT_GIVEN,
        reset_after_response: Optional[bool] | NotGiven = NOT_GIVEN,
        type: Optional[Literal["Flexible", "File Upload", "Table", "Signature", "Selection"]] | NotGiven = NOT_GIVEN,
        type_options: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseUpdateResponse:
        """
        Update an existing response for a document section.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return await self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "enable_submission": enable_submission,
                    "pdf_include_response": pdf_include_response,
                    "reset_after_response": reset_after_response,
                    "type": type,
                    "type_options": type_options,
                },
                response_update_params.ResponseUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseUpdateResponse,
        )

    async def delete(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseDeleteResponse:
        """
        Delete a specific document response.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return await self._delete(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseDeleteResponse,
        )

    async def reset(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseResetResponse:
        """
        Reset an existing document response to its initial state.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return await self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}/reset",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseResetResponse,
        )

    async def restore(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseRestoreResponse:
        """
        Restore a previously deleted document response.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return await self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseRestoreResponse,
        )

    async def submit(
        self,
        document_response_id: str,
        *,
        document_id: str,
        document_section_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        response: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseSubmitResponse:
        """
        Submit a document response, marking it as completed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        if not document_section_id:
            raise ValueError(
                f"Expected a non-empty value for `document_section_id` but received {document_section_id!r}"
            )
        if not document_response_id:
            raise ValueError(
                f"Expected a non-empty value for `document_response_id` but received {document_response_id!r}"
            )
        return await self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/response/{document_response_id}/submit",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "response": response,
                },
                response_submit_params.ResponseSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseSubmitResponse,
        )


class ResponseResourceWithRawResponse:
    def __init__(self, response: ResponseResource) -> None:
        self._response = response

        self.create = to_raw_response_wrapper(
            response.create,
        )
        self.update = to_raw_response_wrapper(
            response.update,
        )
        self.delete = to_raw_response_wrapper(
            response.delete,
        )
        self.reset = to_raw_response_wrapper(
            response.reset,
        )
        self.restore = to_raw_response_wrapper(
            response.restore,
        )
        self.submit = to_raw_response_wrapper(
            response.submit,
        )


class AsyncResponseResourceWithRawResponse:
    def __init__(self, response: AsyncResponseResource) -> None:
        self._response = response

        self.create = async_to_raw_response_wrapper(
            response.create,
        )
        self.update = async_to_raw_response_wrapper(
            response.update,
        )
        self.delete = async_to_raw_response_wrapper(
            response.delete,
        )
        self.reset = async_to_raw_response_wrapper(
            response.reset,
        )
        self.restore = async_to_raw_response_wrapper(
            response.restore,
        )
        self.submit = async_to_raw_response_wrapper(
            response.submit,
        )


class ResponseResourceWithStreamingResponse:
    def __init__(self, response: ResponseResource) -> None:
        self._response = response

        self.create = to_streamed_response_wrapper(
            response.create,
        )
        self.update = to_streamed_response_wrapper(
            response.update,
        )
        self.delete = to_streamed_response_wrapper(
            response.delete,
        )
        self.reset = to_streamed_response_wrapper(
            response.reset,
        )
        self.restore = to_streamed_response_wrapper(
            response.restore,
        )
        self.submit = to_streamed_response_wrapper(
            response.submit,
        )


class AsyncResponseResourceWithStreamingResponse:
    def __init__(self, response: AsyncResponseResource) -> None:
        self._response = response

        self.create = async_to_streamed_response_wrapper(
            response.create,
        )
        self.update = async_to_streamed_response_wrapper(
            response.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            response.delete,
        )
        self.reset = async_to_streamed_response_wrapper(
            response.reset,
        )
        self.restore = async_to_streamed_response_wrapper(
            response.restore,
        )
        self.submit = async_to_streamed_response_wrapper(
            response.submit,
        )
