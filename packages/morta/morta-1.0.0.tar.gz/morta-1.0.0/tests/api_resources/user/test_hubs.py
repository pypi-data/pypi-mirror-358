# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.user import (
    HubListResponse,
    HubListTagsResponse,
    HubTogglePinResponse,
    HubListFavouritesResponse,
    HubToggleFavouriteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHubs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Morta) -> None:
        hub = client.user.hubs.list()
        assert_matches_type(HubListResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Morta) -> None:
        response = client.user.hubs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubListResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Morta) -> None:
        with client.user.hubs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubListResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_favourites(self, client: Morta) -> None:
        hub = client.user.hubs.list_favourites()
        assert_matches_type(HubListFavouritesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_favourites(self, client: Morta) -> None:
        response = client.user.hubs.with_raw_response.list_favourites()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubListFavouritesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_favourites(self, client: Morta) -> None:
        with client.user.hubs.with_streaming_response.list_favourites() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubListFavouritesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_tags(self, client: Morta) -> None:
        hub = client.user.hubs.list_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubListTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_tags(self, client: Morta) -> None:
        response = client.user.hubs.with_raw_response.list_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubListTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_tags(self, client: Morta) -> None:
        with client.user.hubs.with_streaming_response.list_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubListTagsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_tags(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.user.hubs.with_raw_response.list_tags(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_toggle_favourite(self, client: Morta) -> None:
        hub = client.user.hubs.toggle_favourite(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubToggleFavouriteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_toggle_favourite(self, client: Morta) -> None:
        response = client.user.hubs.with_raw_response.toggle_favourite(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubToggleFavouriteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_toggle_favourite(self, client: Morta) -> None:
        with client.user.hubs.with_streaming_response.toggle_favourite(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubToggleFavouriteResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_toggle_favourite(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.user.hubs.with_raw_response.toggle_favourite(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_toggle_pin(self, client: Morta) -> None:
        hub = client.user.hubs.toggle_pin(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubTogglePinResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_toggle_pin(self, client: Morta) -> None:
        response = client.user.hubs.with_raw_response.toggle_pin(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubTogglePinResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_toggle_pin(self, client: Morta) -> None:
        with client.user.hubs.with_streaming_response.toggle_pin(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubTogglePinResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_toggle_pin(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.user.hubs.with_raw_response.toggle_pin(
                "",
            )


class TestAsyncHubs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncMorta) -> None:
        hub = await async_client.user.hubs.list()
        assert_matches_type(HubListResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.hubs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubListResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMorta) -> None:
        async with async_client.user.hubs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubListResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_favourites(self, async_client: AsyncMorta) -> None:
        hub = await async_client.user.hubs.list_favourites()
        assert_matches_type(HubListFavouritesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_favourites(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.hubs.with_raw_response.list_favourites()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubListFavouritesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_favourites(self, async_client: AsyncMorta) -> None:
        async with async_client.user.hubs.with_streaming_response.list_favourites() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubListFavouritesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_tags(self, async_client: AsyncMorta) -> None:
        hub = await async_client.user.hubs.list_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubListTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_tags(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.hubs.with_raw_response.list_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubListTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_tags(self, async_client: AsyncMorta) -> None:
        async with async_client.user.hubs.with_streaming_response.list_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubListTagsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_tags(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.user.hubs.with_raw_response.list_tags(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_toggle_favourite(self, async_client: AsyncMorta) -> None:
        hub = await async_client.user.hubs.toggle_favourite(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubToggleFavouriteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_toggle_favourite(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.hubs.with_raw_response.toggle_favourite(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubToggleFavouriteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_toggle_favourite(self, async_client: AsyncMorta) -> None:
        async with async_client.user.hubs.with_streaming_response.toggle_favourite(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubToggleFavouriteResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_toggle_favourite(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.user.hubs.with_raw_response.toggle_favourite(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_toggle_pin(self, async_client: AsyncMorta) -> None:
        hub = await async_client.user.hubs.toggle_pin(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubTogglePinResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_toggle_pin(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.hubs.with_raw_response.toggle_pin(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubTogglePinResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_toggle_pin(self, async_client: AsyncMorta) -> None:
        async with async_client.user.hubs.with_streaming_response.toggle_pin(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubTogglePinResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_toggle_pin(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.user.hubs.with_raw_response.toggle_pin(
                "",
            )
