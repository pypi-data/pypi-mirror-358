# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
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
from ...types.table import (
    column_create_params,
    column_update_params,
    column_get_distinct_values_params,
)
from ..._base_client import make_request_options
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.table.column_create_response import ColumnCreateResponse
from ...types.table.column_delete_response import ColumnDeleteResponse
from ...types.table.column_update_response import ColumnUpdateResponse
from ...types.table.column_restore_response import ColumnRestoreResponse
from ...types.table.column_check_views_response import ColumnCheckViewsResponse
from ...types.table.select_options_lookup_param import SelectOptionsLookupParam
from ...types.table.column_get_distinct_values_response import ColumnGetDistinctValuesResponse

__all__ = ["ColumnResource", "AsyncColumnResource"]


class ColumnResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ColumnResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return ColumnResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ColumnResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return ColumnResourceWithStreamingResponse(self)

    def create(
        self,
        table_id: str,
        *,
        aconex_synced: int | NotGiven = NOT_GIVEN,
        aconex_workflows_synced: int | NotGiven = NOT_GIVEN,
        aggregate: int | NotGiven = NOT_GIVEN,
        alter_options: column_create_params.AlterOptions | NotGiven = NOT_GIVEN,
        asite_documents_synced: int | NotGiven = NOT_GIVEN,
        asite_forms_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_checklists_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_issues_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_models_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_users_synced: int | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        date_format: Optional[str] | NotGiven = NOT_GIVEN,
        decimal_places: int | NotGiven = NOT_GIVEN,
        description: column_create_params.Description | NotGiven = NOT_GIVEN,
        display_link: bool | NotGiven = NOT_GIVEN,
        export_width: Optional[int] | NotGiven = NOT_GIVEN,
        formula: Optional[str] | NotGiven = NOT_GIVEN,
        formula_enabled: bool | NotGiven = NOT_GIVEN,
        header_background_color: Optional[str] | NotGiven = NOT_GIVEN,
        header_text_color: Optional[str] | NotGiven = NOT_GIVEN,
        is_indexed: bool | NotGiven = NOT_GIVEN,
        is_joined: Optional[bool] | NotGiven = NOT_GIVEN,
        kind: Literal[
            "text",
            "datetime",
            "date",
            "link",
            "multilink",
            "select",
            "multiselect",
            "integer",
            "float",
            "percentage",
            "tag",
            "variable",
            "attachment",
            "phone",
            "email",
            "vote",
            "checkbox",
            "duration",
        ]
        | NotGiven = NOT_GIVEN,
        kind_options: SelectOptionsLookupParam | NotGiven = NOT_GIVEN,
        morta_synced: int | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        procore_synced: int | NotGiven = NOT_GIVEN,
        public_id: str | NotGiven = NOT_GIVEN,
        revizto_issues_synced: int | NotGiven = NOT_GIVEN,
        script: Optional[str] | NotGiven = NOT_GIVEN,
        script_enabled: bool | NotGiven = NOT_GIVEN,
        thousand_separator: bool | NotGiven = NOT_GIVEN,
        viewpoint_rfis_synced: int | NotGiven = NOT_GIVEN,
        viewpoint_synced: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnCreateResponse:
        """
        Add a new column to an existing table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return self._post(
            f"/v1/table/{table_id}/column",
            body=maybe_transform(
                {
                    "aconex_synced": aconex_synced,
                    "aconex_workflows_synced": aconex_workflows_synced,
                    "aggregate": aggregate,
                    "alter_options": alter_options,
                    "asite_documents_synced": asite_documents_synced,
                    "asite_forms_synced": asite_forms_synced,
                    "autodesk_bim360_checklists_synced": autodesk_bim360_checklists_synced,
                    "autodesk_bim360_issues_synced": autodesk_bim360_issues_synced,
                    "autodesk_bim360_models_synced": autodesk_bim360_models_synced,
                    "autodesk_bim360_synced": autodesk_bim360_synced,
                    "autodesk_bim360_users_synced": autodesk_bim360_users_synced,
                    "context": context,
                    "date_format": date_format,
                    "decimal_places": decimal_places,
                    "description": description,
                    "display_link": display_link,
                    "export_width": export_width,
                    "formula": formula,
                    "formula_enabled": formula_enabled,
                    "header_background_color": header_background_color,
                    "header_text_color": header_text_color,
                    "is_indexed": is_indexed,
                    "is_joined": is_joined,
                    "kind": kind,
                    "kind_options": kind_options,
                    "morta_synced": morta_synced,
                    "name": name,
                    "procore_synced": procore_synced,
                    "public_id": public_id,
                    "revizto_issues_synced": revizto_issues_synced,
                    "script": script,
                    "script_enabled": script_enabled,
                    "thousand_separator": thousand_separator,
                    "viewpoint_rfis_synced": viewpoint_rfis_synced,
                    "viewpoint_synced": viewpoint_synced,
                    "width": width,
                },
                column_create_params.ColumnCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnCreateResponse,
        )

    def update(
        self,
        column_id: str,
        *,
        table_id: str,
        aconex_synced: int | NotGiven = NOT_GIVEN,
        aconex_workflows_synced: int | NotGiven = NOT_GIVEN,
        aggregate: int | NotGiven = NOT_GIVEN,
        alter_options: column_update_params.AlterOptions | NotGiven = NOT_GIVEN,
        asite_documents_synced: int | NotGiven = NOT_GIVEN,
        asite_forms_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_checklists_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_issues_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_models_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_users_synced: int | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        date_format: Optional[str] | NotGiven = NOT_GIVEN,
        decimal_places: int | NotGiven = NOT_GIVEN,
        description: column_update_params.Description | NotGiven = NOT_GIVEN,
        display_link: bool | NotGiven = NOT_GIVEN,
        export_width: Optional[int] | NotGiven = NOT_GIVEN,
        formula: Optional[str] | NotGiven = NOT_GIVEN,
        formula_enabled: bool | NotGiven = NOT_GIVEN,
        header_background_color: Optional[str] | NotGiven = NOT_GIVEN,
        header_text_color: Optional[str] | NotGiven = NOT_GIVEN,
        is_indexed: bool | NotGiven = NOT_GIVEN,
        is_joined: Optional[bool] | NotGiven = NOT_GIVEN,
        kind: Literal[
            "text",
            "datetime",
            "date",
            "link",
            "multilink",
            "select",
            "multiselect",
            "integer",
            "float",
            "percentage",
            "tag",
            "variable",
            "attachment",
            "phone",
            "email",
            "vote",
            "checkbox",
            "duration",
        ]
        | NotGiven = NOT_GIVEN,
        kind_options: SelectOptionsLookupParam | NotGiven = NOT_GIVEN,
        morta_synced: int | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        procore_synced: int | NotGiven = NOT_GIVEN,
        public_id: str | NotGiven = NOT_GIVEN,
        revizto_issues_synced: int | NotGiven = NOT_GIVEN,
        script: Optional[str] | NotGiven = NOT_GIVEN,
        script_enabled: bool | NotGiven = NOT_GIVEN,
        thousand_separator: bool | NotGiven = NOT_GIVEN,
        viewpoint_rfis_synced: int | NotGiven = NOT_GIVEN,
        viewpoint_synced: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnUpdateResponse:
        """
        Update the properties of a specific column in a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return self._put(
            f"/v1/table/{table_id}/column/{column_id}",
            body=maybe_transform(
                {
                    "aconex_synced": aconex_synced,
                    "aconex_workflows_synced": aconex_workflows_synced,
                    "aggregate": aggregate,
                    "alter_options": alter_options,
                    "asite_documents_synced": asite_documents_synced,
                    "asite_forms_synced": asite_forms_synced,
                    "autodesk_bim360_checklists_synced": autodesk_bim360_checklists_synced,
                    "autodesk_bim360_issues_synced": autodesk_bim360_issues_synced,
                    "autodesk_bim360_models_synced": autodesk_bim360_models_synced,
                    "autodesk_bim360_synced": autodesk_bim360_synced,
                    "autodesk_bim360_users_synced": autodesk_bim360_users_synced,
                    "context": context,
                    "date_format": date_format,
                    "decimal_places": decimal_places,
                    "description": description,
                    "display_link": display_link,
                    "export_width": export_width,
                    "formula": formula,
                    "formula_enabled": formula_enabled,
                    "header_background_color": header_background_color,
                    "header_text_color": header_text_color,
                    "is_indexed": is_indexed,
                    "is_joined": is_joined,
                    "kind": kind,
                    "kind_options": kind_options,
                    "morta_synced": morta_synced,
                    "name": name,
                    "procore_synced": procore_synced,
                    "public_id": public_id,
                    "revizto_issues_synced": revizto_issues_synced,
                    "script": script,
                    "script_enabled": script_enabled,
                    "thousand_separator": thousand_separator,
                    "viewpoint_rfis_synced": viewpoint_rfis_synced,
                    "viewpoint_synced": viewpoint_synced,
                    "width": width,
                },
                column_update_params.ColumnUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnUpdateResponse,
        )

    def delete(
        self,
        column_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnDeleteResponse:
        """
        Delete a specific column from a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return self._delete(
            f"/v1/table/{table_id}/column/{column_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnDeleteResponse,
        )

    def check_views(
        self,
        column_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnCheckViewsResponse:
        """
        Retrieve all views in which a specific table column is used.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return self._get(
            f"/v1/table/{table_id}/column/{column_id}/views",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnCheckViewsResponse,
        )

    def get_distinct_values(
        self,
        column_id: str,
        *,
        table_id: str,
        filter: str | NotGiven = NOT_GIVEN,
        group_columns: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnGetDistinctValuesResponse:
        """
        Retrieve a list of distinct (unique) values for a specified column in a table.

        Args:
          filter: Filter criteria for the distinct values

          group_columns: Specify columns for grouping values

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return self._get(
            f"/v1/table/{table_id}/column/{column_id}/distinct",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "group_columns": group_columns,
                    },
                    column_get_distinct_values_params.ColumnGetDistinctValuesParams,
                ),
            ),
            cast_to=ColumnGetDistinctValuesResponse,
        )

    def restore(
        self,
        column_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnRestoreResponse:
        """
        Restore a previously deleted column in a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return self._put(
            f"/v1/table/{table_id}/column/{column_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnRestoreResponse,
        )


class AsyncColumnResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncColumnResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncColumnResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncColumnResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncColumnResourceWithStreamingResponse(self)

    async def create(
        self,
        table_id: str,
        *,
        aconex_synced: int | NotGiven = NOT_GIVEN,
        aconex_workflows_synced: int | NotGiven = NOT_GIVEN,
        aggregate: int | NotGiven = NOT_GIVEN,
        alter_options: column_create_params.AlterOptions | NotGiven = NOT_GIVEN,
        asite_documents_synced: int | NotGiven = NOT_GIVEN,
        asite_forms_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_checklists_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_issues_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_models_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_users_synced: int | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        date_format: Optional[str] | NotGiven = NOT_GIVEN,
        decimal_places: int | NotGiven = NOT_GIVEN,
        description: column_create_params.Description | NotGiven = NOT_GIVEN,
        display_link: bool | NotGiven = NOT_GIVEN,
        export_width: Optional[int] | NotGiven = NOT_GIVEN,
        formula: Optional[str] | NotGiven = NOT_GIVEN,
        formula_enabled: bool | NotGiven = NOT_GIVEN,
        header_background_color: Optional[str] | NotGiven = NOT_GIVEN,
        header_text_color: Optional[str] | NotGiven = NOT_GIVEN,
        is_indexed: bool | NotGiven = NOT_GIVEN,
        is_joined: Optional[bool] | NotGiven = NOT_GIVEN,
        kind: Literal[
            "text",
            "datetime",
            "date",
            "link",
            "multilink",
            "select",
            "multiselect",
            "integer",
            "float",
            "percentage",
            "tag",
            "variable",
            "attachment",
            "phone",
            "email",
            "vote",
            "checkbox",
            "duration",
        ]
        | NotGiven = NOT_GIVEN,
        kind_options: SelectOptionsLookupParam | NotGiven = NOT_GIVEN,
        morta_synced: int | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        procore_synced: int | NotGiven = NOT_GIVEN,
        public_id: str | NotGiven = NOT_GIVEN,
        revizto_issues_synced: int | NotGiven = NOT_GIVEN,
        script: Optional[str] | NotGiven = NOT_GIVEN,
        script_enabled: bool | NotGiven = NOT_GIVEN,
        thousand_separator: bool | NotGiven = NOT_GIVEN,
        viewpoint_rfis_synced: int | NotGiven = NOT_GIVEN,
        viewpoint_synced: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnCreateResponse:
        """
        Add a new column to an existing table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        return await self._post(
            f"/v1/table/{table_id}/column",
            body=await async_maybe_transform(
                {
                    "aconex_synced": aconex_synced,
                    "aconex_workflows_synced": aconex_workflows_synced,
                    "aggregate": aggregate,
                    "alter_options": alter_options,
                    "asite_documents_synced": asite_documents_synced,
                    "asite_forms_synced": asite_forms_synced,
                    "autodesk_bim360_checklists_synced": autodesk_bim360_checklists_synced,
                    "autodesk_bim360_issues_synced": autodesk_bim360_issues_synced,
                    "autodesk_bim360_models_synced": autodesk_bim360_models_synced,
                    "autodesk_bim360_synced": autodesk_bim360_synced,
                    "autodesk_bim360_users_synced": autodesk_bim360_users_synced,
                    "context": context,
                    "date_format": date_format,
                    "decimal_places": decimal_places,
                    "description": description,
                    "display_link": display_link,
                    "export_width": export_width,
                    "formula": formula,
                    "formula_enabled": formula_enabled,
                    "header_background_color": header_background_color,
                    "header_text_color": header_text_color,
                    "is_indexed": is_indexed,
                    "is_joined": is_joined,
                    "kind": kind,
                    "kind_options": kind_options,
                    "morta_synced": morta_synced,
                    "name": name,
                    "procore_synced": procore_synced,
                    "public_id": public_id,
                    "revizto_issues_synced": revizto_issues_synced,
                    "script": script,
                    "script_enabled": script_enabled,
                    "thousand_separator": thousand_separator,
                    "viewpoint_rfis_synced": viewpoint_rfis_synced,
                    "viewpoint_synced": viewpoint_synced,
                    "width": width,
                },
                column_create_params.ColumnCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnCreateResponse,
        )

    async def update(
        self,
        column_id: str,
        *,
        table_id: str,
        aconex_synced: int | NotGiven = NOT_GIVEN,
        aconex_workflows_synced: int | NotGiven = NOT_GIVEN,
        aggregate: int | NotGiven = NOT_GIVEN,
        alter_options: column_update_params.AlterOptions | NotGiven = NOT_GIVEN,
        asite_documents_synced: int | NotGiven = NOT_GIVEN,
        asite_forms_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_checklists_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_issues_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_models_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_synced: int | NotGiven = NOT_GIVEN,
        autodesk_bim360_users_synced: int | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        date_format: Optional[str] | NotGiven = NOT_GIVEN,
        decimal_places: int | NotGiven = NOT_GIVEN,
        description: column_update_params.Description | NotGiven = NOT_GIVEN,
        display_link: bool | NotGiven = NOT_GIVEN,
        export_width: Optional[int] | NotGiven = NOT_GIVEN,
        formula: Optional[str] | NotGiven = NOT_GIVEN,
        formula_enabled: bool | NotGiven = NOT_GIVEN,
        header_background_color: Optional[str] | NotGiven = NOT_GIVEN,
        header_text_color: Optional[str] | NotGiven = NOT_GIVEN,
        is_indexed: bool | NotGiven = NOT_GIVEN,
        is_joined: Optional[bool] | NotGiven = NOT_GIVEN,
        kind: Literal[
            "text",
            "datetime",
            "date",
            "link",
            "multilink",
            "select",
            "multiselect",
            "integer",
            "float",
            "percentage",
            "tag",
            "variable",
            "attachment",
            "phone",
            "email",
            "vote",
            "checkbox",
            "duration",
        ]
        | NotGiven = NOT_GIVEN,
        kind_options: SelectOptionsLookupParam | NotGiven = NOT_GIVEN,
        morta_synced: int | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        procore_synced: int | NotGiven = NOT_GIVEN,
        public_id: str | NotGiven = NOT_GIVEN,
        revizto_issues_synced: int | NotGiven = NOT_GIVEN,
        script: Optional[str] | NotGiven = NOT_GIVEN,
        script_enabled: bool | NotGiven = NOT_GIVEN,
        thousand_separator: bool | NotGiven = NOT_GIVEN,
        viewpoint_rfis_synced: int | NotGiven = NOT_GIVEN,
        viewpoint_synced: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnUpdateResponse:
        """
        Update the properties of a specific column in a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return await self._put(
            f"/v1/table/{table_id}/column/{column_id}",
            body=await async_maybe_transform(
                {
                    "aconex_synced": aconex_synced,
                    "aconex_workflows_synced": aconex_workflows_synced,
                    "aggregate": aggregate,
                    "alter_options": alter_options,
                    "asite_documents_synced": asite_documents_synced,
                    "asite_forms_synced": asite_forms_synced,
                    "autodesk_bim360_checklists_synced": autodesk_bim360_checklists_synced,
                    "autodesk_bim360_issues_synced": autodesk_bim360_issues_synced,
                    "autodesk_bim360_models_synced": autodesk_bim360_models_synced,
                    "autodesk_bim360_synced": autodesk_bim360_synced,
                    "autodesk_bim360_users_synced": autodesk_bim360_users_synced,
                    "context": context,
                    "date_format": date_format,
                    "decimal_places": decimal_places,
                    "description": description,
                    "display_link": display_link,
                    "export_width": export_width,
                    "formula": formula,
                    "formula_enabled": formula_enabled,
                    "header_background_color": header_background_color,
                    "header_text_color": header_text_color,
                    "is_indexed": is_indexed,
                    "is_joined": is_joined,
                    "kind": kind,
                    "kind_options": kind_options,
                    "morta_synced": morta_synced,
                    "name": name,
                    "procore_synced": procore_synced,
                    "public_id": public_id,
                    "revizto_issues_synced": revizto_issues_synced,
                    "script": script,
                    "script_enabled": script_enabled,
                    "thousand_separator": thousand_separator,
                    "viewpoint_rfis_synced": viewpoint_rfis_synced,
                    "viewpoint_synced": viewpoint_synced,
                    "width": width,
                },
                column_update_params.ColumnUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnUpdateResponse,
        )

    async def delete(
        self,
        column_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnDeleteResponse:
        """
        Delete a specific column from a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return await self._delete(
            f"/v1/table/{table_id}/column/{column_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnDeleteResponse,
        )

    async def check_views(
        self,
        column_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnCheckViewsResponse:
        """
        Retrieve all views in which a specific table column is used.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/column/{column_id}/views",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnCheckViewsResponse,
        )

    async def get_distinct_values(
        self,
        column_id: str,
        *,
        table_id: str,
        filter: str | NotGiven = NOT_GIVEN,
        group_columns: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnGetDistinctValuesResponse:
        """
        Retrieve a list of distinct (unique) values for a specified column in a table.

        Args:
          filter: Filter criteria for the distinct values

          group_columns: Specify columns for grouping values

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return await self._get(
            f"/v1/table/{table_id}/column/{column_id}/distinct",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "group_columns": group_columns,
                    },
                    column_get_distinct_values_params.ColumnGetDistinctValuesParams,
                ),
            ),
            cast_to=ColumnGetDistinctValuesResponse,
        )

    async def restore(
        self,
        column_id: str,
        *,
        table_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ColumnRestoreResponse:
        """
        Restore a previously deleted column in a table.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_id:
            raise ValueError(f"Expected a non-empty value for `table_id` but received {table_id!r}")
        if not column_id:
            raise ValueError(f"Expected a non-empty value for `column_id` but received {column_id!r}")
        return await self._put(
            f"/v1/table/{table_id}/column/{column_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ColumnRestoreResponse,
        )


class ColumnResourceWithRawResponse:
    def __init__(self, column: ColumnResource) -> None:
        self._column = column

        self.create = to_raw_response_wrapper(
            column.create,
        )
        self.update = to_raw_response_wrapper(
            column.update,
        )
        self.delete = to_raw_response_wrapper(
            column.delete,
        )
        self.check_views = to_raw_response_wrapper(
            column.check_views,
        )
        self.get_distinct_values = to_raw_response_wrapper(
            column.get_distinct_values,
        )
        self.restore = to_raw_response_wrapper(
            column.restore,
        )


class AsyncColumnResourceWithRawResponse:
    def __init__(self, column: AsyncColumnResource) -> None:
        self._column = column

        self.create = async_to_raw_response_wrapper(
            column.create,
        )
        self.update = async_to_raw_response_wrapper(
            column.update,
        )
        self.delete = async_to_raw_response_wrapper(
            column.delete,
        )
        self.check_views = async_to_raw_response_wrapper(
            column.check_views,
        )
        self.get_distinct_values = async_to_raw_response_wrapper(
            column.get_distinct_values,
        )
        self.restore = async_to_raw_response_wrapper(
            column.restore,
        )


class ColumnResourceWithStreamingResponse:
    def __init__(self, column: ColumnResource) -> None:
        self._column = column

        self.create = to_streamed_response_wrapper(
            column.create,
        )
        self.update = to_streamed_response_wrapper(
            column.update,
        )
        self.delete = to_streamed_response_wrapper(
            column.delete,
        )
        self.check_views = to_streamed_response_wrapper(
            column.check_views,
        )
        self.get_distinct_values = to_streamed_response_wrapper(
            column.get_distinct_values,
        )
        self.restore = to_streamed_response_wrapper(
            column.restore,
        )


class AsyncColumnResourceWithStreamingResponse:
    def __init__(self, column: AsyncColumnResource) -> None:
        self._column = column

        self.create = async_to_streamed_response_wrapper(
            column.create,
        )
        self.update = async_to_streamed_response_wrapper(
            column.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            column.delete,
        )
        self.check_views = async_to_streamed_response_wrapper(
            column.check_views,
        )
        self.get_distinct_values = async_to_streamed_response_wrapper(
            column.get_distinct_values,
        )
        self.restore = async_to_streamed_response_wrapper(
            column.restore,
        )
