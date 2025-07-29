# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.user import (
    ApikeyCreateResponse,
    ApikeyDeleteResponse,
    ApikeyUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestApikey:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        apikey = client.user.apikey.create(
            access_level=0,
        )
        assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        apikey = client.user.apikey.create(
            access_level=0,
            document_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            name="name",
            project_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            table_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.user.apikey.with_raw_response.create(
            access_level=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        apikey = response.parse()
        assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.user.apikey.with_streaming_response.create(
            access_level=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            apikey = response.parse()
            assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        apikey = client.user.apikey.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
        )
        assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        apikey = client.user.apikey.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
            document_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            name="name",
            project_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            table_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.user.apikey.with_raw_response.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        apikey = response.parse()
        assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.user.apikey.with_streaming_response.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            apikey = response.parse()
            assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_key_id` but received ''"):
            client.user.apikey.with_raw_response.update(
                api_key_id="",
                access_level=0,
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        apikey = client.user.apikey.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ApikeyDeleteResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.user.apikey.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        apikey = response.parse()
        assert_matches_type(ApikeyDeleteResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.user.apikey.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            apikey = response.parse()
            assert_matches_type(ApikeyDeleteResponse, apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_key_id` but received ''"):
            client.user.apikey.with_raw_response.delete(
                "",
            )


class TestAsyncApikey:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        apikey = await async_client.user.apikey.create(
            access_level=0,
        )
        assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        apikey = await async_client.user.apikey.create(
            access_level=0,
            document_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            name="name",
            project_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            table_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.apikey.with_raw_response.create(
            access_level=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        apikey = await response.parse()
        assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.user.apikey.with_streaming_response.create(
            access_level=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            apikey = await response.parse()
            assert_matches_type(ApikeyCreateResponse, apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        apikey = await async_client.user.apikey.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
        )
        assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        apikey = await async_client.user.apikey.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
            document_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            name="name",
            project_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            table_restrictions=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.apikey.with_raw_response.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        apikey = await response.parse()
        assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.user.apikey.with_streaming_response.update(
            api_key_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            access_level=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            apikey = await response.parse()
            assert_matches_type(ApikeyUpdateResponse, apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_key_id` but received ''"):
            await async_client.user.apikey.with_raw_response.update(
                api_key_id="",
                access_level=0,
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        apikey = await async_client.user.apikey.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ApikeyDeleteResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.apikey.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        apikey = await response.parse()
        assert_matches_type(ApikeyDeleteResponse, apikey, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.user.apikey.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            apikey = await response.parse()
            assert_matches_type(ApikeyDeleteResponse, apikey, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_key_id` but received ''"):
            await async_client.user.apikey.with_raw_response.delete(
                "",
            )
