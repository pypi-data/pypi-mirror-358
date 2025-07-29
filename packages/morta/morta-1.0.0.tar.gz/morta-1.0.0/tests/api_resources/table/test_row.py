# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta._utils import parse_datetime
from morta.types.table import (
    RowAddResponse,
    RowUpdateResponse,
    RowUpsertResponse,
    RowGetRowsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRow:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        row = client.table.row.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                }
            ],
        )
        assert_matches_type(RowUpdateResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        row = client.table.row.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "sort_order": 0,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(RowUpdateResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.table.row.with_raw_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowUpdateResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.table.row.with_streaming_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowUpdateResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.row.with_raw_response.update(
                table_id="",
                rows=[
                    {
                        "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "row_data": {"foo": "bar"},
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_add(self, client: Morta) -> None:
        row = client.table.row.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_add_with_all_params(self, client: Morta) -> None:
        row = client.table.row.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "row_data": {"foo": "bar"},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "sort_order": 0,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_add(self, client: Morta) -> None:
        response = client.table.row.with_raw_response.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_add(self, client: Morta) -> None:
        with client.table.row.with_streaming_response.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowAddResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_add(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.row.with_raw_response.add(
                table_id="",
                rows=[{"row_data": {"foo": "bar"}}],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_rows(self, client: Morta) -> None:
        row = client.table.row.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RowGetRowsResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_rows_with_all_params(self, client: Morta) -> None:
        row = client.table.row.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=["string"],
            distinct_columns=["string"],
            filter="filter",
            last_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            next_page_token="next_page_token",
            page=1,
            size=1,
            sort="sort",
        )
        assert_matches_type(RowGetRowsResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_rows(self, client: Morta) -> None:
        response = client.table.row.with_raw_response.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowGetRowsResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_rows(self, client: Morta) -> None:
        with client.table.row.with_streaming_response.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowGetRowsResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_rows(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.row.with_raw_response.get_rows(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert(self, client: Morta) -> None:
        row = client.table.row.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        )
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert_with_all_params(self, client: Morta) -> None:
        row = client.table.row.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "row_data": {"foo": "bar"},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "sort_order": 0,
                }
            ],
            upsert_column_name="upsertColumnName",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upsert(self, client: Morta) -> None:
        response = client.table.row.with_raw_response.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upsert(self, client: Morta) -> None:
        with client.table.row.with_streaming_response.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowUpsertResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_upsert(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.row.with_raw_response.upsert(
                table_id="",
                rows=[{"row_data": {"foo": "bar"}}],
                upsert_column_name="upsertColumnName",
            )


class TestAsyncRow:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                }
            ],
        )
        assert_matches_type(RowUpdateResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "sort_order": 0,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(RowUpdateResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.row.with_raw_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowUpdateResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.table.row.with_streaming_response.update(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "row_data": {"foo": "bar"},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowUpdateResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.row.with_raw_response.update(
                table_id="",
                rows=[
                    {
                        "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "row_data": {"foo": "bar"},
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_add(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_add_with_all_params(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "row_data": {"foo": "bar"},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "sort_order": 0,
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_add(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.row.with_raw_response.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncMorta) -> None:
        async with async_client.table.row.with_streaming_response.add(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowAddResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_add(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.row.with_raw_response.add(
                table_id="",
                rows=[{"row_data": {"foo": "bar"}}],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_rows(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RowGetRowsResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_rows_with_all_params(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            columns=["string"],
            distinct_columns=["string"],
            filter="filter",
            last_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            next_page_token="next_page_token",
            page=1,
            size=1,
            sort="sort",
        )
        assert_matches_type(RowGetRowsResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_rows(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.row.with_raw_response.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowGetRowsResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_rows(self, async_client: AsyncMorta) -> None:
        async with async_client.table.row.with_streaming_response.get_rows(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowGetRowsResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_rows(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.row.with_raw_response.get_rows(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        )
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert_with_all_params(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.row.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[
                {
                    "row_data": {"foo": "bar"},
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "sort_order": 0,
                }
            ],
            upsert_column_name="upsertColumnName",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upsert(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.row.with_raw_response.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upsert(self, async_client: AsyncMorta) -> None:
        async with async_client.table.row.with_streaming_response.upsert(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowUpsertResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_upsert(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.row.with_raw_response.upsert(
                table_id="",
                rows=[{"row_data": {"foo": "bar"}}],
                upsert_column_name="upsertColumnName",
            )
