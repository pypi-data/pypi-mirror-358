# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from morta import Morta, AsyncMorta
from morta.types import (
    TableCreateResponse,
    TableDeleteResponse,
    TableUpdateResponse,
    TableRestoreResponse,
    TableRetrieveResponse,
    TableTruncateResponse,
    TableDuplicateResponse,
    TableListJoinsResponse,
    TableCheckUsageResponse,
    TableDeleteRowsResponse,
    TableCreateIndexResponse,
    TableListColumnsResponse,
    TableUpdateCellsResponse,
    TableGetStatisticsResponse,
    TableGetDuplicatedChildrenResponse,
)
from tests.utils import assert_matches_type
from morta._utils import parse_datetime
from morta._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTable:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        table = client.table.create(
            columns=[{}],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableCreateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        table = client.table.create(
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
                    "export_width": 0,
                    "formula": "formula",
                    "formula_enabled": True,
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
                    "morta_synced": 0,
                    "name": "name",
                    "procore_synced": 0,
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "revizto_issues_synced": 0,
                    "script": "script",
                    "script_enabled": True,
                    "thousand_separator": True,
                    "viewpoint_rfis_synced": 0,
                    "viewpoint_synced": 0,
                    "width": 0,
                }
            ],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            joins=[
                {
                    "data_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "is_one_to_many": True,
                    "join_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "join_table_name": "joinTableName",
                    "join_view_id": "joinViewId",
                    "join_view_name": "joinViewName",
                }
            ],
            type="type",
        )
        assert_matches_type(TableCreateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.table.with_raw_response.create(
            columns=[{}],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableCreateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.table.with_streaming_response.create(
            columns=[{}],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableCreateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        table = client.table.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableRetrieveResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Morta) -> None:
        table = client.table.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=["string"],
            distinct_columns=["string"],
            filter="filter",
            ignore_cached_options=True,
            last_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            next_page_token="next_page_token",
            page=1,
            size=1,
            sort="sort",
        )
        assert_matches_type(TableRetrieveResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.table.with_raw_response.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableRetrieveResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.table.with_streaming_response.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableRetrieveResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.retrieve(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        table = client.table.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableUpdateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        table = client.table.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            allow_comments=True,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            is_reference_table=True,
            joins=[
                {
                    "data_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "is_one_to_many": True,
                    "join_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "join_table_name": "joinTableName",
                    "join_view_id": "joinViewId",
                    "join_view_name": "joinViewName",
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            keep_colours_in_sync=True,
            keep_validations_in_sync=True,
            logo="logo",
            name="name",
            sync_hourly_frequency=0,
            type="type",
        )
        assert_matches_type(TableUpdateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.table.with_raw_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableUpdateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.table.with_streaming_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableUpdateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.update(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        table = client.table.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableDeleteResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.table.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableDeleteResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.table.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableDeleteResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_check_usage(self, client: Morta) -> None:
        table = client.table.check_usage(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableCheckUsageResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_check_usage(self, client: Morta) -> None:
        response = client.table.with_raw_response.check_usage(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableCheckUsageResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_check_usage(self, client: Morta) -> None:
        with client.table.with_streaming_response.check_usage(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableCheckUsageResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_check_usage(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.check_usage(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_create_index(self, client: Morta) -> None:
        table = client.table.create_index(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )
        assert_matches_type(TableCreateIndexResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_index(self, client: Morta) -> None:
        response = client.table.with_raw_response.create_index(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableCreateIndexResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_index(self, client: Morta) -> None:
        with client.table.with_streaming_response.create_index(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableCreateIndexResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create_index(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.create_index(
                table_id="",
                columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_rows(self, client: Morta) -> None:
        table = client.table.delete_rows(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableDeleteRowsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete_rows(self, client: Morta) -> None:
        response = client.table.with_raw_response.delete_rows(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableDeleteRowsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete_rows(self, client: Morta) -> None:
        with client.table.with_streaming_response.delete_rows(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableDeleteRowsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete_rows(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.delete_rows(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_download_csv(self, client: Morta) -> None:
        table = client.table.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_download_csv_with_all_params(self, client: Morta) -> None:
        table = client.table.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            sort="sort",
        )
        assert_matches_type(str, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_download_csv(self, client: Morta) -> None:
        response = client.table.with_raw_response.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(str, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_download_csv(self, client: Morta) -> None:
        with client.table.with_streaming_response.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(str, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_download_csv(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.download_csv(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate(self, client: Morta) -> None:
        table = client.table.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableDuplicateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate_with_all_params(self, client: Morta) -> None:
        table = client.table.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            duplicate_linked_tables=True,
            duplicate_permissions=True,
        )
        assert_matches_type(TableDuplicateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_duplicate(self, client: Morta) -> None:
        response = client.table.with_raw_response.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableDuplicateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_duplicate(self, client: Morta) -> None:
        with client.table.with_streaming_response.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableDuplicateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_duplicate(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.duplicate(
                table_id="",
                target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_get_csv_backup(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/csv-backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = client.table.get_csv_backup(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert table.is_closed
        assert table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_get_csv_backup(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/csv-backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        table = client.table.with_raw_response.get_csv_backup(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert table.is_closed is True
        assert table.http_request.headers.get("X-Stainless-Lang") == "python"
        assert table.json() == {"foo": "bar"}
        assert isinstance(table, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_get_csv_backup(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/csv-backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.table.with_streaming_response.get_csv_backup(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as table:
            assert not table.is_closed
            assert table.http_request.headers.get("X-Stainless-Lang") == "python"

            assert table.json() == {"foo": "bar"}
            assert cast(Any, table.is_closed) is True
            assert isinstance(table, StreamedBinaryAPIResponse)

        assert cast(Any, table.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_get_csv_backup(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.get_csv_backup(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_duplicated_children(self, client: Morta) -> None:
        table = client.table.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableGetDuplicatedChildrenResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_duplicated_children(self, client: Morta) -> None:
        response = client.table.with_raw_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableGetDuplicatedChildrenResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_duplicated_children(self, client: Morta) -> None:
        with client.table.with_streaming_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableGetDuplicatedChildrenResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_duplicated_children(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.get_duplicated_children(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_get_file(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/file").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = client.table.get_file(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filename="filename",
        )
        assert table.is_closed
        assert table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_get_file(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/file").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        table = client.table.with_raw_response.get_file(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filename="filename",
        )

        assert table.is_closed is True
        assert table.http_request.headers.get("X-Stainless-Lang") == "python"
        assert table.json() == {"foo": "bar"}
        assert isinstance(table, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_get_file(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/file").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.table.with_streaming_response.get_file(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filename="filename",
        ) as table:
            assert not table.is_closed
            assert table.http_request.headers.get("X-Stainless-Lang") == "python"

            assert table.json() == {"foo": "bar"}
            assert cast(Any, table.is_closed) is True
            assert isinstance(table, StreamedBinaryAPIResponse)

        assert cast(Any, table.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_get_file(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.get_file(
                table_id="",
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                filename="filename",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_statistics(self, client: Morta) -> None:
        table = client.table.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_statistics_with_all_params(self, client: Morta) -> None:
        table = client.table.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            aggregation={"foo": "string"},
            filter="filter",
        )
        assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_statistics(self, client: Morta) -> None:
        response = client.table.with_raw_response.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_statistics(self, client: Morta) -> None:
        with client.table.with_streaming_response.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_statistics(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.get_statistics(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_columns(self, client: Morta) -> None:
        table = client.table.list_columns(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableListColumnsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_columns(self, client: Morta) -> None:
        response = client.table.with_raw_response.list_columns(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableListColumnsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_columns(self, client: Morta) -> None:
        with client.table.with_streaming_response.list_columns(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableListColumnsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_columns(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.list_columns(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_joins(self, client: Morta) -> None:
        table = client.table.list_joins(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableListJoinsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_joins(self, client: Morta) -> None:
        response = client.table.with_raw_response.list_joins(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableListJoinsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_joins(self, client: Morta) -> None:
        with client.table.with_streaming_response.list_joins(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableListJoinsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_joins(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.list_joins(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_restore(self, client: Morta) -> None:
        table = client.table.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableRestoreResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_restore(self, client: Morta) -> None:
        response = client.table.with_raw_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableRestoreResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_restore(self, client: Morta) -> None:
        with client.table.with_streaming_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableRestoreResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_restore(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.restore(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_stream_rows(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = client.table.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert table.is_closed
        assert table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_stream_rows_with_all_params(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = client.table.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            page=1,
            size=1,
            sort="sort",
        )
        assert table.is_closed
        assert table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_stream_rows(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        table = client.table.with_raw_response.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert table.is_closed is True
        assert table.http_request.headers.get("X-Stainless-Lang") == "python"
        assert table.json() == {"foo": "bar"}
        assert isinstance(table, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_stream_rows(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.table.with_streaming_response.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as table:
            assert not table.is_closed
            assert table.http_request.headers.get("X-Stainless-Lang") == "python"

            assert table.json() == {"foo": "bar"}
            assert cast(Any, table.is_closed) is True
            assert isinstance(table, StreamedBinaryAPIResponse)

        assert cast(Any, table.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_stream_rows(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.stream_rows(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_truncate(self, client: Morta) -> None:
        table = client.table.truncate(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableTruncateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_truncate(self, client: Morta) -> None:
        response = client.table.with_raw_response.truncate(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableTruncateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_truncate(self, client: Morta) -> None:
        with client.table.with_streaming_response.truncate(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableTruncateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_truncate(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.truncate(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_cells(self, client: Morta) -> None:
        table = client.table.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        )
        assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_cells_with_all_params(self, client: Morta) -> None:
        table = client.table.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_cells(self, client: Morta) -> None:
        response = client.table.with_raw_response.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        table = response.parse()
        assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_cells(self, client: Morta) -> None:
        with client.table.with_streaming_response.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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

            table = response.parse()
            assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_cells(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.with_raw_response.update_cells(
                table_id="",
                cells=[
                    {
                        "column_name": "x",
                        "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "value": {},
                    }
                ],
            )


class TestAsyncTable:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.create(
            columns=[{}],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableCreateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.create(
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
                    "export_width": 0,
                    "formula": "formula",
                    "formula_enabled": True,
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
                    "morta_synced": 0,
                    "name": "name",
                    "procore_synced": 0,
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "revizto_issues_synced": 0,
                    "script": "script",
                    "script_enabled": True,
                    "thousand_separator": True,
                    "viewpoint_rfis_synced": 0,
                    "viewpoint_synced": 0,
                    "width": 0,
                }
            ],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            joins=[
                {
                    "data_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "is_one_to_many": True,
                    "join_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "join_table_name": "joinTableName",
                    "join_view_id": "joinViewId",
                    "join_view_name": "joinViewName",
                }
            ],
            type="type",
        )
        assert_matches_type(TableCreateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.create(
            columns=[{}],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableCreateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.create(
            columns=[{}],
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableCreateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableRetrieveResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=["string"],
            distinct_columns=["string"],
            filter="filter",
            ignore_cached_options=True,
            last_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            next_page_token="next_page_token",
            page=1,
            size=1,
            sort="sort",
        )
        assert_matches_type(TableRetrieveResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableRetrieveResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.retrieve(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableRetrieveResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.retrieve(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableUpdateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            allow_comments=True,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            is_reference_table=True,
            joins=[
                {
                    "data_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "is_one_to_many": True,
                    "join_columns": [
                        {
                            "source_column_id": "sourceColumnId",
                            "target_column_id": "targetColumnId",
                        }
                    ],
                    "join_table_name": "joinTableName",
                    "join_view_id": "joinViewId",
                    "join_view_name": "joinViewName",
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            keep_colours_in_sync=True,
            keep_validations_in_sync=True,
            logo="logo",
            name="name",
            sync_hourly_frequency=0,
            type="type",
        )
        assert_matches_type(TableUpdateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableUpdateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableUpdateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.update(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableDeleteResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableDeleteResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableDeleteResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_check_usage(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.check_usage(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableCheckUsageResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_check_usage(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.check_usage(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableCheckUsageResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_check_usage(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.check_usage(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableCheckUsageResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_check_usage(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.check_usage(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_index(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.create_index(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )
        assert_matches_type(TableCreateIndexResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_index(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.create_index(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableCreateIndexResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_index(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.create_index(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableCreateIndexResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create_index(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.create_index(
                table_id="",
                columns=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_rows(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.delete_rows(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableDeleteRowsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete_rows(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.delete_rows(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableDeleteRowsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete_rows(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.delete_rows(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableDeleteRowsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete_rows(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.delete_rows(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_download_csv(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_download_csv_with_all_params(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            sort="sort",
        )
        assert_matches_type(str, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_download_csv(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(str, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_download_csv(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.download_csv(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(str, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_download_csv(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.download_csv(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableDuplicateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate_with_all_params(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            duplicate_linked_tables=True,
            duplicate_permissions=True,
        )
        assert_matches_type(TableDuplicateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_duplicate(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableDuplicateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_duplicate(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.duplicate(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableDuplicateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_duplicate(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.duplicate(
                table_id="",
                target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_get_csv_backup(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/csv-backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = await async_client.table.get_csv_backup(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert table.is_closed
        assert await table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_get_csv_backup(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/csv-backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        table = await async_client.table.with_raw_response.get_csv_backup(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert table.is_closed is True
        assert table.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await table.json() == {"foo": "bar"}
        assert isinstance(table, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_get_csv_backup(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/csv-backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.table.with_streaming_response.get_csv_backup(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as table:
            assert not table.is_closed
            assert table.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await table.json() == {"foo": "bar"}
            assert cast(Any, table.is_closed) is True
            assert isinstance(table, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, table.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_get_csv_backup(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.get_csv_backup(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableGetDuplicatedChildrenResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableGetDuplicatedChildrenResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableGetDuplicatedChildrenResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.get_duplicated_children(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_get_file(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/file").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = await async_client.table.get_file(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filename="filename",
        )
        assert table.is_closed
        assert await table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_get_file(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/file").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        table = await async_client.table.with_raw_response.get_file(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filename="filename",
        )

        assert table.is_closed is True
        assert table.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await table.json() == {"foo": "bar"}
        assert isinstance(table, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_get_file(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/file").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.table.with_streaming_response.get_file(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filename="filename",
        ) as table:
            assert not table.is_closed
            assert table.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await table.json() == {"foo": "bar"}
            assert cast(Any, table.is_closed) is True
            assert isinstance(table, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, table.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_get_file(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.get_file(
                table_id="",
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                filename="filename",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_statistics(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_statistics_with_all_params(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            aggregation={"foo": "string"},
            filter="filter",
        )
        assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_statistics(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_statistics(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.get_statistics(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableGetStatisticsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_statistics(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.get_statistics(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_columns(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.list_columns(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableListColumnsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_columns(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.list_columns(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableListColumnsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_columns(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.list_columns(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableListColumnsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_columns(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.list_columns(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_joins(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.list_joins(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableListJoinsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_joins(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.list_joins(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableListJoinsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_joins(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.list_joins(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableListJoinsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_joins(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.list_joins(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_restore(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableRestoreResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_restore(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableRestoreResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_restore(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableRestoreResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_restore(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.restore(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_stream_rows(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = await async_client.table.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert table.is_closed
        assert await table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_stream_rows_with_all_params(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        table = await async_client.table.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            page=1,
            size=1,
            sort="sort",
        )
        assert table.is_closed
        assert await table.json() == {"foo": "bar"}
        assert cast(Any, table.is_closed) is True
        assert isinstance(table, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_stream_rows(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        table = await async_client.table.with_raw_response.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert table.is_closed is True
        assert table.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await table.json() == {"foo": "bar"}
        assert isinstance(table, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_stream_rows(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/table/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/rows-stream").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.table.with_streaming_response.stream_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as table:
            assert not table.is_closed
            assert table.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await table.json() == {"foo": "bar"}
            assert cast(Any, table.is_closed) is True
            assert isinstance(table, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, table.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_stream_rows(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.stream_rows(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_truncate(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.truncate(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TableTruncateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_truncate(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.truncate(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableTruncateResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_truncate(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.truncate(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableTruncateResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_truncate(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.truncate(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_cells(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            cells=[
                {
                    "column_name": "x",
                    "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "value": {},
                }
            ],
        )
        assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_cells_with_all_params(self, async_client: AsyncMorta) -> None:
        table = await async_client.table.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_cells(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.with_raw_response.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        table = await response.parse()
        assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_cells(self, async_client: AsyncMorta) -> None:
        async with async_client.table.with_streaming_response.update_cells(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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

            table = await response.parse()
            assert_matches_type(TableUpdateCellsResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_cells(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.with_raw_response.update_cells(
                table_id="",
                cells=[
                    {
                        "column_name": "x",
                        "row_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "value": {},
                    }
                ],
            )
