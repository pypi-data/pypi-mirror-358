# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.table.views import (
    RowAddResponse,
    RowListResponse,
    RowDeleteResponse,
    RowUpdateResponse,
    RowUpsertResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRows:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        row = client.table.views.rows.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        row = client.table.views.rows.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        response = client.table.views.rows.with_raw_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with client.table.views.rows.with_streaming_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.rows.with_raw_response.update(
                view_id="",
                rows=[
                    {
                        "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "row_data": {"foo": "bar"},
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Morta) -> None:
        row = client.table.views.rows.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RowListResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Morta) -> None:
        row = client.table.views.rows.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            alphabetical_column_sort=True,
            filter="filter",
            page=0,
            size=0,
            sort="sort",
        )
        assert_matches_type(RowListResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Morta) -> None:
        response = client.table.views.rows.with_raw_response.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowListResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Morta) -> None:
        with client.table.views.rows.with_streaming_response.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowListResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.rows.with_raw_response.list(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        row = client.table.views.rows.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.table.views.rows.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.table.views.rows.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowDeleteResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.rows.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_add(self, client: Morta) -> None:
        row = client.table.views.rows.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_add_with_all_params(self, client: Morta) -> None:
        row = client.table.views.rows.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        response = client.table.views.rows.with_raw_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_add(self, client: Morta) -> None:
        with client.table.views.rows.with_streaming_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.rows.with_raw_response.add(
                view_id="",
                rows=[{"row_data": {"foo": "bar"}}],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert(self, client: Morta) -> None:
        row = client.table.views.rows.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        )
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert_with_all_params(self, client: Morta) -> None:
        row = client.table.views.rows.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        response = client.table.views.rows.with_raw_response.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with client.table.views.rows.with_streaming_response.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            client.table.views.rows.with_raw_response.upsert(
                view_id="",
                rows=[{"row_data": {"foo": "bar"}}],
                upsert_column_name="upsertColumnName",
            )


class TestAsyncRows:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        row = await async_client.table.views.rows.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        response = await async_client.table.views.rows.with_raw_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        async with async_client.table.views.rows.with_streaming_response.update(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.rows.with_raw_response.update(
                view_id="",
                rows=[
                    {
                        "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "row_data": {"foo": "bar"},
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RowListResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            alphabetical_column_sort=True,
            filter="filter",
            page=0,
            size=0,
            sort="sort",
        )
        assert_matches_type(RowListResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.rows.with_raw_response.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowListResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.rows.with_streaming_response.list(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowListResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.rows.with_raw_response.list(
                view_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.views.rows.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.rows.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowDeleteResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.rows.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_add(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_add_with_all_params(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        response = await async_client.table.views.rows.with_raw_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowAddResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncMorta) -> None:
        async with async_client.table.views.rows.with_streaming_response.add(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.rows.with_raw_response.add(
                view_id="",
                rows=[{"row_data": {"foo": "bar"}}],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rows=[{"row_data": {"foo": "bar"}}],
            upsert_column_name="upsertColumnName",
        )
        assert_matches_type(RowUpsertResponse, row, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert_with_all_params(self, async_client: AsyncMorta) -> None:
        row = await async_client.table.views.rows.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        response = await async_client.table.views.rows.with_raw_response.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        async with async_client.table.views.rows.with_streaming_response.upsert(
            view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_id` but received ''"):
            await async_client.table.views.rows.with_raw_response.upsert(
                view_id="",
                rows=[{"row_data": {"foo": "bar"}}],
                upsert_column_name="upsertColumnName",
            )
