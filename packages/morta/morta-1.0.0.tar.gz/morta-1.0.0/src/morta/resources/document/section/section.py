# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from .response import (
    ResponseResource,
    AsyncResponseResource,
    ResponseResourceWithRawResponse,
    AsyncResponseResourceWithRawResponse,
    ResponseResourceWithStreamingResponse,
    AsyncResponseResourceWithStreamingResponse,
)
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
from ....types.document import section_create_params, section_update_params, section_retrieve_params
from ....types.base_request_context_param import BaseRequestContextParam
from ....types.document.section_create_response import SectionCreateResponse
from ....types.document.section_delete_response import SectionDeleteResponse
from ....types.document.section_update_response import SectionUpdateResponse
from ....types.document.section_restore_response import SectionRestoreResponse
from ....types.document.section_retrieve_response import SectionRetrieveResponse
from ....types.document.section_duplicate_response import SectionDuplicateResponse
from ....types.document.section_duplicate_async_response import SectionDuplicateAsyncResponse

__all__ = ["SectionResource", "AsyncSectionResource"]


class SectionResource(SyncAPIResource):
    @cached_property
    def response(self) -> ResponseResource:
        return ResponseResource(self._client)

    @cached_property
    def with_raw_response(self) -> SectionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return SectionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SectionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return SectionResourceWithStreamingResponse(self)

    def create(
        self,
        document_id: str,
        *,
        name: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: section_create_params.Description | NotGiven = NOT_GIVEN,
        parent_id: Optional[str] | NotGiven = NOT_GIVEN,
        plaintext_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionCreateResponse:
        """
        Create a new section within a specified document, with an option to set a parent
        section

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._post(
            f"/v1/document/{document_id}/section",
            body=maybe_transform(
                {
                    "name": name,
                    "context": context,
                    "description": description,
                    "parent_id": parent_id,
                    "plaintext_description": plaintext_description,
                },
                section_create_params.SectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionCreateResponse,
        )

    def retrieve(
        self,
        document_section_id: str,
        *,
        document_id: str,
        main_parent_section: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionRetrieveResponse:
        """
        Retrieve a specific Document section.

        Args:
          main_parent_section: Flag to retrieve the main parent section of the document section

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
        return self._get(
            f"/v1/document/{document_id}/section/{document_section_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"main_parent_section": main_parent_section}, section_retrieve_params.SectionRetrieveParams
                ),
            ),
            cast_to=SectionRetrieveResponse,
        )

    def update(
        self,
        document_section_id: str,
        *,
        document_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: section_update_params.Description | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        page_break_before: Optional[bool] | NotGiven = NOT_GIVEN,
        pdf_include_description: Optional[bool] | NotGiven = NOT_GIVEN,
        pdf_include_section: Optional[bool] | NotGiven = NOT_GIVEN,
        plaintext_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionUpdateResponse:
        """
        Update an existing document section's details by document section ID

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
        return self._put(
            f"/v1/document/{document_id}/section/{document_section_id}",
            body=maybe_transform(
                {
                    "context": context,
                    "description": description,
                    "name": name,
                    "page_break_before": page_break_before,
                    "pdf_include_description": pdf_include_description,
                    "pdf_include_section": pdf_include_section,
                    "plaintext_description": plaintext_description,
                },
                section_update_params.SectionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionUpdateResponse,
        )

    def delete(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionDeleteResponse:
        """
        Delete a specific document section.

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
        return self._delete(
            f"/v1/document/{document_id}/section/{document_section_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionDeleteResponse,
        )

    def duplicate(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionDuplicateResponse:
        """
        Duplicate a specific document section.

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
            f"/v1/document/{document_id}/section/{document_section_id}/duplicate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionDuplicateResponse,
        )

    def duplicate_async(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionDuplicateAsyncResponse:
        """
        Duplicate a specific document section asynchronously.

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
            f"/v1/document/{document_id}/section/{document_section_id}/duplicate-async",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionDuplicateAsyncResponse,
        )

    def restore(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionRestoreResponse:
        """
        Restore a previously deleted document section.

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
        return self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionRestoreResponse,
        )


class AsyncSectionResource(AsyncAPIResource):
    @cached_property
    def response(self) -> AsyncResponseResource:
        return AsyncResponseResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSectionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSectionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSectionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncSectionResourceWithStreamingResponse(self)

    async def create(
        self,
        document_id: str,
        *,
        name: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: section_create_params.Description | NotGiven = NOT_GIVEN,
        parent_id: Optional[str] | NotGiven = NOT_GIVEN,
        plaintext_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionCreateResponse:
        """
        Create a new section within a specified document, with an option to set a parent
        section

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._post(
            f"/v1/document/{document_id}/section",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "context": context,
                    "description": description,
                    "parent_id": parent_id,
                    "plaintext_description": plaintext_description,
                },
                section_create_params.SectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionCreateResponse,
        )

    async def retrieve(
        self,
        document_section_id: str,
        *,
        document_id: str,
        main_parent_section: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionRetrieveResponse:
        """
        Retrieve a specific Document section.

        Args:
          main_parent_section: Flag to retrieve the main parent section of the document section

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
        return await self._get(
            f"/v1/document/{document_id}/section/{document_section_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"main_parent_section": main_parent_section}, section_retrieve_params.SectionRetrieveParams
                ),
            ),
            cast_to=SectionRetrieveResponse,
        )

    async def update(
        self,
        document_section_id: str,
        *,
        document_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: section_update_params.Description | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        page_break_before: Optional[bool] | NotGiven = NOT_GIVEN,
        pdf_include_description: Optional[bool] | NotGiven = NOT_GIVEN,
        pdf_include_section: Optional[bool] | NotGiven = NOT_GIVEN,
        plaintext_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionUpdateResponse:
        """
        Update an existing document section's details by document section ID

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
        return await self._put(
            f"/v1/document/{document_id}/section/{document_section_id}",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "description": description,
                    "name": name,
                    "page_break_before": page_break_before,
                    "pdf_include_description": pdf_include_description,
                    "pdf_include_section": pdf_include_section,
                    "plaintext_description": plaintext_description,
                },
                section_update_params.SectionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionUpdateResponse,
        )

    async def delete(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionDeleteResponse:
        """
        Delete a specific document section.

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
        return await self._delete(
            f"/v1/document/{document_id}/section/{document_section_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionDeleteResponse,
        )

    async def duplicate(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionDuplicateResponse:
        """
        Duplicate a specific document section.

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
            f"/v1/document/{document_id}/section/{document_section_id}/duplicate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionDuplicateResponse,
        )

    async def duplicate_async(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionDuplicateAsyncResponse:
        """
        Duplicate a specific document section asynchronously.

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
            f"/v1/document/{document_id}/section/{document_section_id}/duplicate-async",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionDuplicateAsyncResponse,
        )

    async def restore(
        self,
        document_section_id: str,
        *,
        document_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SectionRestoreResponse:
        """
        Restore a previously deleted document section.

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
        return await self._put(
            f"/v1/document/{document_id}/section/{document_section_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SectionRestoreResponse,
        )


class SectionResourceWithRawResponse:
    def __init__(self, section: SectionResource) -> None:
        self._section = section

        self.create = to_raw_response_wrapper(
            section.create,
        )
        self.retrieve = to_raw_response_wrapper(
            section.retrieve,
        )
        self.update = to_raw_response_wrapper(
            section.update,
        )
        self.delete = to_raw_response_wrapper(
            section.delete,
        )
        self.duplicate = to_raw_response_wrapper(
            section.duplicate,
        )
        self.duplicate_async = to_raw_response_wrapper(
            section.duplicate_async,
        )
        self.restore = to_raw_response_wrapper(
            section.restore,
        )

    @cached_property
    def response(self) -> ResponseResourceWithRawResponse:
        return ResponseResourceWithRawResponse(self._section.response)


class AsyncSectionResourceWithRawResponse:
    def __init__(self, section: AsyncSectionResource) -> None:
        self._section = section

        self.create = async_to_raw_response_wrapper(
            section.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            section.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            section.update,
        )
        self.delete = async_to_raw_response_wrapper(
            section.delete,
        )
        self.duplicate = async_to_raw_response_wrapper(
            section.duplicate,
        )
        self.duplicate_async = async_to_raw_response_wrapper(
            section.duplicate_async,
        )
        self.restore = async_to_raw_response_wrapper(
            section.restore,
        )

    @cached_property
    def response(self) -> AsyncResponseResourceWithRawResponse:
        return AsyncResponseResourceWithRawResponse(self._section.response)


class SectionResourceWithStreamingResponse:
    def __init__(self, section: SectionResource) -> None:
        self._section = section

        self.create = to_streamed_response_wrapper(
            section.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            section.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            section.update,
        )
        self.delete = to_streamed_response_wrapper(
            section.delete,
        )
        self.duplicate = to_streamed_response_wrapper(
            section.duplicate,
        )
        self.duplicate_async = to_streamed_response_wrapper(
            section.duplicate_async,
        )
        self.restore = to_streamed_response_wrapper(
            section.restore,
        )

    @cached_property
    def response(self) -> ResponseResourceWithStreamingResponse:
        return ResponseResourceWithStreamingResponse(self._section.response)


class AsyncSectionResourceWithStreamingResponse:
    def __init__(self, section: AsyncSectionResource) -> None:
        self._section = section

        self.create = async_to_streamed_response_wrapper(
            section.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            section.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            section.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            section.delete,
        )
        self.duplicate = async_to_streamed_response_wrapper(
            section.duplicate,
        )
        self.duplicate_async = async_to_streamed_response_wrapper(
            section.duplicate_async,
        )
        self.restore = async_to_streamed_response_wrapper(
            section.restore,
        )

    @cached_property
    def response(self) -> AsyncResponseResourceWithStreamingResponse:
        return AsyncResponseResourceWithStreamingResponse(self._section.response)
