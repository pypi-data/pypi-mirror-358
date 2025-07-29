# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from datetime import datetime

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
from ...types.table import row_add_params, row_update_params, row_upsert_params, row_get_rows_params
from ..._base_client import make_request_options
from ...types.table.row_add_response import RowAddResponse
from ...types.table.row_update_response import RowUpdateResponse
from ...types.table.row_upsert_response import RowUpsertResponse
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.table.row_get_rows_response import RowGetRowsResponse
from ...types.table.table_row_action_param import TableRowActionParam

__all__ = ["RowResource", "AsyncRowResource"]


class RowResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RowResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return RowResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RowResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return RowResourceWithStreamingResponse(self)

    def update(
        self,
        table_id: str,
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
        Update existing rows in the specified table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._put(
            f"/v1/table/{table_id}/row",
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

    def add(
        self,
        table_id: str,
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
        Add a new row to the specified table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._post(
            f"/v1/table/{table_id}/row",
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

    def get_rows(
        self,
        table_id: str,
        *,
        columns: List[str] | NotGiven = NOT_GIVEN,
        distinct_columns: List[str] | NotGiven = NOT_GIVEN,
        filter: str | NotGiven = NOT_GIVEN,
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
    ) -> RowGetRowsResponse:
        """
        Retrieve rows from a table based on provided query parameters.

        Args:
          columns: Specific columns to include in the response

          distinct_columns: Columns to apply distinct filtering

          filter: Filter criteria for the table rows

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
            f"/v1/table/{table_id}/row",
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
                        "last_created_at": last_created_at,
                        "last_updated_at": last_updated_at,
                        "next_page_token": next_page_token,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    row_get_rows_params.RowGetRowsParams,
                ),
            ),
            cast_to=RowGetRowsResponse,
        )

    def upsert(
        self,
        table_id: str,
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
        Add or update a row in the specified table based on a unique column value.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._post(
            f"/v1/table/{table_id}/row/upsert",
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


class AsyncRowResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRowResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRowResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRowResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncRowResourceWithStreamingResponse(self)

    async def update(
        self,
        table_id: str,
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
        Update existing rows in the specified table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._put(
            f"/v1/table/{table_id}/row",
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

    async def add(
        self,
        table_id: str,
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
        Add a new row to the specified table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/row",
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

    async def get_rows(
        self,
        table_id: str,
        *,
        columns: List[str] | NotGiven = NOT_GIVEN,
        distinct_columns: List[str] | NotGiven = NOT_GIVEN,
        filter: str | NotGiven = NOT_GIVEN,
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
    ) -> RowGetRowsResponse:
        """
        Retrieve rows from a table based on provided query parameters.

        Args:
          columns: Specific columns to include in the response

          distinct_columns: Columns to apply distinct filtering

          filter: Filter criteria for the table rows

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
            f"/v1/table/{table_id}/row",
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
                        "last_created_at": last_created_at,
                        "last_updated_at": last_updated_at,
                        "next_page_token": next_page_token,
                        "page": page,
                        "size": size,
                        "sort": sort,
                    },
                    row_get_rows_params.RowGetRowsParams,
                ),
            ),
            cast_to=RowGetRowsResponse,
        )

    async def upsert(
        self,
        table_id: str,
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
        Add or update a row in the specified table based on a unique column value.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/row/upsert",
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


class RowResourceWithRawResponse:
    def __init__(self, row: RowResource) -> None:
        self._row = row

        self.update = to_raw_response_wrapper(
            row.update,
        )
        self.add = to_raw_response_wrapper(
            row.add,
        )
        self.get_rows = to_raw_response_wrapper(
            row.get_rows,
        )
        self.upsert = to_raw_response_wrapper(
            row.upsert,
        )


class AsyncRowResourceWithRawResponse:
    def __init__(self, row: AsyncRowResource) -> None:
        self._row = row

        self.update = async_to_raw_response_wrapper(
            row.update,
        )
        self.add = async_to_raw_response_wrapper(
            row.add,
        )
        self.get_rows = async_to_raw_response_wrapper(
            row.get_rows,
        )
        self.upsert = async_to_raw_response_wrapper(
            row.upsert,
        )


class RowResourceWithStreamingResponse:
    def __init__(self, row: RowResource) -> None:
        self._row = row

        self.update = to_streamed_response_wrapper(
            row.update,
        )
        self.add = to_streamed_response_wrapper(
            row.add,
        )
        self.get_rows = to_streamed_response_wrapper(
            row.get_rows,
        )
        self.upsert = to_streamed_response_wrapper(
            row.upsert,
        )


class AsyncRowResourceWithStreamingResponse:
    def __init__(self, row: AsyncRowResource) -> None:
        self._row = row

        self.update = async_to_streamed_response_wrapper(
            row.update,
        )
        self.add = async_to_streamed_response_wrapper(
            row.add,
        )
        self.get_rows = async_to_streamed_response_wrapper(
            row.get_rows,
        )
        self.upsert = async_to_streamed_response_wrapper(
            row.upsert,
        )
