# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable, Optional
from typing_extensions import Literal

import httpx

from .rows import (
    RowsResource,
    AsyncRowsResource,
    RowsResourceWithRawResponse,
    AsyncRowsResourceWithRawResponse,
    RowsResourceWithStreamingResponse,
    AsyncRowsResourceWithStreamingResponse,
)
from .columns import (
    ColumnsResource,
    AsyncColumnsResource,
    ColumnsResourceWithRawResponse,
    AsyncColumnsResourceWithRawResponse,
    ColumnsResourceWithStreamingResponse,
    AsyncColumnsResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ....types.table import (
    view_list_params,
    view_stats_params,
    view_create_params,
    view_update_params,
    view_retrieve_params,
    view_preview_row_params,
    view_stream_rows_params,
    view_download_csv_params,
    view_update_cells_params,
    view_duplicate_default_params,
)
from ...._base_client import make_request_options
from ....types.table.sort_param import SortParam
from ....types.table.group_param import GroupParam
from ....types.table.colour_param import ColourParam
from ....types.table.filter_param import FilterParam
from ....types.table.view_list_response import ViewListResponse
from ....types.table.view_stats_response import ViewStatsResponse
from ....types.base_request_context_param import BaseRequestContextParam
from ....types.table.view_create_response import ViewCreateResponse
from ....types.table.view_delete_response import ViewDeleteResponse
from ....types.table.view_update_response import ViewUpdateResponse
from ....types.table.view_retrieve_response import ViewRetrieveResponse
from ....types.table.view_duplicate_response import ViewDuplicateResponse
from ....types.table.view_preview_row_response import ViewPreviewRowResponse
from ....types.table.view_set_default_response import ViewSetDefaultResponse
from ....types.table.view_update_cells_response import ViewUpdateCellsResponse
from ....types.table.view_duplicate_default_response import ViewDuplicateDefaultResponse
from ....types.table.views.update_table_view_column_param import UpdateTableViewColumnParam

__all__ = ["ViewsResource", "AsyncViewsResource"]


class ViewsResource(SyncAPIResource):
    @cached_property
    def rows(self) -> RowsResource:
        return RowsResource(self._client)

    @cached_property
    def columns(self) -> ColumnsResource:
        return ColumnsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ViewsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return ViewsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ViewsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return ViewsResourceWithStreamingResponse(self)

    def create(
        self,
        table_id: str,
        *,
        name: str,
        allow_contributor_delete: bool | NotGiven = NOT_GIVEN,
        chart_settings: view_create_params.ChartSettings | NotGiven = NOT_GIVEN,
        collapsed_group_view: bool | NotGiven = NOT_GIVEN,
        colour_settings: Iterable[ColourParam] | NotGiven = NOT_GIVEN,
        columns: Iterable[view_create_params.Column] | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: view_create_params.Description | NotGiven = NOT_GIVEN,
        disable_new_row: bool | NotGiven = NOT_GIVEN,
        disable_sync_csv: bool | NotGiven = NOT_GIVEN,
        display_comment_rows: int | NotGiven = NOT_GIVEN,
        display_validation_error_rows: Literal[0, 1, 2] | NotGiven = NOT_GIVEN,
        filter_settings: Iterable[FilterParam] | NotGiven = NOT_GIVEN,
        frozen_index: int | NotGiven = NOT_GIVEN,
        group_settings: Iterable[GroupParam] | NotGiven = NOT_GIVEN,
        include_all_columns: bool | NotGiven = NOT_GIVEN,
        is_default: bool | NotGiven = NOT_GIVEN,
        row_height: int | NotGiven = NOT_GIVEN,
        sort_settings: Iterable[SortParam] | NotGiven = NOT_GIVEN,
        type: int | NotGiven = NOT_GIVEN,
        unpack_multiselect_group_view: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewCreateResponse:
        """
        Create a new view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._post(
            f"/v1/table/{table_id}/views",
            body=maybe_transform(
                {
                    "name": name,
                    "allow_contributor_delete": allow_contributor_delete,
                    "chart_settings": chart_settings,
                    "collapsed_group_view": collapsed_group_view,
                    "colour_settings": colour_settings,
                    "columns": columns,
                    "context": context,
                    "description": description,
                    "disable_new_row": disable_new_row,
                    "disable_sync_csv": disable_sync_csv,
                    "display_comment_rows": display_comment_rows,
                    "display_validation_error_rows": display_validation_error_rows,
                    "filter_settings": filter_settings,
                    "frozen_index": frozen_index,
                    "group_settings": group_settings,
                    "include_all_columns": include_all_columns,
                    "is_default": is_default,
                    "row_height": row_height,
                    "sort_settings": sort_settings,
                    "type": type,
                    "unpack_multiselect_group_view": unpack_multiselect_group_view,
                },
                view_create_params.ViewCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewCreateResponse,
        )

    def retrieve(
        self,
        view_id: str,
        *,
        ignore_cached_options: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewRetrieveResponse:
        """
        Retrieve a specific view by its ID for a table.

        Args:
          ignore_cached_options: Flag to indicate whether to ignore cached options in the response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._get(
            f"/v1/table/views/{view_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"ignore_cached_options": ignore_cached_options}, view_retrieve_params.ViewRetrieveParams
                ),
            ),
            cast_to=ViewRetrieveResponse,
        )

    def update(
        self,
        view_id: str,
        *,
        allow_contributor_delete: bool | NotGiven = NOT_GIVEN,
        chart_settings: view_update_params.ChartSettings | NotGiven = NOT_GIVEN,
        collapsed_group_view: bool | NotGiven = NOT_GIVEN,
        colour_settings: Iterable[ColourParam] | NotGiven = NOT_GIVEN,
        columns: Iterable[UpdateTableViewColumnParam] | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: view_update_params.Description | NotGiven = NOT_GIVEN,
        disable_new_row: bool | NotGiven = NOT_GIVEN,
        disable_sync_csv: bool | NotGiven = NOT_GIVEN,
        display_comment_rows: int | NotGiven = NOT_GIVEN,
        display_validation_error_rows: Literal[0, 1, 2] | NotGiven = NOT_GIVEN,
        filter_settings: Iterable[FilterParam] | NotGiven = NOT_GIVEN,
        frozen_index: int | NotGiven = NOT_GIVEN,
        group_settings: Iterable[GroupParam] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        row_height: int | NotGiven = NOT_GIVEN,
        sort_settings: Iterable[SortParam] | NotGiven = NOT_GIVEN,
        type: int | NotGiven = NOT_GIVEN,
        unpack_multiselect_group_view: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewUpdateResponse:
        """
        Update an existing view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._put(
            f"/v1/table/views/{view_id}",
            body=maybe_transform(
                {
                    "allow_contributor_delete": allow_contributor_delete,
                    "chart_settings": chart_settings,
                    "collapsed_group_view": collapsed_group_view,
                    "colour_settings": colour_settings,
                    "columns": columns,
                    "context": context,
                    "description": description,
                    "disable_new_row": disable_new_row,
                    "disable_sync_csv": disable_sync_csv,
                    "display_comment_rows": display_comment_rows,
                    "display_validation_error_rows": display_validation_error_rows,
                    "filter_settings": filter_settings,
                    "frozen_index": frozen_index,
                    "group_settings": group_settings,
                    "name": name,
                    "row_height": row_height,
                    "sort_settings": sort_settings,
                    "type": type,
                    "unpack_multiselect_group_view": unpack_multiselect_group_view,
                },
                view_update_params.ViewUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewUpdateResponse,
        )

    def list(
        self,
        table_id: str,
        *,
        ignore_columns: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewListResponse:
        """
        Retrieve all views associated with a specific table.

        Args:
          ignore_columns: Flag to indicate whether to ignore column data in the response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/views",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"ignore_columns": ignore_columns}, view_list_params.ViewListParams),
            ),
            cast_to=ViewListResponse,
        )

    def delete(
        self,
        view_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewDeleteResponse:
        """
        Delete a specific view of a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._delete(
            f"/v1/table/views/{view_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewDeleteResponse,
        )

    def download_csv(
        self,
        view_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        process_id: str | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Download the data of a specific table view in CSV format.

        Args:
          filter: Filters to apply to the CSV data.

          process_id: Optional UUID of a process to filter the data.

          sort: Sorting parameters for the CSV data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return self._get(
            f"/v1/table/views/{view_id}/csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "process_id": process_id,
                        "sort": sort,
                    },
                    view_download_csv_params.ViewDownloadCsvParams,
                ),
            ),
            cast_to=str,
        )

    def duplicate(
        self,
        view_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewDuplicateResponse:
        """
        Create a duplicate of an existing view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._post(
            f"/v1/table/{table_id}/views/{view_id}/duplicate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewDuplicateResponse,
        )

    def duplicate_default(
        self,
        table_id: str,
        *,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        type: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewDuplicateDefaultResponse:
        """
        Create a duplicate of the default view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._post(
            f"/v1/table/{table_id}/views/duplicate-default",
            body=maybe_transform(
                {
                    "context": context,
                    "name": name,
                    "type": type,
                },
                view_duplicate_default_params.ViewDuplicateDefaultParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewDuplicateDefaultResponse,
        )

    def preview_row(
        self,
        view_id: str,
        *,
        row_data: Dict[str, Optional[object]],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewPreviewRowResponse:
        """
        Preview the resulting row from given inputs in a specific table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._post(
            f"/v1/table/views/{view_id}/preview-row",
            body=maybe_transform(
                {
                    "row_data": row_data,
                    "context": context,
                },
                view_preview_row_params.ViewPreviewRowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewPreviewRowResponse,
        )

    def set_default(
        self,
        view_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewSetDefaultResponse:
        """
        Designate a specific table view as the default view for the table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._post(
            f"/v1/table/views/{view_id}/default",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewSetDefaultResponse,
        )

    def stats(
        self,
        view_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        process_id: str | NotGiven = NOT_GIVEN,
        sum_avg_max_min_count: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewStatsResponse:
        """
        Retrieve statistical data for columns in a specific table view.

        Args:
          filter: Filters to apply to the statistical data retrieval.

          process_id: Optional UUID of a process to filter the data.

          sum_avg_max_min_count: Specify columns to perform sum, average, max, min, or count operations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._get(
            f"/v1/table/views/{view_id}/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "process_id": process_id,
                        "sum_avg_max_min_count": sum_avg_max_min_count,
                    },
                    view_stats_params.ViewStatsParams,
                ),
            ),
            cast_to=ViewStatsResponse,
        )

    def stream_rows(
        self,
        view_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        process_id: str | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Stream the data of all rows for a specific table view.

        Args:
          filter: Filters to apply to the streaming data.

          page: Page number for pagination

          process_id: Optional UUID of a process to filter the data.

          size: Number of items per page for pagination

          sort: Sorting parameters for the streaming data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        extra_headers = {"Accept": "application/x-msgppack", **(extra_headers or {})}
        return self._get(
            f"/v1/table/views/{view_id}/rows-stream",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "process_id": process_id,
                        "size": size,
                        "sort": sort,
                    },
                    view_stream_rows_params.ViewStreamRowsParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def update_cells(
        self,
        view_id: str,
        *,
        cells: Iterable[view_update_cells_params.Cell],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewUpdateCellsResponse:
        """
        Update specific cells in a table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._put(
            f"/v1/table/views/{view_id}/cells",
            body=maybe_transform(
                {
                    "cells": cells,
                    "context": context,
                },
                view_update_cells_params.ViewUpdateCellsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewUpdateCellsResponse,
        )


class AsyncViewsResource(AsyncAPIResource):
    @cached_property
    def rows(self) -> AsyncRowsResource:
        return AsyncRowsResource(self._client)

    @cached_property
    def columns(self) -> AsyncColumnsResource:
        return AsyncColumnsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncViewsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncViewsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncViewsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncViewsResourceWithStreamingResponse(self)

    async def create(
        self,
        table_id: str,
        *,
        name: str,
        allow_contributor_delete: bool | NotGiven = NOT_GIVEN,
        chart_settings: view_create_params.ChartSettings | NotGiven = NOT_GIVEN,
        collapsed_group_view: bool | NotGiven = NOT_GIVEN,
        colour_settings: Iterable[ColourParam] | NotGiven = NOT_GIVEN,
        columns: Iterable[view_create_params.Column] | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: view_create_params.Description | NotGiven = NOT_GIVEN,
        disable_new_row: bool | NotGiven = NOT_GIVEN,
        disable_sync_csv: bool | NotGiven = NOT_GIVEN,
        display_comment_rows: int | NotGiven = NOT_GIVEN,
        display_validation_error_rows: Literal[0, 1, 2] | NotGiven = NOT_GIVEN,
        filter_settings: Iterable[FilterParam] | NotGiven = NOT_GIVEN,
        frozen_index: int | NotGiven = NOT_GIVEN,
        group_settings: Iterable[GroupParam] | NotGiven = NOT_GIVEN,
        include_all_columns: bool | NotGiven = NOT_GIVEN,
        is_default: bool | NotGiven = NOT_GIVEN,
        row_height: int | NotGiven = NOT_GIVEN,
        sort_settings: Iterable[SortParam] | NotGiven = NOT_GIVEN,
        type: int | NotGiven = NOT_GIVEN,
        unpack_multiselect_group_view: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewCreateResponse:
        """
        Create a new view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/views",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "allow_contributor_delete": allow_contributor_delete,
                    "chart_settings": chart_settings,
                    "collapsed_group_view": collapsed_group_view,
                    "colour_settings": colour_settings,
                    "columns": columns,
                    "context": context,
                    "description": description,
                    "disable_new_row": disable_new_row,
                    "disable_sync_csv": disable_sync_csv,
                    "display_comment_rows": display_comment_rows,
                    "display_validation_error_rows": display_validation_error_rows,
                    "filter_settings": filter_settings,
                    "frozen_index": frozen_index,
                    "group_settings": group_settings,
                    "include_all_columns": include_all_columns,
                    "is_default": is_default,
                    "row_height": row_height,
                    "sort_settings": sort_settings,
                    "type": type,
                    "unpack_multiselect_group_view": unpack_multiselect_group_view,
                },
                view_create_params.ViewCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewCreateResponse,
        )

    async def retrieve(
        self,
        view_id: str,
        *,
        ignore_cached_options: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewRetrieveResponse:
        """
        Retrieve a specific view by its ID for a table.

        Args:
          ignore_cached_options: Flag to indicate whether to ignore cached options in the response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._get(
            f"/v1/table/views/{view_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"ignore_cached_options": ignore_cached_options}, view_retrieve_params.ViewRetrieveParams
                ),
            ),
            cast_to=ViewRetrieveResponse,
        )

    async def update(
        self,
        view_id: str,
        *,
        allow_contributor_delete: bool | NotGiven = NOT_GIVEN,
        chart_settings: view_update_params.ChartSettings | NotGiven = NOT_GIVEN,
        collapsed_group_view: bool | NotGiven = NOT_GIVEN,
        colour_settings: Iterable[ColourParam] | NotGiven = NOT_GIVEN,
        columns: Iterable[UpdateTableViewColumnParam] | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        description: view_update_params.Description | NotGiven = NOT_GIVEN,
        disable_new_row: bool | NotGiven = NOT_GIVEN,
        disable_sync_csv: bool | NotGiven = NOT_GIVEN,
        display_comment_rows: int | NotGiven = NOT_GIVEN,
        display_validation_error_rows: Literal[0, 1, 2] | NotGiven = NOT_GIVEN,
        filter_settings: Iterable[FilterParam] | NotGiven = NOT_GIVEN,
        frozen_index: int | NotGiven = NOT_GIVEN,
        group_settings: Iterable[GroupParam] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        row_height: int | NotGiven = NOT_GIVEN,
        sort_settings: Iterable[SortParam] | NotGiven = NOT_GIVEN,
        type: int | NotGiven = NOT_GIVEN,
        unpack_multiselect_group_view: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewUpdateResponse:
        """
        Update an existing view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._put(
            f"/v1/table/views/{view_id}",
            body=await async_maybe_transform(
                {
                    "allow_contributor_delete": allow_contributor_delete,
                    "chart_settings": chart_settings,
                    "collapsed_group_view": collapsed_group_view,
                    "colour_settings": colour_settings,
                    "columns": columns,
                    "context": context,
                    "description": description,
                    "disable_new_row": disable_new_row,
                    "disable_sync_csv": disable_sync_csv,
                    "display_comment_rows": display_comment_rows,
                    "display_validation_error_rows": display_validation_error_rows,
                    "filter_settings": filter_settings,
                    "frozen_index": frozen_index,
                    "group_settings": group_settings,
                    "name": name,
                    "row_height": row_height,
                    "sort_settings": sort_settings,
                    "type": type,
                    "unpack_multiselect_group_view": unpack_multiselect_group_view,
                },
                view_update_params.ViewUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewUpdateResponse,
        )

    async def list(
        self,
        table_id: str,
        *,
        ignore_columns: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewListResponse:
        """
        Retrieve all views associated with a specific table.

        Args:
          ignore_columns: Flag to indicate whether to ignore column data in the response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/views",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"ignore_columns": ignore_columns}, view_list_params.ViewListParams),
            ),
            cast_to=ViewListResponse,
        )

    async def delete(
        self,
        view_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewDeleteResponse:
        """
        Delete a specific view of a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._delete(
            f"/v1/table/views/{view_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewDeleteResponse,
        )

    async def download_csv(
        self,
        view_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        process_id: str | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Download the data of a specific table view in CSV format.

        Args:
          filter: Filters to apply to the CSV data.

          process_id: Optional UUID of a process to filter the data.

          sort: Sorting parameters for the CSV data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return await self._get(
            f"/v1/table/views/{view_id}/csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "process_id": process_id,
                        "sort": sort,
                    },
                    view_download_csv_params.ViewDownloadCsvParams,
                ),
            ),
            cast_to=str,
        )

    async def duplicate(
        self,
        view_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewDuplicateResponse:
        """
        Create a duplicate of an existing view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/views/{view_id}/duplicate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewDuplicateResponse,
        )

    async def duplicate_default(
        self,
        table_id: str,
        *,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        type: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewDuplicateDefaultResponse:
        """
        Create a duplicate of the default view for a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/views/duplicate-default",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "name": name,
                    "type": type,
                },
                view_duplicate_default_params.ViewDuplicateDefaultParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewDuplicateDefaultResponse,
        )

    async def preview_row(
        self,
        view_id: str,
        *,
        row_data: Dict[str, Optional[object]],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewPreviewRowResponse:
        """
        Preview the resulting row from given inputs in a specific table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._post(
            f"/v1/table/views/{view_id}/preview-row",
            body=await async_maybe_transform(
                {
                    "row_data": row_data,
                    "context": context,
                },
                view_preview_row_params.ViewPreviewRowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewPreviewRowResponse,
        )

    async def set_default(
        self,
        view_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewSetDefaultResponse:
        """
        Designate a specific table view as the default view for the table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._post(
            f"/v1/table/views/{view_id}/default",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewSetDefaultResponse,
        )

    async def stats(
        self,
        view_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        process_id: str | NotGiven = NOT_GIVEN,
        sum_avg_max_min_count: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewStatsResponse:
        """
        Retrieve statistical data for columns in a specific table view.

        Args:
          filter: Filters to apply to the statistical data retrieval.

          process_id: Optional UUID of a process to filter the data.

          sum_avg_max_min_count: Specify columns to perform sum, average, max, min, or count operations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._get(
            f"/v1/table/views/{view_id}/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "process_id": process_id,
                        "sum_avg_max_min_count": sum_avg_max_min_count,
                    },
                    view_stats_params.ViewStatsParams,
                ),
            ),
            cast_to=ViewStatsResponse,
        )

    async def stream_rows(
        self,
        view_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        process_id: str | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Stream the data of all rows for a specific table view.

        Args:
          filter: Filters to apply to the streaming data.

          page: Page number for pagination

          process_id: Optional UUID of a process to filter the data.

          size: Number of items per page for pagination

          sort: Sorting parameters for the streaming data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        extra_headers = {"Accept": "application/x-msgppack", **(extra_headers or {})}
        return await self._get(
            f"/v1/table/views/{view_id}/rows-stream",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "process_id": process_id,
                        "size": size,
                        "sort": sort,
                    },
                    view_stream_rows_params.ViewStreamRowsParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def update_cells(
        self,
        view_id: str,
        *,
        cells: Iterable[view_update_cells_params.Cell],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ViewUpdateCellsResponse:
        """
        Update specific cells in a table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._put(
            f"/v1/table/views/{view_id}/cells",
            body=await async_maybe_transform(
                {
                    "cells": cells,
                    "context": context,
                },
                view_update_cells_params.ViewUpdateCellsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewUpdateCellsResponse,
        )


class ViewsResourceWithRawResponse:
    def __init__(self, views: ViewsResource) -> None:
        self._views = views

        self.create = to_raw_response_wrapper(
            views.create,
        )
        self.retrieve = to_raw_response_wrapper(
            views.retrieve,
        )
        self.update = to_raw_response_wrapper(
            views.update,
        )
        self.list = to_raw_response_wrapper(
            views.list,
        )
        self.delete = to_raw_response_wrapper(
            views.delete,
        )
        self.download_csv = to_raw_response_wrapper(
            views.download_csv,
        )
        self.duplicate = to_raw_response_wrapper(
            views.duplicate,
        )
        self.duplicate_default = to_raw_response_wrapper(
            views.duplicate_default,
        )
        self.preview_row = to_raw_response_wrapper(
            views.preview_row,
        )
        self.set_default = to_raw_response_wrapper(
            views.set_default,
        )
        self.stats = to_raw_response_wrapper(
            views.stats,
        )
        self.stream_rows = to_custom_raw_response_wrapper(
            views.stream_rows,
            BinaryAPIResponse,
        )
        self.update_cells = to_raw_response_wrapper(
            views.update_cells,
        )

    @cached_property
    def rows(self) -> RowsResourceWithRawResponse:
        return RowsResourceWithRawResponse(self._views.rows)

    @cached_property
    def columns(self) -> ColumnsResourceWithRawResponse:
        return ColumnsResourceWithRawResponse(self._views.columns)


class AsyncViewsResourceWithRawResponse:
    def __init__(self, views: AsyncViewsResource) -> None:
        self._views = views

        self.create = async_to_raw_response_wrapper(
            views.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            views.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            views.update,
        )
        self.list = async_to_raw_response_wrapper(
            views.list,
        )
        self.delete = async_to_raw_response_wrapper(
            views.delete,
        )
        self.download_csv = async_to_raw_response_wrapper(
            views.download_csv,
        )
        self.duplicate = async_to_raw_response_wrapper(
            views.duplicate,
        )
        self.duplicate_default = async_to_raw_response_wrapper(
            views.duplicate_default,
        )
        self.preview_row = async_to_raw_response_wrapper(
            views.preview_row,
        )
        self.set_default = async_to_raw_response_wrapper(
            views.set_default,
        )
        self.stats = async_to_raw_response_wrapper(
            views.stats,
        )
        self.stream_rows = async_to_custom_raw_response_wrapper(
            views.stream_rows,
            AsyncBinaryAPIResponse,
        )
        self.update_cells = async_to_raw_response_wrapper(
            views.update_cells,
        )

    @cached_property
    def rows(self) -> AsyncRowsResourceWithRawResponse:
        return AsyncRowsResourceWithRawResponse(self._views.rows)

    @cached_property
    def columns(self) -> AsyncColumnsResourceWithRawResponse:
        return AsyncColumnsResourceWithRawResponse(self._views.columns)


class ViewsResourceWithStreamingResponse:
    def __init__(self, views: ViewsResource) -> None:
        self._views = views

        self.create = to_streamed_response_wrapper(
            views.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            views.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            views.update,
        )
        self.list = to_streamed_response_wrapper(
            views.list,
        )
        self.delete = to_streamed_response_wrapper(
            views.delete,
        )
        self.download_csv = to_streamed_response_wrapper(
            views.download_csv,
        )
        self.duplicate = to_streamed_response_wrapper(
            views.duplicate,
        )
        self.duplicate_default = to_streamed_response_wrapper(
            views.duplicate_default,
        )
        self.preview_row = to_streamed_response_wrapper(
            views.preview_row,
        )
        self.set_default = to_streamed_response_wrapper(
            views.set_default,
        )
        self.stats = to_streamed_response_wrapper(
            views.stats,
        )
        self.stream_rows = to_custom_streamed_response_wrapper(
            views.stream_rows,
            StreamedBinaryAPIResponse,
        )
        self.update_cells = to_streamed_response_wrapper(
            views.update_cells,
        )

    @cached_property
    def rows(self) -> RowsResourceWithStreamingResponse:
        return RowsResourceWithStreamingResponse(self._views.rows)

    @cached_property
    def columns(self) -> ColumnsResourceWithStreamingResponse:
        return ColumnsResourceWithStreamingResponse(self._views.columns)


class AsyncViewsResourceWithStreamingResponse:
    def __init__(self, views: AsyncViewsResource) -> None:
        self._views = views

        self.create = async_to_streamed_response_wrapper(
            views.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            views.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            views.update,
        )
        self.list = async_to_streamed_response_wrapper(
            views.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            views.delete,
        )
        self.download_csv = async_to_streamed_response_wrapper(
            views.download_csv,
        )
        self.duplicate = async_to_streamed_response_wrapper(
            views.duplicate,
        )
        self.duplicate_default = async_to_streamed_response_wrapper(
            views.duplicate_default,
        )
        self.preview_row = async_to_streamed_response_wrapper(
            views.preview_row,
        )
        self.set_default = async_to_streamed_response_wrapper(
            views.set_default,
        )
        self.stats = async_to_streamed_response_wrapper(
            views.stats,
        )
        self.stream_rows = async_to_custom_streamed_response_wrapper(
            views.stream_rows,
            AsyncStreamedBinaryAPIResponse,
        )
        self.update_cells = async_to_streamed_response_wrapper(
            views.update_cells,
        )

    @cached_property
    def rows(self) -> AsyncRowsResourceWithStreamingResponse:
        return AsyncRowsResourceWithStreamingResponse(self._views.rows)

    @cached_property
    def columns(self) -> AsyncColumnsResourceWithStreamingResponse:
        return AsyncColumnsResourceWithStreamingResponse(self._views.columns)
