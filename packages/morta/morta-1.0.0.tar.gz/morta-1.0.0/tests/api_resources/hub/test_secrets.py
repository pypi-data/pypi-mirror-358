# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.hub import (
    SecretListResponse,
    SecretCreateResponse,
    SecretDeleteResponse,
    SecretUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSecrets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        secret = client.hub.secrets.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )
        assert_matches_type(SecretCreateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.hub.secrets.with_raw_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(SecretCreateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.hub.secrets.with_streaming_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(SecretCreateResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.secrets.with_raw_response.create(
                hub_id="",
                name="name",
                value="value",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        secret = client.hub.secrets.update(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )
        assert_matches_type(SecretUpdateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.hub.secrets.with_raw_response.update(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(SecretUpdateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.hub.secrets.with_streaming_response.update(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(SecretUpdateResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.secrets.with_raw_response.update(
                secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
                name="name",
                value="value",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            client.hub.secrets.with_raw_response.update(
                secret_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                name="name",
                value="value",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Morta) -> None:
        secret = client.hub.secrets.list(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Morta) -> None:
        response = client.hub.secrets.with_raw_response.list(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Morta) -> None:
        with client.hub.secrets.with_streaming_response.list(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(SecretListResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.secrets.with_raw_response.list(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        secret = client.hub.secrets.delete(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SecretDeleteResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.hub.secrets.with_raw_response.delete(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(SecretDeleteResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.hub.secrets.with_streaming_response.delete(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(SecretDeleteResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.secrets.with_raw_response.delete(
                secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            client.hub.secrets.with_raw_response.delete(
                secret_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncSecrets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        secret = await async_client.hub.secrets.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )
        assert_matches_type(SecretCreateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.secrets.with_raw_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(SecretCreateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.secrets.with_streaming_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(SecretCreateResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.secrets.with_raw_response.create(
                hub_id="",
                name="name",
                value="value",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        secret = await async_client.hub.secrets.update(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )
        assert_matches_type(SecretUpdateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.secrets.with_raw_response.update(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(SecretUpdateResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.secrets.with_streaming_response.update(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            value="value",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(SecretUpdateResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.secrets.with_raw_response.update(
                secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
                name="name",
                value="value",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            await async_client.hub.secrets.with_raw_response.update(
                secret_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                name="name",
                value="value",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncMorta) -> None:
        secret = await async_client.hub.secrets.list(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.secrets.with_raw_response.list(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.secrets.with_streaming_response.list(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(SecretListResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.secrets.with_raw_response.list(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        secret = await async_client.hub.secrets.delete(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SecretDeleteResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.secrets.with_raw_response.delete(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(SecretDeleteResponse, secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.secrets.with_streaming_response.delete(
            secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(SecretDeleteResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.secrets.with_raw_response.delete(
                secret_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            await async_client.hub.secrets.with_raw_response.delete(
                secret_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
