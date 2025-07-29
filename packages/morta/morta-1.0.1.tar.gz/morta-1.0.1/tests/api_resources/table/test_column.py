# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.table import (
    ColumnCreateResponse,
    ColumnDeleteResponse,
    ColumnUpdateResponse,
    ColumnRestoreResponse,
    ColumnCheckViewsResponse,
    ColumnGetDistinctValuesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestColumn:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        column = client.table.column.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnCreateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        column = client.table.column.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            aconex_synced=0,
            aconex_workflows_synced=0,
            aggregate=0,
            alter_options={
                "date_conversion_format": "DD/MM/YYYY",
                "run_script_on_all_cells": True,
            },
            asite_documents_synced=0,
            asite_forms_synced=0,
            autodesk_bim360_checklists_synced=0,
            autodesk_bim360_issues_synced=0,
            autodesk_bim360_models_synced=0,
            autodesk_bim360_synced=0,
            autodesk_bim360_users_synced=0,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            date_format="dateFormat",
            decimal_places=0,
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
            display_link=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            header_background_color="headerBackgroundColor",
            header_text_color="headerTextColor",
            is_indexed=True,
            is_joined=True,
            kind="text",
            kind_options={
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
            morta_synced=0,
            name="name",
            procore_synced=0,
            public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            revizto_issues_synced=0,
            script="script",
            script_enabled=True,
            thousand_separator=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=0,
        )
        assert_matches_type(ColumnCreateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.table.column.with_raw_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnCreateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.table.column.with_streaming_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnCreateResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.column.with_raw_response.create(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        column = client.table.column.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        column = client.table.column.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            aconex_synced=0,
            aconex_workflows_synced=0,
            aggregate=0,
            alter_options={
                "date_conversion_format": "DD/MM/YYYY",
                "run_script_on_all_cells": True,
            },
            asite_documents_synced=0,
            asite_forms_synced=0,
            autodesk_bim360_checklists_synced=0,
            autodesk_bim360_issues_synced=0,
            autodesk_bim360_models_synced=0,
            autodesk_bim360_synced=0,
            autodesk_bim360_users_synced=0,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            date_format="dateFormat",
            decimal_places=0,
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
            display_link=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            header_background_color="headerBackgroundColor",
            header_text_color="headerTextColor",
            is_indexed=True,
            is_joined=True,
            kind="text",
            kind_options={
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
            morta_synced=0,
            name="name",
            procore_synced=0,
            public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            revizto_issues_synced=0,
            script="script",
            script_enabled=True,
            thousand_separator=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=0,
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.table.column.with_raw_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.table.column.with_streaming_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnUpdateResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.column.with_raw_response.update(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.column.with_raw_response.update(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        column = client.table.column.delete(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnDeleteResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.table.column.with_raw_response.delete(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnDeleteResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.table.column.with_streaming_response.delete(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnDeleteResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.column.with_raw_response.delete(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.column.with_raw_response.delete(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_check_views(self, client: Morta) -> None:
        column = client.table.column.check_views(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnCheckViewsResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_check_views(self, client: Morta) -> None:
        response = client.table.column.with_raw_response.check_views(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnCheckViewsResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_check_views(self, client: Morta) -> None:
        with client.table.column.with_streaming_response.check_views(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnCheckViewsResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_check_views(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.column.with_raw_response.check_views(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.column.with_raw_response.check_views(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_distinct_values(self, client: Morta) -> None:
        column = client.table.column.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_distinct_values_with_all_params(self, client: Morta) -> None:
        column = client.table.column.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            group_columns=["string"],
        )
        assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_distinct_values(self, client: Morta) -> None:
        response = client.table.column.with_raw_response.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_distinct_values(self, client: Morta) -> None:
        with client.table.column.with_streaming_response.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_distinct_values(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.column.with_raw_response.get_distinct_values(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.column.with_raw_response.get_distinct_values(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_restore(self, client: Morta) -> None:
        column = client.table.column.restore(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnRestoreResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_restore(self, client: Morta) -> None:
        response = client.table.column.with_raw_response.restore(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnRestoreResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_restore(self, client: Morta) -> None:
        with client.table.column.with_streaming_response.restore(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnRestoreResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_restore(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.column.with_raw_response.restore(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.column.with_raw_response.restore(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncColumn:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnCreateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            aconex_synced=0,
            aconex_workflows_synced=0,
            aggregate=0,
            alter_options={
                "date_conversion_format": "DD/MM/YYYY",
                "run_script_on_all_cells": True,
            },
            asite_documents_synced=0,
            asite_forms_synced=0,
            autodesk_bim360_checklists_synced=0,
            autodesk_bim360_issues_synced=0,
            autodesk_bim360_models_synced=0,
            autodesk_bim360_synced=0,
            autodesk_bim360_users_synced=0,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            date_format="dateFormat",
            decimal_places=0,
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
            display_link=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            header_background_color="headerBackgroundColor",
            header_text_color="headerTextColor",
            is_indexed=True,
            is_joined=True,
            kind="text",
            kind_options={
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
            morta_synced=0,
            name="name",
            procore_synced=0,
            public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            revizto_issues_synced=0,
            script="script",
            script_enabled=True,
            thousand_separator=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=0,
        )
        assert_matches_type(ColumnCreateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.column.with_raw_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnCreateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.table.column.with_streaming_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnCreateResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.column.with_raw_response.create(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            aconex_synced=0,
            aconex_workflows_synced=0,
            aggregate=0,
            alter_options={
                "date_conversion_format": "DD/MM/YYYY",
                "run_script_on_all_cells": True,
            },
            asite_documents_synced=0,
            asite_forms_synced=0,
            autodesk_bim360_checklists_synced=0,
            autodesk_bim360_issues_synced=0,
            autodesk_bim360_models_synced=0,
            autodesk_bim360_synced=0,
            autodesk_bim360_users_synced=0,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            date_format="dateFormat",
            decimal_places=0,
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
            display_link=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            header_background_color="headerBackgroundColor",
            header_text_color="headerTextColor",
            is_indexed=True,
            is_joined=True,
            kind="text",
            kind_options={
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
            morta_synced=0,
            name="name",
            procore_synced=0,
            public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            revizto_issues_synced=0,
            script="script",
            script_enabled=True,
            thousand_separator=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=0,
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.column.with_raw_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.table.column.with_streaming_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnUpdateResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.column.with_raw_response.update(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.column.with_raw_response.update(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.delete(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnDeleteResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.column.with_raw_response.delete(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnDeleteResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.table.column.with_streaming_response.delete(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnDeleteResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.column.with_raw_response.delete(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.column.with_raw_response.delete(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_check_views(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.check_views(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnCheckViewsResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_check_views(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.column.with_raw_response.check_views(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnCheckViewsResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_check_views(self, async_client: AsyncMorta) -> None:
        async with async_client.table.column.with_streaming_response.check_views(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnCheckViewsResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_check_views(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.column.with_raw_response.check_views(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.column.with_raw_response.check_views(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_distinct_values(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_distinct_values_with_all_params(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            group_columns=["string"],
        )
        assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_distinct_values(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.column.with_raw_response.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_distinct_values(self, async_client: AsyncMorta) -> None:
        async with async_client.table.column.with_streaming_response.get_distinct_values(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnGetDistinctValuesResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_distinct_values(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.column.with_raw_response.get_distinct_values(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.column.with_raw_response.get_distinct_values(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_restore(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.column.restore(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnRestoreResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_restore(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.column.with_raw_response.restore(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnRestoreResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_restore(self, async_client: AsyncMorta) -> None:
        async with async_client.table.column.with_streaming_response.restore(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnRestoreResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_restore(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.column.with_raw_response.restore(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.column.with_raw_response.restore(
                column_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
