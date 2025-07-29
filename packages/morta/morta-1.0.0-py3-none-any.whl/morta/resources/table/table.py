# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from .row import (
    RowResource,
    AsyncRowResource,
    RowResourceWithRawResponse,
    AsyncRowResourceWithRawResponse,
    RowResourceWithStreamingResponse,
    AsyncRowResourceWithStreamingResponse,
)
from .join import (
    JoinResource,
    AsyncJoinResource,
    JoinResourceWithRawResponse,
    AsyncJoinResourceWithRawResponse,
    JoinResourceWithStreamingResponse,
    AsyncJoinResourceWithStreamingResponse,
)
from .sync import (
    SyncResource,
    AsyncSyncResource,
    SyncResourceWithRawResponse,
    AsyncSyncResourceWithRawResponse,
    SyncResourceWithStreamingResponse,
    AsyncSyncResourceWithStreamingResponse,
)
from .column import (
    ColumnResource,
    AsyncColumnResource,
    ColumnResourceWithRawResponse,
    AsyncColumnResourceWithRawResponse,
    ColumnResourceWithStreamingResponse,
    AsyncColumnResourceWithStreamingResponse,
)
from ...types import (
    table_create_params,
    table_update_params,
    table_get_file_params,
    table_retrieve_params,
    table_duplicate_params,
    table_stream_rows_params,
    table_create_index_params,
    table_download_csv_params,
    table_update_cells_params,
    table_get_statistics_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
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
from .views.views import (
    ViewsResource,
    AsyncViewsResource,
    ViewsResourceWithRawResponse,
    AsyncViewsResourceWithRawResponse,
    ViewsResourceWithStreamingResponse,
    AsyncViewsResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from ...types.table_create_response import TableCreateResponse
from ...types.table_delete_response import TableDeleteResponse
from ...types.table_update_response import TableUpdateResponse
from ...types.table_restore_response import TableRestoreResponse
from ...types.table_retrieve_response import TableRetrieveResponse
from ...types.table_truncate_response import TableTruncateResponse
from ...types.table.table_column_param import TableColumnParam
from ...types.table_duplicate_response import TableDuplicateResponse
from ...types.table_list_joins_response import TableListJoinsResponse
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.table_check_usage_response import TableCheckUsageResponse
from ...types.table_delete_rows_response import TableDeleteRowsResponse
from ...types.table_create_index_response import TableCreateIndexResponse
from ...types.table_list_columns_response import TableListColumnsResponse
from ...types.table_update_cells_response import TableUpdateCellsResponse
from ...types.table_get_statistics_response import TableGetStatisticsResponse
from ...types.table_get_duplicated_children_response import TableGetDuplicatedChildrenResponse

__all__ = ["TableResource", "AsyncTableResource"]


class TableResource(SyncAPIResource):
    @cached_property
    def column(self) -> ColumnResource:
        return ColumnResource(self._client)

    @cached_property
    def row(self) -> RowResource:
        return RowResource(self._client)

    @cached_property
    def join(self) -> JoinResource:
        return JoinResource(self._client)

    @cached_property
    def sync(self) -> SyncResource:
        return SyncResource(self._client)

    @cached_property
    def views(self) -> ViewsResource:
        return ViewsResource(self._client)

    @cached_property
    def with_raw_response(self) -> TableResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return TableResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TableResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return TableResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        columns: Iterable[TableColumnParam],
        name: str,
        project_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        joins: Iterable[table_create_params.Join] | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableCreateResponse:
        """
        Create a new document table within a hub.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/table",
            body=maybe_transform(
                {
                    "columns": columns,
                    "name": name,
                    "project_id": project_id,
                    "context": context,
                    "joins": joins,
                    "type": type,
                },
                table_create_params.TableCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableCreateResponse,
        )

    def retrieve(
        self,
        table_id: str,
        *,
        columns: List[str] | NotGiven = NOT_GIVEN,
        distinct_columns: List[str] | NotGiven = NOT_GIVEN,
        filter: str | NotGiven = NOT_GIVEN,
        ignore_cached_options: bool | NotGiven = NOT_GIVEN,
        last_created_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        next_page_token: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableRetrieveResponse:
        """
        Retrieve a table and its rows based on provided parameters

        Args:
          columns: Specific columns to include in the response

          distinct_columns: Columns to apply distinct filtering

          filter: Filter criteria for the table rows

          ignore_cached_options: Flag to indicate whether to ignore cached options in the response.

          last_created_at: Filter for rows created after this date

          last_updated_at: Filter for rows updated after this date

          next_page_token: Token for fetching the next page of results

          page: Page number for pagination

          size: Number of items per page for pagination

          sort: Sorting criteria for the table rows

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "columns": columns,
                        "distinct_columns": distinct_columns,
                        "filter": filter,
                        "ignore_cached_options": ignore_cached_options,
                        "last_created_at": last_created_at,
                        "last_updated_at": last_updated_at,
                        "next_page_token": next_page_token,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    table_retrieve_params.TableRetrieveParams,
                ),
            ),
            cast_to=TableRetrieveResponse,
        )

    def update(
        self,
        table_id: str,
        *,
        allow_comments: bool | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        is_reference_table: bool | NotGiven = NOT_GIVEN,
        joins: Iterable[table_update_params.Join] | NotGiven = NOT_GIVEN,
        keep_colours_in_sync: bool | NotGiven = NOT_GIVEN,
        keep_validations_in_sync: bool | NotGiven = NOT_GIVEN,
        logo: Optional[str] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        sync_hourly_frequency: Literal[0, 24] | NotGiven = NOT_GIVEN,
        type: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableUpdateResponse:
        """
        Update the properties of an existing table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._put(
            f"/v1/table/{table_id}",
            body=maybe_transform(
                {
                    "allow_comments": allow_comments,
                    "context": context,
                    "is_reference_table": is_reference_table,
                    "joins": joins,
                    "keep_colours_in_sync": keep_colours_in_sync,
                    "keep_validations_in_sync": keep_validations_in_sync,
                    "logo": logo,
                    "name": name,
                    "sync_hourly_frequency": sync_hourly_frequency,
                    "type": type,
                },
                table_update_params.TableUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableUpdateResponse,
        )

    def delete(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableDeleteResponse:
        """
        Delete a specified table by its UUID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._delete(
            f"/v1/table/{table_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableDeleteResponse,
        )

    def check_usage(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableCheckUsageResponse:
        """
        Check and return a list of documents, table joins, and selects where the
        specified table is used.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/used",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableCheckUsageResponse,
        )

    def create_index(
        self,
        table_id: str,
        *,
        columns: Iterable[table_create_index_params.Column],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableCreateIndexResponse:
        """
        Create an index on one or more columns of a table to improve query performance.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._post(
            f"/v1/table/{table_id}/indexes",
            body=maybe_transform({"columns": columns}, table_create_index_params.TableCreateIndexParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableCreateIndexResponse,
        )

    def delete_rows(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableDeleteRowsResponse:
        """
        Delete all rows or specific rows from a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._delete(
            f"/v1/table/{table_id}/rows",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableDeleteRowsResponse,
        )

    def download_csv(
        self,
        table_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Download the data of a specified table as a CSV file.

        Args:
          filter: Filter criteria for the table rows

          sort: Sorting criteria for the table rows

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return self._get(
            f"/v1/table/{table_id}/csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "sort": sort,
                    },
                    table_download_csv_params.TableDownloadCsvParams,
                ),
            ),
            cast_to=str,
        )

    def duplicate(
        self,
        table_id: str,
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
    ) -> TableDuplicateResponse:
        """
        Create a duplicate of an existing table along with its data, settings, and
        optionally linked tables.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._post(
            f"/v1/table/{table_id}/duplicate",
            body=maybe_transform(
                {
                    "target_project_id": target_project_id,
                    "context": context,
                    "duplicate_linked_tables": duplicate_linked_tables,
                    "duplicate_permissions": duplicate_permissions,
                },
                table_duplicate_params.TableDuplicateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableDuplicateResponse,
        )

    def get_csv_backup(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Get a CSV backup of a table at a specific date

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._get(
            f"/v1/table/{table_id}/csv-backup",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def get_duplicated_children(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableGetDuplicatedChildrenResponse:
        """
        Get duplicated children of a table

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/duplicated-children",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableGetDuplicatedChildrenResponse,
        )

    def get_file(
        self,
        table_id: str,
        *,
        column_id: str,
        filename: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Retrieve a file associated with a specific cell in a table.

        Args:
          column_id: UUID of the column containing the cell.

          filename: Name of the file to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._get(
            f"/v1/table/{table_id}/file",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "column_id": column_id,
                        "filename": filename,
                    },
                    table_get_file_params.TableGetFileParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def get_statistics(
        self,
        table_id: str,
        *,
        aggregation: Dict[str, str] | NotGiven = NOT_GIVEN,
        filter: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableGetStatisticsResponse:
        """
        Retrieve statistics for table columns based on specified parameters.

        Args:
          aggregation: Aggregation functions to apply on columns

          filter: Filter criteria for the columns

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "aggregation": aggregation,
                        "filter": filter,
                    },
                    table_get_statistics_params.TableGetStatisticsParams,
                ),
            ),
            cast_to=TableGetStatisticsResponse,
        )

    def list_columns(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableListColumnsResponse:
        """
        Retrieve all active columns of a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/columns",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableListColumnsResponse,
        )

    def list_joins(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableListJoinsResponse:
        """
        Retrieve all joins associated with a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._get(
            f"/v1/table/{table_id}/joins",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableListJoinsResponse,
        )

    def restore(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableRestoreResponse:
        """
        Restore a previously deleted table using its UUID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._put(
            f"/v1/table/{table_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableRestoreResponse,
        )

    def stream_rows(
        self,
        table_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
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
        Stream the data of all rows for a specific table.

        Args:
          filter: Filters to apply to the streaming data.

          page: Page number for pagination

          size: Number of items per page for pagination

          sort: Sorting parameters for the streaming data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "application/x-msgppack", **(extra_headers or {})}
        return self._get(
            f"/v1/table/{table_id}/rows-stream",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    table_stream_rows_params.TableStreamRowsParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def truncate(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableTruncateResponse:
        """
        Deletes all rows from the specified table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._delete(
            f"/v1/table/{table_id}/truncate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableTruncateResponse,
        )

    def update_cells(
        self,
        table_id: str,
        *,
        cells: Iterable[table_update_cells_params.Cell],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableUpdateCellsResponse:
        """
        Update specific cells in a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._put(
            f"/v1/table/{table_id}/cells",
            body=maybe_transform(
                {
                    "cells": cells,
                    "context": context,
                },
                table_update_cells_params.TableUpdateCellsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableUpdateCellsResponse,
        )


class AsyncTableResource(AsyncAPIResource):
    @cached_property
    def column(self) -> AsyncColumnResource:
        return AsyncColumnResource(self._client)

    @cached_property
    def row(self) -> AsyncRowResource:
        return AsyncRowResource(self._client)

    @cached_property
    def join(self) -> AsyncJoinResource:
        return AsyncJoinResource(self._client)

    @cached_property
    def sync(self) -> AsyncSyncResource:
        return AsyncSyncResource(self._client)

    @cached_property
    def views(self) -> AsyncViewsResource:
        return AsyncViewsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTableResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTableResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTableResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncTableResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        columns: Iterable[TableColumnParam],
        name: str,
        project_id: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        joins: Iterable[table_create_params.Join] | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableCreateResponse:
        """
        Create a new document table within a hub.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/table",
            body=await async_maybe_transform(
                {
                    "columns": columns,
                    "name": name,
                    "project_id": project_id,
                    "context": context,
                    "joins": joins,
                    "type": type,
                },
                table_create_params.TableCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableCreateResponse,
        )

    async def retrieve(
        self,
        table_id: str,
        *,
        columns: List[str] | NotGiven = NOT_GIVEN,
        distinct_columns: List[str] | NotGiven = NOT_GIVEN,
        filter: str | NotGiven = NOT_GIVEN,
        ignore_cached_options: bool | NotGiven = NOT_GIVEN,
        last_created_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        next_page_token: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableRetrieveResponse:
        """
        Retrieve a table and its rows based on provided parameters

        Args:
          columns: Specific columns to include in the response

          distinct_columns: Columns to apply distinct filtering

          filter: Filter criteria for the table rows

          ignore_cached_options: Flag to indicate whether to ignore cached options in the response.

          last_created_at: Filter for rows created after this date

          last_updated_at: Filter for rows updated after this date

          next_page_token: Token for fetching the next page of results

          page: Page number for pagination

          size: Number of items per page for pagination

          sort: Sorting criteria for the table rows

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "columns": columns,
                        "distinct_columns": distinct_columns,
                        "filter": filter,
                        "ignore_cached_options": ignore_cached_options,
                        "last_created_at": last_created_at,
                        "last_updated_at": last_updated_at,
                        "next_page_token": next_page_token,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    table_retrieve_params.TableRetrieveParams,
                ),
            ),
            cast_to=TableRetrieveResponse,
        )

    async def update(
        self,
        table_id: str,
        *,
        allow_comments: bool | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        is_reference_table: bool | NotGiven = NOT_GIVEN,
        joins: Iterable[table_update_params.Join] | NotGiven = NOT_GIVEN,
        keep_colours_in_sync: bool | NotGiven = NOT_GIVEN,
        keep_validations_in_sync: bool | NotGiven = NOT_GIVEN,
        logo: Optional[str] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        sync_hourly_frequency: Literal[0, 24] | NotGiven = NOT_GIVEN,
        type: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableUpdateResponse:
        """
        Update the properties of an existing table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._put(
            f"/v1/table/{table_id}",
            body=await async_maybe_transform(
                {
                    "allow_comments": allow_comments,
                    "context": context,
                    "is_reference_table": is_reference_table,
                    "joins": joins,
                    "keep_colours_in_sync": keep_colours_in_sync,
                    "keep_validations_in_sync": keep_validations_in_sync,
                    "logo": logo,
                    "name": name,
                    "sync_hourly_frequency": sync_hourly_frequency,
                    "type": type,
                },
                table_update_params.TableUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableUpdateResponse,
        )

    async def delete(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableDeleteResponse:
        """
        Delete a specified table by its UUID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._delete(
            f"/v1/table/{table_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableDeleteResponse,
        )

    async def check_usage(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableCheckUsageResponse:
        """
        Check and return a list of documents, table joins, and selects where the
        specified table is used.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/used",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableCheckUsageResponse,
        )

    async def create_index(
        self,
        table_id: str,
        *,
        columns: Iterable[table_create_index_params.Column],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableCreateIndexResponse:
        """
        Create an index on one or more columns of a table to improve query performance.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/indexes",
            body=await async_maybe_transform({"columns": columns}, table_create_index_params.TableCreateIndexParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableCreateIndexResponse,
        )

    async def delete_rows(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableDeleteRowsResponse:
        """
        Delete all rows or specific rows from a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._delete(
            f"/v1/table/{table_id}/rows",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableDeleteRowsResponse,
        )

    async def download_csv(
        self,
        table_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        sort: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Download the data of a specified table as a CSV file.

        Args:
          filter: Filter criteria for the table rows

          sort: Sorting criteria for the table rows

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return await self._get(
            f"/v1/table/{table_id}/csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "sort": sort,
                    },
                    table_download_csv_params.TableDownloadCsvParams,
                ),
            ),
            cast_to=str,
        )

    async def duplicate(
        self,
        table_id: str,
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
    ) -> TableDuplicateResponse:
        """
        Create a duplicate of an existing table along with its data, settings, and
        optionally linked tables.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/duplicate",
            body=await async_maybe_transform(
                {
                    "target_project_id": target_project_id,
                    "context": context,
                    "duplicate_linked_tables": duplicate_linked_tables,
                    "duplicate_permissions": duplicate_permissions,
                },
                table_duplicate_params.TableDuplicateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableDuplicateResponse,
        )

    async def get_csv_backup(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Get a CSV backup of a table at a specific date

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._get(
            f"/v1/table/{table_id}/csv-backup",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def get_duplicated_children(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableGetDuplicatedChildrenResponse:
        """
        Get duplicated children of a table

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/duplicated-children",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableGetDuplicatedChildrenResponse,
        )

    async def get_file(
        self,
        table_id: str,
        *,
        column_id: str,
        filename: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Retrieve a file associated with a specific cell in a table.

        Args:
          column_id: UUID of the column containing the cell.

          filename: Name of the file to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._get(
            f"/v1/table/{table_id}/file",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "column_id": column_id,
                        "filename": filename,
                    },
                    table_get_file_params.TableGetFileParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def get_statistics(
        self,
        table_id: str,
        *,
        aggregation: Dict[str, str] | NotGiven = NOT_GIVEN,
        filter: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableGetStatisticsResponse:
        """
        Retrieve statistics for table columns based on specified parameters.

        Args:
          aggregation: Aggregation functions to apply on columns

          filter: Filter criteria for the columns

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "aggregation": aggregation,
                        "filter": filter,
                    },
                    table_get_statistics_params.TableGetStatisticsParams,
                ),
            ),
            cast_to=TableGetStatisticsResponse,
        )

    async def list_columns(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableListColumnsResponse:
        """
        Retrieve all active columns of a specific table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/columns",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableListColumnsResponse,
        )

    async def list_joins(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableListJoinsResponse:
        """
        Retrieve all joins associated with a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/joins",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableListJoinsResponse,
        )

    async def restore(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableRestoreResponse:
        """
        Restore a previously deleted table using its UUID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._put(
            f"/v1/table/{table_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableRestoreResponse,
        )

    async def stream_rows(
        self,
        table_id: str,
        *,
        filter: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
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
        Stream the data of all rows for a specific table.

        Args:
          filter: Filters to apply to the streaming data.

          page: Page number for pagination

          size: Number of items per page for pagination

          sort: Sorting parameters for the streaming data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        extra_headers = {"Accept": "application/x-msgppack", **(extra_headers or {})}
        return await self._get(
            f"/v1/table/{table_id}/rows-stream",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    table_stream_rows_params.TableStreamRowsParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def truncate(
        self,
        table_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableTruncateResponse:
        """
        Deletes all rows from the specified table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._delete(
            f"/v1/table/{table_id}/truncate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableTruncateResponse,
        )

    async def update_cells(
        self,
        table_id: str,
        *,
        cells: Iterable[table_update_cells_params.Cell],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TableUpdateCellsResponse:
        """
        Update specific cells in a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._put(
            f"/v1/table/{table_id}/cells",
            body=await async_maybe_transform(
                {
                    "cells": cells,
                    "context": context,
                },
                table_update_cells_params.TableUpdateCellsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TableUpdateCellsResponse,
        )


class TableResourceWithRawResponse:
    def __init__(self, table: TableResource) -> None:
        self._table = table

        self.create = to_raw_response_wrapper(
            table.create,
        )
        self.retrieve = to_raw_response_wrapper(
            table.retrieve,
        )
        self.update = to_raw_response_wrapper(
            table.update,
        )
        self.delete = to_raw_response_wrapper(
            table.delete,
        )
        self.check_usage = to_raw_response_wrapper(
            table.check_usage,
        )
        self.create_index = to_raw_response_wrapper(
            table.create_index,
        )
        self.delete_rows = to_raw_response_wrapper(
            table.delete_rows,
        )
        self.download_csv = to_raw_response_wrapper(
            table.download_csv,
        )
        self.duplicate = to_raw_response_wrapper(
            table.duplicate,
        )
        self.get_csv_backup = to_custom_raw_response_wrapper(
            table.get_csv_backup,
            BinaryAPIResponse,
        )
        self.get_duplicated_children = to_raw_response_wrapper(
            table.get_duplicated_children,
        )
        self.get_file = to_custom_raw_response_wrapper(
            table.get_file,
            BinaryAPIResponse,
        )
        self.get_statistics = to_raw_response_wrapper(
            table.get_statistics,
        )
        self.list_columns = to_raw_response_wrapper(
            table.list_columns,
        )
        self.list_joins = to_raw_response_wrapper(
            table.list_joins,
        )
        self.restore = to_raw_response_wrapper(
            table.restore,
        )
        self.stream_rows = to_custom_raw_response_wrapper(
            table.stream_rows,
            BinaryAPIResponse,
        )
        self.truncate = to_raw_response_wrapper(
            table.truncate,
        )
        self.update_cells = to_raw_response_wrapper(
            table.update_cells,
        )

    @cached_property
    def column(self) -> ColumnResourceWithRawResponse:
        return ColumnResourceWithRawResponse(self._table.column)

    @cached_property
    def row(self) -> RowResourceWithRawResponse:
        return RowResourceWithRawResponse(self._table.row)

    @cached_property
    def join(self) -> JoinResourceWithRawResponse:
        return JoinResourceWithRawResponse(self._table.join)

    @cached_property
    def sync(self) -> SyncResourceWithRawResponse:
        return SyncResourceWithRawResponse(self._table.sync)

    @cached_property
    def views(self) -> ViewsResourceWithRawResponse:
        return ViewsResourceWithRawResponse(self._table.views)


class AsyncTableResourceWithRawResponse:
    def __init__(self, table: AsyncTableResource) -> None:
        self._table = table

        self.create = async_to_raw_response_wrapper(
            table.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            table.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            table.update,
        )
        self.delete = async_to_raw_response_wrapper(
            table.delete,
        )
        self.check_usage = async_to_raw_response_wrapper(
            table.check_usage,
        )
        self.create_index = async_to_raw_response_wrapper(
            table.create_index,
        )
        self.delete_rows = async_to_raw_response_wrapper(
            table.delete_rows,
        )
        self.download_csv = async_to_raw_response_wrapper(
            table.download_csv,
        )
        self.duplicate = async_to_raw_response_wrapper(
            table.duplicate,
        )
        self.get_csv_backup = async_to_custom_raw_response_wrapper(
            table.get_csv_backup,
            AsyncBinaryAPIResponse,
        )
        self.get_duplicated_children = async_to_raw_response_wrapper(
            table.get_duplicated_children,
        )
        self.get_file = async_to_custom_raw_response_wrapper(
            table.get_file,
            AsyncBinaryAPIResponse,
        )
        self.get_statistics = async_to_raw_response_wrapper(
            table.get_statistics,
        )
        self.list_columns = async_to_raw_response_wrapper(
            table.list_columns,
        )
        self.list_joins = async_to_raw_response_wrapper(
            table.list_joins,
        )
        self.restore = async_to_raw_response_wrapper(
            table.restore,
        )
        self.stream_rows = async_to_custom_raw_response_wrapper(
            table.stream_rows,
            AsyncBinaryAPIResponse,
        )
        self.truncate = async_to_raw_response_wrapper(
            table.truncate,
        )
        self.update_cells = async_to_raw_response_wrapper(
            table.update_cells,
        )

    @cached_property
    def column(self) -> AsyncColumnResourceWithRawResponse:
        return AsyncColumnResourceWithRawResponse(self._table.column)

    @cached_property
    def row(self) -> AsyncRowResourceWithRawResponse:
        return AsyncRowResourceWithRawResponse(self._table.row)

    @cached_property
    def join(self) -> AsyncJoinResourceWithRawResponse:
        return AsyncJoinResourceWithRawResponse(self._table.join)

    @cached_property
    def sync(self) -> AsyncSyncResourceWithRawResponse:
        return AsyncSyncResourceWithRawResponse(self._table.sync)

    @cached_property
    def views(self) -> AsyncViewsResourceWithRawResponse:
        return AsyncViewsResourceWithRawResponse(self._table.views)


class TableResourceWithStreamingResponse:
    def __init__(self, table: TableResource) -> None:
        self._table = table

        self.create = to_streamed_response_wrapper(
            table.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            table.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            table.update,
        )
        self.delete = to_streamed_response_wrapper(
            table.delete,
        )
        self.check_usage = to_streamed_response_wrapper(
            table.check_usage,
        )
        self.create_index = to_streamed_response_wrapper(
            table.create_index,
        )
        self.delete_rows = to_streamed_response_wrapper(
            table.delete_rows,
        )
        self.download_csv = to_streamed_response_wrapper(
            table.download_csv,
        )
        self.duplicate = to_streamed_response_wrapper(
            table.duplicate,
        )
        self.get_csv_backup = to_custom_streamed_response_wrapper(
            table.get_csv_backup,
            StreamedBinaryAPIResponse,
        )
        self.get_duplicated_children = to_streamed_response_wrapper(
            table.get_duplicated_children,
        )
        self.get_file = to_custom_streamed_response_wrapper(
            table.get_file,
            StreamedBinaryAPIResponse,
        )
        self.get_statistics = to_streamed_response_wrapper(
            table.get_statistics,
        )
        self.list_columns = to_streamed_response_wrapper(
            table.list_columns,
        )
        self.list_joins = to_streamed_response_wrapper(
            table.list_joins,
        )
        self.restore = to_streamed_response_wrapper(
            table.restore,
        )
        self.stream_rows = to_custom_streamed_response_wrapper(
            table.stream_rows,
            StreamedBinaryAPIResponse,
        )
        self.truncate = to_streamed_response_wrapper(
            table.truncate,
        )
        self.update_cells = to_streamed_response_wrapper(
            table.update_cells,
        )

    @cached_property
    def column(self) -> ColumnResourceWithStreamingResponse:
        return ColumnResourceWithStreamingResponse(self._table.column)

    @cached_property
    def row(self) -> RowResourceWithStreamingResponse:
        return RowResourceWithStreamingResponse(self._table.row)

    @cached_property
    def join(self) -> JoinResourceWithStreamingResponse:
        return JoinResourceWithStreamingResponse(self._table.join)

    @cached_property
    def sync(self) -> SyncResourceWithStreamingResponse:
        return SyncResourceWithStreamingResponse(self._table.sync)

    @cached_property
    def views(self) -> ViewsResourceWithStreamingResponse:
        return ViewsResourceWithStreamingResponse(self._table.views)


class AsyncTableResourceWithStreamingResponse:
    def __init__(self, table: AsyncTableResource) -> None:
        self._table = table

        self.create = async_to_streamed_response_wrapper(
            table.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            table.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            table.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            table.delete,
        )
        self.check_usage = async_to_streamed_response_wrapper(
            table.check_usage,
        )
        self.create_index = async_to_streamed_response_wrapper(
            table.create_index,
        )
        self.delete_rows = async_to_streamed_response_wrapper(
            table.delete_rows,
        )
        self.download_csv = async_to_streamed_response_wrapper(
            table.download_csv,
        )
        self.duplicate = async_to_streamed_response_wrapper(
            table.duplicate,
        )
        self.get_csv_backup = async_to_custom_streamed_response_wrapper(
            table.get_csv_backup,
            AsyncStreamedBinaryAPIResponse,
        )
        self.get_duplicated_children = async_to_streamed_response_wrapper(
            table.get_duplicated_children,
        )
        self.get_file = async_to_custom_streamed_response_wrapper(
            table.get_file,
            AsyncStreamedBinaryAPIResponse,
        )
        self.get_statistics = async_to_streamed_response_wrapper(
            table.get_statistics,
        )
        self.list_columns = async_to_streamed_response_wrapper(
            table.list_columns,
        )
        self.list_joins = async_to_streamed_response_wrapper(
            table.list_joins,
        )
        self.restore = async_to_streamed_response_wrapper(
            table.restore,
        )
        self.stream_rows = async_to_custom_streamed_response_wrapper(
            table.stream_rows,
            AsyncStreamedBinaryAPIResponse,
        )
        self.truncate = async_to_streamed_response_wrapper(
            table.truncate,
        )
        self.update_cells = async_to_streamed_response_wrapper(
            table.update_cells,
        )

    @cached_property
    def column(self) -> AsyncColumnResourceWithStreamingResponse:
        return AsyncColumnResourceWithStreamingResponse(self._table.column)

    @cached_property
    def row(self) -> AsyncRowResourceWithStreamingResponse:
        return AsyncRowResourceWithStreamingResponse(self._table.row)

    @cached_property
    def join(self) -> AsyncJoinResourceWithStreamingResponse:
        return AsyncJoinResourceWithStreamingResponse(self._table.join)

    @cached_property
    def sync(self) -> AsyncSyncResourceWithStreamingResponse:
        return AsyncSyncResourceWithStreamingResponse(self._table.sync)

    @cached_property
    def views(self) -> AsyncViewsResourceWithStreamingResponse:
        return AsyncViewsResourceWithStreamingResponse(self._table.views)
