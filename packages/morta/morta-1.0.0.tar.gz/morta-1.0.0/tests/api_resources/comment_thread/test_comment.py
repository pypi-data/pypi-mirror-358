# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.comment_thread import (
    CommentCreateResponse,
    CommentDeleteResponse,
    CommentUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestComment:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        comment = client.comment_thread.comment.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )
        assert_matches_type(CommentCreateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        comment = client.comment_thread.comment.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(CommentCreateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.comment_thread.comment.with_raw_response.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment = response.parse()
        assert_matches_type(CommentCreateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.comment_thread.comment.with_streaming_response.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment = response.parse()
            assert_matches_type(CommentCreateResponse, comment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            client.comment_thread.comment.with_raw_response.create(
                comment_thread_id="",
                comment_text="commentText",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        comment = client.comment_thread.comment.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )
        assert_matches_type(CommentUpdateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        comment = client.comment_thread.comment.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(CommentUpdateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.comment_thread.comment.with_raw_response.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment = response.parse()
        assert_matches_type(CommentUpdateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.comment_thread.comment.with_streaming_response.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment = response.parse()
            assert_matches_type(CommentUpdateResponse, comment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            client.comment_thread.comment.with_raw_response.update(
                comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                comment_thread_id="",
                comment_text="commentText",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_id` but received ''"):
            client.comment_thread.comment.with_raw_response.update(
                comment_id="",
                comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                comment_text="commentText",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        comment = client.comment_thread.comment.delete(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentDeleteResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.comment_thread.comment.with_raw_response.delete(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment = response.parse()
        assert_matches_type(CommentDeleteResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.comment_thread.comment.with_streaming_response.delete(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment = response.parse()
            assert_matches_type(CommentDeleteResponse, comment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            client.comment_thread.comment.with_raw_response.delete(
                comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                comment_thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_id` but received ''"):
            client.comment_thread.comment.with_raw_response.delete(
                comment_id="",
                comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncComment:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        comment = await async_client.comment_thread.comment.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )
        assert_matches_type(CommentCreateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        comment = await async_client.comment_thread.comment.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(CommentCreateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.comment.with_raw_response.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment = await response.parse()
        assert_matches_type(CommentCreateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.comment.with_streaming_response.create(
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment = await response.parse()
            assert_matches_type(CommentCreateResponse, comment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            await async_client.comment_thread.comment.with_raw_response.create(
                comment_thread_id="",
                comment_text="commentText",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        comment = await async_client.comment_thread.comment.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )
        assert_matches_type(CommentUpdateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        comment = await async_client.comment_thread.comment.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(CommentUpdateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.comment.with_raw_response.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment = await response.parse()
        assert_matches_type(CommentUpdateResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.comment.with_streaming_response.update(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_text="commentText",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment = await response.parse()
            assert_matches_type(CommentUpdateResponse, comment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            await async_client.comment_thread.comment.with_raw_response.update(
                comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                comment_thread_id="",
                comment_text="commentText",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_id` but received ''"):
            await async_client.comment_thread.comment.with_raw_response.update(
                comment_id="",
                comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                comment_text="commentText",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        comment = await async_client.comment_thread.comment.delete(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentDeleteResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.comment.with_raw_response.delete(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment = await response.parse()
        assert_matches_type(CommentDeleteResponse, comment, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.comment.with_streaming_response.delete(
            comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment = await response.parse()
            assert_matches_type(CommentDeleteResponse, comment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            await async_client.comment_thread.comment.with_raw_response.delete(
                comment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                comment_thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_id` but received ''"):
            await async_client.comment_thread.comment.with_raw_response.delete(
                comment_id="",
                comment_thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
