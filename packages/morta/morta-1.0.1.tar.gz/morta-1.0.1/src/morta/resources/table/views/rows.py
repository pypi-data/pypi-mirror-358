# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ....types.table.views import row_add_params, row_list_params, row_update_params, row_upsert_params
from ....types.base_request_context_param import BaseRequestContextParam
from ....types.table.table_row_action_param import TableRowActionParam
from ....types.table.views.row_add_response import RowAddResponse
from ....types.table.views.row_list_response import RowListResponse
from ....types.table.views.row_delete_response import RowDeleteResponse
from ....types.table.views.row_update_response import RowUpdateResponse
from ....types.table.views.row_upsert_response import RowUpsertResponse

__all__ = ["RowsResource", "AsyncRowsResource"]


class RowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return RowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return RowsResourceWithStreamingResponse(self)

    def update(
        self,
        view_id: str,
        *,
        rows: Iterable[row_update_params.Row],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowUpdateResponse:
        """
        Update existing rows in a specified table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._put(
            f"/v1/table/views/{view_id}/rows",
            body=maybe_transform(
                {
                    "rows": rows,
                    "context": context,
                },
                row_update_params.RowUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowUpdateResponse,
        )

    def list(
        self,
        view_id: str,
        *,
        alphabetical_column_sort: bool | NotGiven = NOT_GIVEN,
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
    ) -> RowListResponse:
        """
        Retrieve the actual data for a specific table view.

        Args:
          alphabetical_column_sort: If true, columns in row data are sorted alphabetically otherwise columns in row
              data follows their order in the view.

          filter: URL encoded JSON string of filter criteria (e.g.
              'filter=%7B%22columnName%22%3A%22Price%22%2C%22value%22%3A%22100%22%2C%22filterType%22%3A%22gt%22%7D')

          page: Page number for pagination.

          size: Number of items per page for pagination.

          sort: Sort the results by a field, this parameter takes the form
              `ColumnName:SortDirection`, for example to sort by price ascending
              `sort=Price:asc`. Sort direction can be either `asc` or `desc`. You can pass
              multiple sort parameters to add secondary and tertiary sorts etc., the sort will
              be applied in the order of the query string.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._get(
            f"/v1/table/views/{view_id}/rows",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "alphabetical_column_sort": alphabetical_column_sort,
                        "filter": filter,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    row_list_params.RowListParams,
                ),
            ),
            cast_to=RowListResponse,
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
    ) -> RowDeleteResponse:
        """
        Delete specific rows from a table view based on row IDs.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._delete(
            f"/v1/table/views/{view_id}/rows",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowDeleteResponse,
        )

    def add(
        self,
        view_id: str,
        *,
        rows: Iterable[TableRowActionParam],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowAddResponse:
        """
        Insert new rows at the end of the specified table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._post(
            f"/v1/table/views/{view_id}/rows",
            body=maybe_transform(
                {
                    "rows": rows,
                    "context": context,
                },
                row_add_params.RowAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowAddResponse,
        )

    def upsert(
        self,
        view_id: str,
        *,
        rows: Iterable[TableRowActionParam],
        upsert_column_name: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowUpsertResponse:
        """
        Upsert (add or update) rows in a table view based on a specified column.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return self._post(
            f"/v1/table/views/{view_id}/rows/upsert",
            body=maybe_transform(
                {
                    "rows": rows,
                    "upsert_column_name": upsert_column_name,
                    "context": context,
                },
                row_upsert_params.RowUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowUpsertResponse,
        )


class AsyncRowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncRowsResourceWithStreamingResponse(self)

    async def update(
        self,
        view_id: str,
        *,
        rows: Iterable[row_update_params.Row],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowUpdateResponse:
        """
        Update existing rows in a specified table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._put(
            f"/v1/table/views/{view_id}/rows",
            body=await async_maybe_transform(
                {
                    "rows": rows,
                    "context": context,
                },
                row_update_params.RowUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowUpdateResponse,
        )

    async def list(
        self,
        view_id: str,
        *,
        alphabetical_column_sort: bool | NotGiven = NOT_GIVEN,
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
    ) -> RowListResponse:
        """
        Retrieve the actual data for a specific table view.

        Args:
          alphabetical_column_sort: If true, columns in row data are sorted alphabetically otherwise columns in row
              data follows their order in the view.

          filter: URL encoded JSON string of filter criteria (e.g.
              'filter=%7B%22columnName%22%3A%22Price%22%2C%22value%22%3A%22100%22%2C%22filterType%22%3A%22gt%22%7D')

          page: Page number for pagination.

          size: Number of items per page for pagination.

          sort: Sort the results by a field, this parameter takes the form
              `ColumnName:SortDirection`, for example to sort by price ascending
              `sort=Price:asc`. Sort direction can be either `asc` or `desc`. You can pass
              multiple sort parameters to add secondary and tertiary sorts etc., the sort will
              be applied in the order of the query string.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._get(
            f"/v1/table/views/{view_id}/rows",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "alphabetical_column_sort": alphabetical_column_sort,
                        "filter": filter,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    row_list_params.RowListParams,
                ),
            ),
            cast_to=RowListResponse,
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
    ) -> RowDeleteResponse:
        """
        Delete specific rows from a table view based on row IDs.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._delete(
            f"/v1/table/views/{view_id}/rows",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowDeleteResponse,
        )

    async def add(
        self,
        view_id: str,
        *,
        rows: Iterable[TableRowActionParam],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowAddResponse:
        """
        Insert new rows at the end of the specified table view.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._post(
            f"/v1/table/views/{view_id}/rows",
            body=await async_maybe_transform(
                {
                    "rows": rows,
                    "context": context,
                },
                row_add_params.RowAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowAddResponse,
        )

    async def upsert(
        self,
        view_id: str,
        *,
        rows: Iterable[TableRowActionParam],
        upsert_column_name: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowUpsertResponse:
        """
        Upsert (add or update) rows in a table view based on a specified column.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not view_id:
            raise ValueError(f"Expected a non-empty value for `view_id` but received {view_id!r}")
        return await self._post(
            f"/v1/table/views/{view_id}/rows/upsert",
            body=await async_maybe_transform(
                {
                    "rows": rows,
                    "upsert_column_name": upsert_column_name,
                    "context": context,
                },
                row_upsert_params.RowUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowUpsertResponse,
        )


class RowsResourceWithRawResponse:
    def __init__(self, rows: RowsResource) -> None:
        self._rows = rows

        self.update = to_raw_response_wrapper(
            rows.update,
        )
        self.list = to_raw_response_wrapper(
            rows.list,
        )
        self.delete = to_raw_response_wrapper(
            rows.delete,
        )
        self.add = to_raw_response_wrapper(
            rows.add,
        )
        self.upsert = to_raw_response_wrapper(
            rows.upsert,
        )


class AsyncRowsResourceWithRawResponse:
    def __init__(self, rows: AsyncRowsResource) -> None:
        self._rows = rows

        self.update = async_to_raw_response_wrapper(
            rows.update,
        )
        self.list = async_to_raw_response_wrapper(
            rows.list,
        )
        self.delete = async_to_raw_response_wrapper(
            rows.delete,
        )
        self.add = async_to_raw_response_wrapper(
            rows.add,
        )
        self.upsert = async_to_raw_response_wrapper(
            rows.upsert,
        )


class RowsResourceWithStreamingResponse:
    def __init__(self, rows: RowsResource) -> None:
        self._rows = rows

        self.update = to_streamed_response_wrapper(
            rows.update,
        )
        self.list = to_streamed_response_wrapper(
            rows.list,
        )
        self.delete = to_streamed_response_wrapper(
            rows.delete,
        )
        self.add = to_streamed_response_wrapper(
            rows.add,
        )
        self.upsert = to_streamed_response_wrapper(
            rows.upsert,
        )


class AsyncRowsResourceWithStreamingResponse:
    def __init__(self, rows: AsyncRowsResource) -> None:
        self._rows = rows

        self.update = async_to_streamed_response_wrapper(
            rows.update,
        )
        self.list = async_to_streamed_response_wrapper(
            rows.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            rows.delete,
        )
        self.add = async_to_streamed_response_wrapper(
            rows.add,
        )
        self.upsert = async_to_streamed_response_wrapper(
            rows.upsert,
        )
