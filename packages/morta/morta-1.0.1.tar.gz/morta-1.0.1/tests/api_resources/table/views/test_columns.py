# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.table.views import (
    ColumnAddResponse,
    ColumnUpdateResponse,
    ColumnDistinctResponse,
    ColumnFormulaInfoResponse,
    ColumnAIFormulaHelperResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestColumns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        column = client.table.views.columns.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        column = client.table.views.columns.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
            display_validation_error=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            hard_validation=True,
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
            locked=True,
            morta_synced=0,
            name="name",
            procore_synced=0,
            public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            required=True,
            revizto_issues_synced=0,
            script="script",
            script_enabled=True,
            sort_order=0,
            string_validation="stringValidation",
            thousand_separator=True,
            validation_message="validationMessage",
            validation_no_blanks=True,
            validation_no_duplicates=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=100,
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.table.views.columns.with_raw_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.table.views.columns.with_streaming_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnUpdateResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.columns.with_raw_response.update(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.views.columns.with_raw_response.update(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_add(self, client: Morta) -> None:
        column = client.table.views.columns.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
        )
        assert_matches_type(ColumnAddResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_add_with_all_params(self, client: Morta) -> None:
        column = client.table.views.columns.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
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
            display_validation_error=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            hard_validation=True,
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
            string_validation="stringValidation",
            thousand_separator=True,
            validation_message="validationMessage",
            validation_no_blanks=True,
            validation_no_duplicates=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=0,
        )
        assert_matches_type(ColumnAddResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_add(self, client: Morta) -> None:
        response = client.table.views.columns.with_raw_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnAddResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_add(self, client: Morta) -> None:
        with client.table.views.columns.with_streaming_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnAddResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_add(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.columns.with_raw_response.add(
                view_id="",
                locked=True,
                required=True,
                sort_order=0,
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_ai_formula_helper(self, client: Morta) -> None:
        column = client.table.views.columns.ai_formula_helper(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            text="text",
        )
        assert_matches_type(ColumnAIFormulaHelperResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_ai_formula_helper(self, client: Morta) -> None:
        response = client.table.views.columns.with_raw_response.ai_formula_helper(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnAIFormulaHelperResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_ai_formula_helper(self, client: Morta) -> None:
        with client.table.views.columns.with_streaming_response.ai_formula_helper(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnAIFormulaHelperResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_ai_formula_helper(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.columns.with_raw_response.ai_formula_helper(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
                text="text",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.views.columns.with_raw_response.ai_formula_helper(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                text="text",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_distinct(self, client: Morta) -> None:
        column = client.table.views.columns.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnDistinctResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_distinct_with_all_params(self, client: Morta) -> None:
        column = client.table.views.columns.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            group_columns=["string"],
        )
        assert_matches_type(ColumnDistinctResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_distinct(self, client: Morta) -> None:
        response = client.table.views.columns.with_raw_response.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnDistinctResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_distinct(self, client: Morta) -> None:
        with client.table.views.columns.with_streaming_response.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnDistinctResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_distinct(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.columns.with_raw_response.distinct(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.views.columns.with_raw_response.distinct(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_formula_info(self, client: Morta) -> None:
        column = client.table.views.columns.formula_info(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnFormulaInfoResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_formula_info(self, client: Morta) -> None:
        response = client.table.views.columns.with_raw_response.formula_info(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = response.parse()
        assert_matches_type(ColumnFormulaInfoResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_formula_info(self, client: Morta) -> None:
        with client.table.views.columns.with_streaming_response.formula_info(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = response.parse()
            assert_matches_type(ColumnFormulaInfoResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_formula_info(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.columns.with_raw_response.formula_info(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            client.table.views.columns.with_raw_response.formula_info(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncColumns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
            display_validation_error=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            hard_validation=True,
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
            locked=True,
            morta_synced=0,
            name="name",
            procore_synced=0,
            public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            required=True,
            revizto_issues_synced=0,
            script="script",
            script_enabled=True,
            sort_order=0,
            string_validation="stringValidation",
            thousand_separator=True,
            validation_message="validationMessage",
            validation_no_blanks=True,
            validation_no_duplicates=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=100,
        )
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.columns.with_raw_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnUpdateResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.columns.with_streaming_response.update(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnUpdateResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.update(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.update(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_add(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
        )
        assert_matches_type(ColumnAddResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_add_with_all_params(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
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
            display_validation_error=True,
            export_width=0,
            formula="formula",
            formula_enabled=True,
            hard_validation=True,
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
            string_validation="stringValidation",
            thousand_separator=True,
            validation_message="validationMessage",
            validation_no_blanks=True,
            validation_no_duplicates=True,
            viewpoint_rfis_synced=0,
            viewpoint_synced=0,
            width=0,
        )
        assert_matches_type(ColumnAddResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_add(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.columns.with_raw_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnAddResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.columns.with_streaming_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locked=True,
            required=True,
            sort_order=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnAddResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_add(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.add(
                view_id="",
                locked=True,
                required=True,
                sort_order=0,
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_ai_formula_helper(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.ai_formula_helper(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            text="text",
        )
        assert_matches_type(ColumnAIFormulaHelperResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_ai_formula_helper(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.columns.with_raw_response.ai_formula_helper(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnAIFormulaHelperResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_ai_formula_helper(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.columns.with_streaming_response.ai_formula_helper(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnAIFormulaHelperResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_ai_formula_helper(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.ai_formula_helper(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
                text="text",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.ai_formula_helper(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                text="text",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_distinct(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnDistinctResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_distinct_with_all_params(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            filter="filter",
            group_columns=["string"],
        )
        assert_matches_type(ColumnDistinctResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_distinct(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.columns.with_raw_response.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnDistinctResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_distinct(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.columns.with_streaming_response.distinct(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnDistinctResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_distinct(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.distinct(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.distinct(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_formula_info(self, async_client: AsyncMorta) -> None:
        column = await async_client.table.views.columns.formula_info(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ColumnFormulaInfoResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_formula_info(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.columns.with_raw_response.formula_info(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column = await response.parse()
        assert_matches_type(ColumnFormulaInfoResponse, column, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_formula_info(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.columns.with_streaming_response.formula_info(
            column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column = await response.parse()
            assert_matches_type(ColumnFormulaInfoResponse, column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_formula_info(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.formula_info(
                column_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                view_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `column_id` but received ''"):
            await async_client.table.views.columns.with_raw_response.formula_info(
                column_id="",
                view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
