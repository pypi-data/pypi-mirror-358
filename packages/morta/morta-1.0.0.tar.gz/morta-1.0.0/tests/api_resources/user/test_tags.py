# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.user import (
    TagAddResponse,
    TagDeleteResponse,
    TagBulkApplyResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTags:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        tag = client.user.tags.delete(
            tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TagDeleteResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.user.tags.with_raw_response.delete(
            tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagDeleteResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.user.tags.with_streaming_response.delete(
            tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagDeleteResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.user.tags.with_raw_response.delete(
                tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                user_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tag_id` but received ''"):
            client.user.tags.with_raw_response.delete(
                tag_id="",
                user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_add(self, client: Morta) -> None:
        tag = client.user.tags.add(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_id="tagReferenceId",
        )
        assert_matches_type(TagAddResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_add(self, client: Morta) -> None:
        response = client.user.tags.with_raw_response.add(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_id="tagReferenceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagAddResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_add(self, client: Morta) -> None:
        with client.user.tags.with_streaming_response.add(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_id="tagReferenceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagAddResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_add(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.user.tags.with_raw_response.add(
                user_id="",
                tag_reference_id="tagReferenceId",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_bulk_apply(self, client: Morta) -> None:
        tag = client.user.tags.bulk_apply(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_ids=["string"],
        )
        assert_matches_type(TagBulkApplyResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_bulk_apply(self, client: Morta) -> None:
        response = client.user.tags.with_raw_response.bulk_apply(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = response.parse()
        assert_matches_type(TagBulkApplyResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_bulk_apply(self, client: Morta) -> None:
        with client.user.tags.with_streaming_response.bulk_apply(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = response.parse()
            assert_matches_type(TagBulkApplyResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_bulk_apply(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.user.tags.with_raw_response.bulk_apply(
                user_id="",
                project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                tag_reference_ids=["string"],
            )


class TestAsyncTags:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        tag = await async_client.user.tags.delete(
            tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TagDeleteResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.tags.with_raw_response.delete(
            tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagDeleteResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.user.tags.with_streaming_response.delete(
            tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagDeleteResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.user.tags.with_raw_response.delete(
                tag_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                user_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tag_id` but received ''"):
            await async_client.user.tags.with_raw_response.delete(
                tag_id="",
                user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_add(self, async_client: AsyncMorta) -> None:
        tag = await async_client.user.tags.add(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_id="tagReferenceId",
        )
        assert_matches_type(TagAddResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_add(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.tags.with_raw_response.add(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_id="tagReferenceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagAddResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncMorta) -> None:
        async with async_client.user.tags.with_streaming_response.add(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_id="tagReferenceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagAddResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_add(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.user.tags.with_raw_response.add(
                user_id="",
                tag_reference_id="tagReferenceId",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_bulk_apply(self, async_client: AsyncMorta) -> None:
        tag = await async_client.user.tags.bulk_apply(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_ids=["string"],
        )
        assert_matches_type(TagBulkApplyResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_bulk_apply(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.tags.with_raw_response.bulk_apply(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tag = await response.parse()
        assert_matches_type(TagBulkApplyResponse, tag, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_bulk_apply(self, async_client: AsyncMorta) -> None:
        async with async_client.user.tags.with_streaming_response.bulk_apply(
            user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            tag_reference_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tag = await response.parse()
            assert_matches_type(TagBulkApplyResponse, tag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_bulk_apply(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.user.tags.with_raw_response.bulk_apply(
                user_id="",
                project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                tag_reference_ids=["string"],
            )
