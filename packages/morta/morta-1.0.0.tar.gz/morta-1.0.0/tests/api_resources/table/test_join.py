# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.table import (
    JoinCreateResponse,
    JoinDeleteResponse,
    JoinUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestJoin:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        join = client.table.join.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JoinCreateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        join = client.table.join.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data_columns=["string"],
            is_one_to_many=True,
            join_columns=[
                {
                    "source_column_id": "sourceColumnId",
                    "target_column_id": "targetColumnId",
                }
            ],
            join_view_id="joinViewId",
        )
        assert_matches_type(JoinCreateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.table.join.with_raw_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        join = response.parse()
        assert_matches_type(JoinCreateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.table.join.with_streaming_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            join = response.parse()
            assert_matches_type(JoinCreateResponse, join, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.join.with_raw_response.create(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        join = client.table.join.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JoinUpdateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        join = client.table.join.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data_columns=["string"],
            is_one_to_many=True,
            join_columns=[
                {
                    "source_column_id": "sourceColumnId",
                    "target_column_id": "targetColumnId",
                }
            ],
            join_view_id="joinViewId",
        )
        assert_matches_type(JoinUpdateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.table.join.with_raw_response.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        join = response.parse()
        assert_matches_type(JoinUpdateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.table.join.with_streaming_response.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            join = response.parse()
            assert_matches_type(JoinUpdateResponse, join, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.join.with_raw_response.update(
                join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `join_id` but received ''"):
            client.table.join.with_raw_response.update(
                join_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        join = client.table.join.delete(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JoinDeleteResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.table.join.with_raw_response.delete(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        join = response.parse()
        assert_matches_type(JoinDeleteResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.table.join.with_streaming_response.delete(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            join = response.parse()
            assert_matches_type(JoinDeleteResponse, join, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.join.with_raw_response.delete(
                join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `join_id` but received ''"):
            client.table.join.with_raw_response.delete(
                join_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncJoin:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        join = await async_client.table.join.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JoinCreateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        join = await async_client.table.join.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data_columns=["string"],
            is_one_to_many=True,
            join_columns=[
                {
                    "source_column_id": "sourceColumnId",
                    "target_column_id": "targetColumnId",
                }
            ],
            join_view_id="joinViewId",
        )
        assert_matches_type(JoinCreateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.join.with_raw_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        join = await response.parse()
        assert_matches_type(JoinCreateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.table.join.with_streaming_response.create(
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            join = await response.parse()
            assert_matches_type(JoinCreateResponse, join, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.join.with_raw_response.create(
                table_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        join = await async_client.table.join.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JoinUpdateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        join = await async_client.table.join.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data_columns=["string"],
            is_one_to_many=True,
            join_columns=[
                {
                    "source_column_id": "sourceColumnId",
                    "target_column_id": "targetColumnId",
                }
            ],
            join_view_id="joinViewId",
        )
        assert_matches_type(JoinUpdateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.join.with_raw_response.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        join = await response.parse()
        assert_matches_type(JoinUpdateResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.table.join.with_streaming_response.update(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            join = await response.parse()
            assert_matches_type(JoinUpdateResponse, join, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.join.with_raw_response.update(
                join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `join_id` but received ''"):
            await async_client.table.join.with_raw_response.update(
                join_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        join = await async_client.table.join.delete(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JoinDeleteResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.join.with_raw_response.delete(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        join = await response.parse()
        assert_matches_type(JoinDeleteResponse, join, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.table.join.with_streaming_response.delete(
            join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            join = await response.parse()
            assert_matches_type(JoinDeleteResponse, join, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.join.with_raw_response.delete(
                join_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `join_id` but received ''"):
            await async_client.table.join.with_raw_response.delete(
                join_id="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
