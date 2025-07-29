# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)
from morta.types.table import (
    ViewListResponse,
    ViewStatsResponse,
    ViewCreateResponse,
    ViewDeleteResponse,
    ViewUpdateResponse,
    ViewRetrieveResponse,
    ViewDuplicateResponse,
    ViewPreviewRowResponse,
    ViewSetDefaultResponse,
    ViewUpdateCellsResponse,
    ViewDuplicateDefaultResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestViews:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        view = client.table.views.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
        )
        assert_matches_type(ViewCreateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        view = client.table.views.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
            allow_contributor_delete=True,
            chart_settings={
                "aggregate": "sum",
                "chart_type": "bar",
                "column_gantt_end_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_gantt_start_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_label_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_stack_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_value_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "show_legend": True,
                "show_title": True,
                "show_values": True,
                "sort_aggregate": "asc",
            },
            collapsed_group_view=True,
            colour_settings=[
                {
                    "background_colour": "backgroundColour",
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "font_colour": "fontColour",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "value": {},
                }
            ],
            columns=[
                {
                    "column_name": "columnName",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "display_validation_error": True,
                    "hard_validation": True,
                    "locked": True,
                    "required": True,
                    "string_validation": "stringValidation",
                    "validation_message": "validationMessage",
                    "validation_no_blanks": True,
                    "validation_no_duplicates": True,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            description={
                "content": {
                    "blocks": [
                        {
                            "data": {"foo": "bar"},
                            "depth": 0,
                            "entity_ranges": [
                                {
                                    "key": 0,
                                    "length": 0,
                                    "offset": 0,
                                }
                            ],
                            "inline_style_ranges": [
                                {
                                    "length": 0,
                                    "offset": 0,
                                    "style": "style",
                                }
                            ],
                            "key": "key",
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "entity_map": {"foo": "bar"},
                }
            },
            disable_new_row=True,
            disable_sync_csv=True,
            display_comment_rows=0,
            display_validation_error_rows=0,
            filter_settings=[
                {
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "or_group": "orGroup",
                    "value": {},
                }
            ],
            frozen_index=0,
            group_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            include_all_columns=True,
            is_default=True,
            row_height=0,
            sort_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            type=0,
            unpack_multiselect_group_view=True,
        )
        assert_matches_type(ViewCreateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewCreateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewCreateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.views.with_raw_response.create(
                table_id="",
                name="x",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        view = client.table.views.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Morta) -> None:
        view = client.table.views.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            ignore_cached_options=True,
        )
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewRetrieveResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.retrieve(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        view = client.table.views.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        view = client.table.views.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            allow_contributor_delete=True,
            chart_settings={
                "aggregate": "sum",
                "chart_type": "bar",
                "column_gantt_end_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_gantt_start_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_label_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_stack_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_value_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "show_legend": True,
                "show_title": True,
                "show_values": True,
                "sort_aggregate": "asc",
            },
            collapsed_group_view=True,
            colour_settings=[
                {
                    "background_colour": "backgroundColour",
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "font_colour": "fontColour",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "value": {},
                }
            ],
            columns=[
                {
                    "aconex_synced": 0,
                    "aconex_workflows_synced": 0,
                    "aggregate": 0,
                    "alter_options": {
                        "date_conversion_format": "DD/MM/YYYY",
                        "run_script_on_all_cells": True,
                    },
                    "asite_documents_synced": 0,
                    "asite_forms_synced": 0,
                    "autodesk_bim360_checklists_synced": 0,
                    "autodesk_bim360_issues_synced": 0,
                    "autodesk_bim360_models_synced": 0,
                    "autodesk_bim360_synced": 0,
                    "autodesk_bim360_users_synced": 0,
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "date_format": "dateFormat",
                    "decimal_places": 0,
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "display_link": True,
                    "display_validation_error": True,
                    "export_width": 0,
                    "formula": "formula",
                    "formula_enabled": True,
                    "hard_validation": True,
                    "header_background_color": "headerBackgroundColor",
                    "header_text_color": "headerTextColor",
                    "is_indexed": True,
                    "is_joined": True,
                    "kind": "text",
                    "kind_options": {
                        "autopopulate": True,
                        "manual_options": ["string"],
                        "table_options": {
                            "column_id": "columnId",
                            "dependencies": [
                                {
                                    "column_id": "columnId",
                                    "column_join_id": "columnJoinId",
                                }
                            ],
                            "live_values": True,
                            "table_id": "tableId",
                            "view_id": "viewId",
                        },
                    },
                    "locked": True,
                    "morta_synced": 0,
                    "name": "name",
                    "procore_synced": 0,
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "required": True,
                    "revizto_issues_synced": 0,
                    "script": "script",
                    "script_enabled": True,
                    "sort_order": 0,
                    "string_validation": "stringValidation",
                    "thousand_separator": True,
                    "validation_message": "validationMessage",
                    "validation_no_blanks": True,
                    "validation_no_duplicates": True,
                    "viewpoint_rfis_synced": 0,
                    "viewpoint_synced": 0,
                    "width": 100,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            description={
                "content": {
                    "blocks": [
                        {
                            "data": {"foo": "bar"},
                            "depth": 0,
                            "entity_ranges": [
                                {
                                    "key": 0,
                                    "length": 0,
                                    "offset": 0,
                                }
                            ],
                            "inline_style_ranges": [
                                {
                                    "length": 0,
                                    "offset": 0,
                                    "style": "style",
                                }
                            ],
                            "key": "key",
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "entity_map": {"foo": "bar"},
                }
            },
            disable_new_row=True,
            disable_sync_csv=True,
            display_comment_rows=0,
            display_validation_error_rows=0,
            filter_settings=[
                {
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "or_group": "orGroup",
                    "value": {},
                }
            ],
            frozen_index=0,
            group_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            name="x",
            row_height=0,
            sort_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            type=0,
            unpack_multiselect_group_view=True,
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewUpdateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.update(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Morta) -> None:
        view = client.table.views.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewListResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Morta) -> None:
        view = client.table.views.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            ignore_columns=True,
        )
        assert_matches_type(ViewListResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewListResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewListResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.views.with_raw_response.list(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        view = client.table.views.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewDeleteResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewDeleteResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewDeleteResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_download_csv(self, client: Morta) -> None:
        view = client.table.views.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_download_csv_with_all_params(self, client: Morta) -> None:
        view = client.table.views.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sort="sort",
        )
        assert_matches_type(str, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_download_csv(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(str, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_download_csv(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(str, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_download_csv(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.download_csv(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate(self, client: Morta) -> None:
        view = client.table.views.duplicate(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewDuplicateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_duplicate(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.duplicate(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewDuplicateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_duplicate(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.duplicate(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewDuplicateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_duplicate(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.views.with_raw_response.duplicate(
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.duplicate(
                view_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate_default(self, client: Morta) -> None:
        view = client.table.views.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate_default_with_all_params(self, client: Morta) -> None:
        view = client.table.views.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            name="x",
            type=0,
        )
        assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_duplicate_default(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_duplicate_default(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_duplicate_default(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.views.with_raw_response.duplicate_default(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_preview_row(self, client: Morta) -> None:
        view = client.table.views.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
        )
        assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_preview_row_with_all_params(self, client: Morta) -> None:
        view = client.table.views.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_preview_row(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_preview_row(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_preview_row(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.preview_row(
                view_id="",
                row_data={"foo": "bar"},
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_set_default(self, client: Morta) -> None:
        view = client.table.views.set_default(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewSetDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_set_default(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.set_default(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewSetDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_set_default(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.set_default(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewSetDefaultResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_set_default(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.set_default(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_stats(self, client: Morta) -> None:
        view = client.table.views.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewStatsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_stats_with_all_params(self, client: Morta) -> None:
        view = client.table.views.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sum_avg_max_min_count=["string"],
        )
        assert_matches_type(ViewStatsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_stats(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewStatsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_stats(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewStatsResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_stats(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.stats(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_stream_rows(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        view = client.table.views.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert view.is_closed
        assert view.json() == {"foo": "bar"}
        assert cast(Any, view.is_closed) is True
        assert isinstance(view, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_stream_rows_with_all_params(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        view = client.table.views.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            page=1,
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            size=1,
            sort="sort",
        )
        assert view.is_closed
        assert view.json() == {"foo": "bar"}
        assert cast(Any, view.is_closed) is True
        assert isinstance(view, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_stream_rows(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        view = client.table.views.with_raw_response.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert view.is_closed is True
        assert view.http_request.headers.get("X-Stainless-Lang") == "python"
        assert view.json() == {"foo": "bar"}
        assert isinstance(view, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_stream_rows(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.table.views.with_streaming_response.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as view:
            assert not view.is_closed
            assert view.http_request.headers.get("X-Stainless-Lang") == "python"

            assert view.json() == {"foo": "bar"}
            assert cast(Any, view.is_closed) is True
            assert isinstance(view, StreamedBinaryAPIResponse)

        assert cast(Any, view.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_stream_rows(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.stream_rows(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_cells(self, client: Morta) -> None:
        view = client.table.views.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        )
        assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_cells_with_all_params(self, client: Morta) -> None:
        view = client.table.views.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_cells(self, client: Morta) -> None:
        response = client.table.views.with_raw_response.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_cells(self, client: Morta) -> None:
        with client.table.views.with_streaming_response.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_cells(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.with_raw_response.update_cells(
                view_id="",
                cells=[
                    {
                        "column_name": "x",
                        "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "value": {},
                    }
                ],
            )


class TestAsyncViews:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
        )
        assert_matches_type(ViewCreateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
            allow_contributor_delete=True,
            chart_settings={
                "aggregate": "sum",
                "chart_type": "bar",
                "column_gantt_end_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_gantt_start_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_label_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_stack_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_value_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "show_legend": True,
                "show_title": True,
                "show_values": True,
                "sort_aggregate": "asc",
            },
            collapsed_group_view=True,
            colour_settings=[
                {
                    "background_colour": "backgroundColour",
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "font_colour": "fontColour",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "value": {},
                }
            ],
            columns=[
                {
                    "column_name": "columnName",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "display_validation_error": True,
                    "hard_validation": True,
                    "locked": True,
                    "required": True,
                    "string_validation": "stringValidation",
                    "validation_message": "validationMessage",
                    "validation_no_blanks": True,
                    "validation_no_duplicates": True,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            description={
                "content": {
                    "blocks": [
                        {
                            "data": {"foo": "bar"},
                            "depth": 0,
                            "entity_ranges": [
                                {
                                    "key": 0,
                                    "length": 0,
                                    "offset": 0,
                                }
                            ],
                            "inline_style_ranges": [
                                {
                                    "length": 0,
                                    "offset": 0,
                                    "style": "style",
                                }
                            ],
                            "key": "key",
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "entity_map": {"foo": "bar"},
                }
            },
            disable_new_row=True,
            disable_sync_csv=True,
            display_comment_rows=0,
            display_validation_error_rows=0,
            filter_settings=[
                {
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "or_group": "orGroup",
                    "value": {},
                }
            ],
            frozen_index=0,
            group_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            include_all_columns=True,
            is_default=True,
            row_height=0,
            sort_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            type=0,
            unpack_multiselect_group_view=True,
        )
        assert_matches_type(ViewCreateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewCreateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewCreateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.views.with_raw_response.create(
                table_id="",
                name="x",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            ignore_cached_options=True,
        )
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.retrieve(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewRetrieveResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.retrieve(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            allow_contributor_delete=True,
            chart_settings={
                "aggregate": "sum",
                "chart_type": "bar",
                "column_gantt_end_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_gantt_start_date_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_label_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_stack_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "column_value_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "show_legend": True,
                "show_title": True,
                "show_values": True,
                "sort_aggregate": "asc",
            },
            collapsed_group_view=True,
            colour_settings=[
                {
                    "background_colour": "backgroundColour",
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "font_colour": "fontColour",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "value": {},
                }
            ],
            columns=[
                {
                    "aconex_synced": 0,
                    "aconex_workflows_synced": 0,
                    "aggregate": 0,
                    "alter_options": {
                        "date_conversion_format": "DD/MM/YYYY",
                        "run_script_on_all_cells": True,
                    },
                    "asite_documents_synced": 0,
                    "asite_forms_synced": 0,
                    "autodesk_bim360_checklists_synced": 0,
                    "autodesk_bim360_issues_synced": 0,
                    "autodesk_bim360_models_synced": 0,
                    "autodesk_bim360_synced": 0,
                    "autodesk_bim360_users_synced": 0,
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "date_format": "dateFormat",
                    "decimal_places": 0,
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "display_link": True,
                    "display_validation_error": True,
                    "export_width": 0,
                    "formula": "formula",
                    "formula_enabled": True,
                    "hard_validation": True,
                    "header_background_color": "headerBackgroundColor",
                    "header_text_color": "headerTextColor",
                    "is_indexed": True,
                    "is_joined": True,
                    "kind": "text",
                    "kind_options": {
                        "autopopulate": True,
                        "manual_options": ["string"],
                        "table_options": {
                            "column_id": "columnId",
                            "dependencies": [
                                {
                                    "column_id": "columnId",
                                    "column_join_id": "columnJoinId",
                                }
                            ],
                            "live_values": True,
                            "table_id": "tableId",
                            "view_id": "viewId",
                        },
                    },
                    "locked": True,
                    "morta_synced": 0,
                    "name": "name",
                    "procore_synced": 0,
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "required": True,
                    "revizto_issues_synced": 0,
                    "script": "script",
                    "script_enabled": True,
                    "sort_order": 0,
                    "string_validation": "stringValidation",
                    "thousand_separator": True,
                    "validation_message": "validationMessage",
                    "validation_no_blanks": True,
                    "validation_no_duplicates": True,
                    "viewpoint_rfis_synced": 0,
                    "viewpoint_synced": 0,
                    "width": 100,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            description={
                "content": {
                    "blocks": [
                        {
                            "data": {"foo": "bar"},
                            "depth": 0,
                            "entity_ranges": [
                                {
                                    "key": 0,
                                    "length": 0,
                                    "offset": 0,
                                }
                            ],
                            "inline_style_ranges": [
                                {
                                    "length": 0,
                                    "offset": 0,
                                    "style": "style",
                                }
                            ],
                            "key": "key",
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "entity_map": {"foo": "bar"},
                }
            },
            disable_new_row=True,
            disable_sync_csv=True,
            display_comment_rows=0,
            display_validation_error_rows=0,
            filter_settings=[
                {
                    "column_name": "columnName",
                    "filter_type": "eq",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "multiple_values": [{}],
                    "or_group": "orGroup",
                    "value": {},
                }
            ],
            frozen_index=0,
            group_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            name="x",
            row_height=0,
            sort_settings=[
                {
                    "column_name": "columnName",
                    "direction": "direction",
                    "column_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            type=0,
            unpack_multiselect_group_view=True,
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewUpdateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.update(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewListResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            ignore_columns=True,
        )
        assert_matches_type(ViewListResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewListResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.list(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewListResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.views.with_raw_response.list(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewDeleteResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewDeleteResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewDeleteResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_download_csv(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_download_csv_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sort="sort",
        )
        assert_matches_type(str, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_download_csv(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(str, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_download_csv(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.download_csv(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(str, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_download_csv(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.download_csv(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.duplicate(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewDuplicateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_duplicate(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.duplicate(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewDuplicateResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_duplicate(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.duplicate(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewDuplicateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_duplicate(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.views.with_raw_response.duplicate(
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.duplicate(
                view_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate_default(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate_default_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            name="x",
            type=0,
        )
        assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_duplicate_default(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_duplicate_default(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.duplicate_default(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewDuplicateDefaultResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_duplicate_default(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.views.with_raw_response.duplicate_default(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_preview_row(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
        )
        assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_preview_row_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_preview_row(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_preview_row(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.preview_row(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            row_data={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewPreviewRowResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_preview_row(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.preview_row(
                view_id="",
                row_data={"foo": "bar"},
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_default(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.set_default(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewSetDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_set_default(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.set_default(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewSetDefaultResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_set_default(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.set_default(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewSetDefaultResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_set_default(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.set_default(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_stats(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ViewStatsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_stats_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sum_avg_max_min_count=["string"],
        )
        assert_matches_type(ViewStatsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_stats(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewStatsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_stats(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.stats(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewStatsResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_stats(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.stats(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_stream_rows(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        view = await async_client.table.views.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert view.is_closed
        assert await view.json() == {"foo": "bar"}
        assert cast(Any, view.is_closed) is True
        assert isinstance(view, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_stream_rows_with_all_params(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        view = await async_client.table.views.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            page=1,
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            size=1,
            sort="sort",
        )
        assert view.is_closed
        assert await view.json() == {"foo": "bar"}
        assert cast(Any, view.is_closed) is True
        assert isinstance(view, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_stream_rows(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        view = await async_client.table.views.with_raw_response.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert view.is_closed is True
        assert view.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await view.json() == {"foo": "bar"}
        assert isinstance(view, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_stream_rows(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/views/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.table.views.with_streaming_response.stream_rows(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as view:
            assert not view.is_closed
            assert view.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await view.json() == {"foo": "bar"}
            assert cast(Any, view.is_closed) is True
            assert isinstance(view, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, view.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_stream_rows(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.stream_rows(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_cells(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        )
        assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_cells_with_all_params(self, async_client: AsyncMorta) -> None:
        view = await async_client.table.views.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_cells(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.with_raw_response.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_cells(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.with_streaming_response.update_cells(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewUpdateCellsResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_cells(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.with_raw_response.update_cells(
                view_id="",
                cells=[
                    {
                        "column_name": "x",
                        "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "value": {},
                    }
                ],
            )
