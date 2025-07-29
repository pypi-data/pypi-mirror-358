# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.hub import (
    InviteCreateResponse,
    InviteDeleteResponse,
    InviteResendResponse,
    InviteUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInvite:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        invite = client.hub.invite.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
        )
        assert_matches_type(InviteCreateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        invite = client.hub.invite.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
            project_role="member",
            tags=["string"],
        )
        assert_matches_type(InviteCreateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.hub.invite.with_raw_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = response.parse()
        assert_matches_type(InviteCreateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.hub.invite.with_streaming_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = response.parse()
            assert_matches_type(InviteCreateResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.invite.with_raw_response.create(
                hub_id="",
                email="dev@stainless.com",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        invite = client.hub.invite.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(InviteUpdateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        invite = client.hub.invite.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_role="member",
            tags=["string"],
        )
        assert_matches_type(InviteUpdateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.hub.invite.with_raw_response.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = response.parse()
        assert_matches_type(InviteUpdateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.hub.invite.with_streaming_response.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = response.parse()
            assert_matches_type(InviteUpdateResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.invite.with_raw_response.update(
                invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invite_id` but received ''"):
            client.hub.invite.with_raw_response.update(
                invite_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        invite = client.hub.invite.delete(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(InviteDeleteResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.hub.invite.with_raw_response.delete(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = response.parse()
        assert_matches_type(InviteDeleteResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.hub.invite.with_streaming_response.delete(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = response.parse()
            assert_matches_type(InviteDeleteResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.invite.with_raw_response.delete(
                invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invite_id` but received ''"):
            client.hub.invite.with_raw_response.delete(
                invite_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_resend(self, client: Morta) -> None:
        invite = client.hub.invite.resend(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(InviteResendResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_resend(self, client: Morta) -> None:
        response = client.hub.invite.with_raw_response.resend(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = response.parse()
        assert_matches_type(InviteResendResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_resend(self, client: Morta) -> None:
        with client.hub.invite.with_streaming_response.resend(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = response.parse()
            assert_matches_type(InviteResendResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_resend(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.invite.with_raw_response.resend(
                invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invite_id` but received ''"):
            client.hub.invite.with_raw_response.resend(
                invite_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncInvite:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        invite = await async_client.hub.invite.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
        )
        assert_matches_type(InviteCreateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        invite = await async_client.hub.invite.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
            project_role="member",
            tags=["string"],
        )
        assert_matches_type(InviteCreateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.invite.with_raw_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = await response.parse()
        assert_matches_type(InviteCreateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.invite.with_streaming_response.create(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            email="dev@stainless.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = await response.parse()
            assert_matches_type(InviteCreateResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.invite.with_raw_response.create(
                hub_id="",
                email="dev@stainless.com",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        invite = await async_client.hub.invite.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(InviteUpdateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        invite = await async_client.hub.invite.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_role="member",
            tags=["string"],
        )
        assert_matches_type(InviteUpdateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.invite.with_raw_response.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = await response.parse()
        assert_matches_type(InviteUpdateResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.invite.with_streaming_response.update(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = await response.parse()
            assert_matches_type(InviteUpdateResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.invite.with_raw_response.update(
                invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invite_id` but received ''"):
            await async_client.hub.invite.with_raw_response.update(
                invite_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        invite = await async_client.hub.invite.delete(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(InviteDeleteResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.invite.with_raw_response.delete(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = await response.parse()
        assert_matches_type(InviteDeleteResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.invite.with_streaming_response.delete(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = await response.parse()
            assert_matches_type(InviteDeleteResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.invite.with_raw_response.delete(
                invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invite_id` but received ''"):
            await async_client.hub.invite.with_raw_response.delete(
                invite_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_resend(self, async_client: AsyncMorta) -> None:
        invite = await async_client.hub.invite.resend(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(InviteResendResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_resend(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.invite.with_raw_response.resend(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invite = await response.parse()
        assert_matches_type(InviteResendResponse, invite, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_resend(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.invite.with_streaming_response.resend(
            invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invite = await response.parse()
            assert_matches_type(InviteResendResponse, invite, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_resend(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.invite.with_raw_response.resend(
                invite_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invite_id` but received ''"):
            await async_client.hub.invite.with_raw_response.resend(
                invite_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
