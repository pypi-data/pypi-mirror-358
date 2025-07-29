# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
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
from ...types.table import sync_update_params, sync_sync_with_integration_params
from ..._base_client import make_request_options
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.table.sync_update_response import SyncUpdateResponse
from ...types.table.sync_get_sync_info_response import SyncGetSyncInfoResponse
from ...types.table.sync_delete_integration_response import SyncDeleteIntegrationResponse
from ...types.table.sync_sync_with_integration_response import SyncSyncWithIntegrationResponse
from ...types.table.sync_retry_integration_sync_response import SyncRetryIntegrationSyncResponse

__all__ = ["SyncResource", "AsyncSyncResource"]


class SyncResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SyncResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return SyncResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SyncResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return SyncResourceWithStreamingResponse(self)

    def update(
        self,
        integration_name: str,
        *,
        table_id: str,
        company_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        doc_types: List[str] | NotGiven = NOT_GIVEN,
        enterprise_id: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        hub_id: str | NotGiven = NOT_GIVEN,
        license_id: str | NotGiven = NOT_GIVEN,
        model_id: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        project_ids: List[str] | NotGiven = NOT_GIVEN,
        properties: List[str] | NotGiven = NOT_GIVEN,
        region: str | NotGiven = NOT_GIVEN,
        top_folder_id: str | NotGiven = NOT_GIVEN,
        type: Literal[
            "Projects",
            "Resources",
            "Users",
            "Documents",
            "Workflows",
            "Comments",
            "RFIs",
            "Checklists",
            "Columns",
            "Issues",
            "AEC Data Model",
            "Forms",
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncUpdateResponse:
        """
        Update a synced table with a specified integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not integration_name:
            raise ValueError(f"Expected a non-empty value for `integration_name` but received {integration_name!r}")
        return self._post(
            f"/v1/table/{table_id}/sync/{integration_name}/update",
            body=maybe_transform(
                {
                    "company_id": company_id,
                    "context": context,
                    "doc_types": doc_types,
                    "enterprise_id": enterprise_id,
                    "folder_id": folder_id,
                    "hub_id": hub_id,
                    "license_id": license_id,
                    "model_id": model_id,
                    "project_id": project_id,
                    "project_ids": project_ids,
                    "properties": properties,
                    "region": region,
                    "top_folder_id": top_folder_id,
                    "type": type,
                },
                sync_update_params.SyncUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncUpdateResponse,
        )

    def delete_integration(
        self,
        integration_name: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDeleteIntegrationResponse:
        """
        Remove a specific integration from a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not integration_name:
            raise ValueError(f"Expected a non-empty value for `integration_name` but received {integration_name!r}")
        return self._delete(
            f"/v1/table/{table_id}/sync/{integration_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncDeleteIntegrationResponse,
        )

    def get_sync_info(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncGetSyncInfoResponse:
        """
        Retrieve the integration sync info of a given table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/sync/info",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncGetSyncInfoResponse,
        )

    def retry_integration_sync(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncRetryIntegrationSyncResponse:
        """
        Retry a failed integration sync.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/sync/manual",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncRetryIntegrationSyncResponse,
        )

    def sync_with_integration(
        self,
        integration_name: str,
        *,
        table_id: str,
        company_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        doc_types: List[str] | NotGiven = NOT_GIVEN,
        enterprise_id: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        hub_id: str | NotGiven = NOT_GIVEN,
        license_id: str | NotGiven = NOT_GIVEN,
        model_id: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        project_ids: List[str] | NotGiven = NOT_GIVEN,
        properties: List[str] | NotGiven = NOT_GIVEN,
        region: str | NotGiven = NOT_GIVEN,
        top_folder_id: str | NotGiven = NOT_GIVEN,
        type: Literal[
            "Projects",
            "Resources",
            "Users",
            "Documents",
            "Workflows",
            "Comments",
            "RFIs",
            "Checklists",
            "Columns",
            "Issues",
            "AEC Data Model",
            "Forms",
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncSyncWithIntegrationResponse:
        """
        Sync a table with a specified integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not integration_name:
            raise ValueError(f"Expected a non-empty value for `integration_name` but received {integration_name!r}")
        return self._post(
            f"/v1/table/{table_id}/sync/{integration_name}",
            body=maybe_transform(
                {
                    "company_id": company_id,
                    "context": context,
                    "doc_types": doc_types,
                    "enterprise_id": enterprise_id,
                    "folder_id": folder_id,
                    "hub_id": hub_id,
                    "license_id": license_id,
                    "model_id": model_id,
                    "project_id": project_id,
                    "project_ids": project_ids,
                    "properties": properties,
                    "region": region,
                    "top_folder_id": top_folder_id,
                    "type": type,
                },
                sync_sync_with_integration_params.SyncSyncWithIntegrationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncSyncWithIntegrationResponse,
        )


class AsyncSyncResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSyncResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSyncResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSyncResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncSyncResourceWithStreamingResponse(self)

    async def update(
        self,
        integration_name: str,
        *,
        table_id: str,
        company_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        doc_types: List[str] | NotGiven = NOT_GIVEN,
        enterprise_id: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        hub_id: str | NotGiven = NOT_GIVEN,
        license_id: str | NotGiven = NOT_GIVEN,
        model_id: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        project_ids: List[str] | NotGiven = NOT_GIVEN,
        properties: List[str] | NotGiven = NOT_GIVEN,
        region: str | NotGiven = NOT_GIVEN,
        top_folder_id: str | NotGiven = NOT_GIVEN,
        type: Literal[
            "Projects",
            "Resources",
            "Users",
            "Documents",
            "Workflows",
            "Comments",
            "RFIs",
            "Checklists",
            "Columns",
            "Issues",
            "AEC Data Model",
            "Forms",
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncUpdateResponse:
        """
        Update a synced table with a specified integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not integration_name:
            raise ValueError(f"Expected a non-empty value for `integration_name` but received {integration_name!r}")
        return await self._post(
            f"/v1/table/{table_id}/sync/{integration_name}/update",
            body=await async_maybe_transform(
                {
                    "company_id": company_id,
                    "context": context,
                    "doc_types": doc_types,
                    "enterprise_id": enterprise_id,
                    "folder_id": folder_id,
                    "hub_id": hub_id,
                    "license_id": license_id,
                    "model_id": model_id,
                    "project_id": project_id,
                    "project_ids": project_ids,
                    "properties": properties,
                    "region": region,
                    "top_folder_id": top_folder_id,
                    "type": type,
                },
                sync_update_params.SyncUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncUpdateResponse,
        )

    async def delete_integration(
        self,
        integration_name: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDeleteIntegrationResponse:
        """
        Remove a specific integration from a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not integration_name:
            raise ValueError(f"Expected a non-empty value for `integration_name` but received {integration_name!r}")
        return await self._delete(
            f"/v1/table/{table_id}/sync/{integration_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncDeleteIntegrationResponse,
        )

    async def get_sync_info(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncGetSyncInfoResponse:
        """
        Retrieve the integration sync info of a given table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/sync/info",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncGetSyncInfoResponse,
        )

    async def retry_integration_sync(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncRetryIntegrationSyncResponse:
        """
        Retry a failed integration sync.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/sync/manual",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncRetryIntegrationSyncResponse,
        )

    async def sync_with_integration(
        self,
        integration_name: str,
        *,
        table_id: str,
        company_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        doc_types: List[str] | NotGiven = NOT_GIVEN,
        enterprise_id: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        hub_id: str | NotGiven = NOT_GIVEN,
        license_id: str | NotGiven = NOT_GIVEN,
        model_id: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        project_ids: List[str] | NotGiven = NOT_GIVEN,
        properties: List[str] | NotGiven = NOT_GIVEN,
        region: str | NotGiven = NOT_GIVEN,
        top_folder_id: str | NotGiven = NOT_GIVEN,
        type: Literal[
            "Projects",
            "Resources",
            "Users",
            "Documents",
            "Workflows",
            "Comments",
            "RFIs",
            "Checklists",
            "Columns",
            "Issues",
            "AEC Data Model",
            "Forms",
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncSyncWithIntegrationResponse:
        """
        Sync a table with a specified integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not integration_name:
            raise ValueError(f"Expected a non-empty value for `integration_name` but received {integration_name!r}")
        return await self._post(
            f"/v1/table/{table_id}/sync/{integration_name}",
            body=await async_maybe_transform(
                {
                    "company_id": company_id,
                    "context": context,
                    "doc_types": doc_types,
                    "enterprise_id": enterprise_id,
                    "folder_id": folder_id,
                    "hub_id": hub_id,
                    "license_id": license_id,
                    "model_id": model_id,
                    "project_id": project_id,
                    "project_ids": project_ids,
                    "properties": properties,
                    "region": region,
                    "top_folder_id": top_folder_id,
                    "type": type,
                },
                sync_sync_with_integration_params.SyncSyncWithIntegrationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SyncSyncWithIntegrationResponse,
        )


class SyncResourceWithRawResponse:
    def __init__(self, sync: SyncResource) -> None:
        self._sync = sync

        self.update = to_raw_response_wrapper(
            sync.update,
        )
        self.delete_integration = to_raw_response_wrapper(
            sync.delete_integration,
        )
        self.get_sync_info = to_raw_response_wrapper(
            sync.get_sync_info,
        )
        self.retry_integration_sync = to_raw_response_wrapper(
            sync.retry_integration_sync,
        )
        self.sync_with_integration = to_raw_response_wrapper(
            sync.sync_with_integration,
        )


class AsyncSyncResourceWithRawResponse:
    def __init__(self, sync: AsyncSyncResource) -> None:
        self._sync = sync

        self.update = async_to_raw_response_wrapper(
            sync.update,
        )
        self.delete_integration = async_to_raw_response_wrapper(
            sync.delete_integration,
        )
        self.get_sync_info = async_to_raw_response_wrapper(
            sync.get_sync_info,
        )
        self.retry_integration_sync = async_to_raw_response_wrapper(
            sync.retry_integration_sync,
        )
        self.sync_with_integration = async_to_raw_response_wrapper(
            sync.sync_with_integration,
        )


class SyncResourceWithStreamingResponse:
    def __init__(self, sync: SyncResource) -> None:
        self._sync = sync

        self.update = to_streamed_response_wrapper(
            sync.update,
        )
        self.delete_integration = to_streamed_response_wrapper(
            sync.delete_integration,
        )
        self.get_sync_info = to_streamed_response_wrapper(
            sync.get_sync_info,
        )
        self.retry_integration_sync = to_streamed_response_wrapper(
            sync.retry_integration_sync,
        )
        self.sync_with_integration = to_streamed_response_wrapper(
            sync.sync_with_integration,
        )


class AsyncSyncResourceWithStreamingResponse:
    def __init__(self, sync: AsyncSyncResource) -> None:
        self._sync = sync

        self.update = async_to_streamed_response_wrapper(
            sync.update,
        )
        self.delete_integration = async_to_streamed_response_wrapper(
            sync.delete_integration,
        )
        self.get_sync_info = async_to_streamed_response_wrapper(
            sync.get_sync_info,
        )
        self.retry_integration_sync = async_to_streamed_response_wrapper(
            sync.retry_integration_sync,
        )
        self.sync_with_integration = async_to_streamed_response_wrapper(
            sync.sync_with_integration,
        )
