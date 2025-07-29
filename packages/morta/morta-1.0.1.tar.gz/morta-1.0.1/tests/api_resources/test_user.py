# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from morta.types import (
    UserCreateResponse,
    UserSearchResponse,
    UserRetrieveResponse,
    UserRetrieveMeResponse,
    UserListOwnerHubsResponse,
    UserListTemplatesResponse,
    UserUpdateAccountResponse,
    UserUpdateProfileResponse,
    UserListPinnedHubsResponse,
    UserListPublicHubsResponse,
    UserListAchievementsResponse,
    UserListContributionsResponse,
    UserRetrieveByPublicIDResponse,
    UserListPublicContributionsResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUser:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        user = client.user.create(
            email="dev@stainless.com",
            name="name",
            password="password",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        user = client.user.create(
            email="dev@stainless.com",
            name="name",
            password="password",
            opt_out_ai_email=True,
            opt_out_duplication_email=True,
            opt_out_hub_email=True,
            opt_out_sync_email=True,
            opt_out_welcome_email=True,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.user.with_raw_response.create(
            email="dev@stainless.com",
            name="name",
            password="password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.user.with_streaming_response.create(
            email="dev@stainless.com",
            name="name",
            password="password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserCreateResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        user = client.user.retrieve(
            "firebase_id",
        )
        assert_matches_type(UserRetrieveResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.user.with_raw_response.retrieve(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserRetrieveResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.user.with_streaming_response.retrieve(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserRetrieveResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            client.user.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_achievements(self, client: Morta) -> None:
        user = client.user.list_achievements(
            "firebase_id",
        )
        assert_matches_type(UserListAchievementsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_achievements(self, client: Morta) -> None:
        response = client.user.with_raw_response.list_achievements(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListAchievementsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_achievements(self, client: Morta) -> None:
        with client.user.with_streaming_response.list_achievements(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListAchievementsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_achievements(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            client.user.with_raw_response.list_achievements(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_contributions(self, client: Morta) -> None:
        user = client.user.list_contributions(
            "firebase_id",
        )
        assert_matches_type(UserListContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_contributions(self, client: Morta) -> None:
        response = client.user.with_raw_response.list_contributions(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_contributions(self, client: Morta) -> None:
        with client.user.with_streaming_response.list_contributions(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListContributionsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_contributions(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            client.user.with_raw_response.list_contributions(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_owner_hubs(self, client: Morta) -> None:
        user = client.user.list_owner_hubs()
        assert_matches_type(UserListOwnerHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_owner_hubs(self, client: Morta) -> None:
        response = client.user.with_raw_response.list_owner_hubs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListOwnerHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_owner_hubs(self, client: Morta) -> None:
        with client.user.with_streaming_response.list_owner_hubs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListOwnerHubsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_pinned_hubs(self, client: Morta) -> None:
        user = client.user.list_pinned_hubs(
            "firebase_id",
        )
        assert_matches_type(UserListPinnedHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_pinned_hubs(self, client: Morta) -> None:
        response = client.user.with_raw_response.list_pinned_hubs(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListPinnedHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_pinned_hubs(self, client: Morta) -> None:
        with client.user.with_streaming_response.list_pinned_hubs(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListPinnedHubsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_pinned_hubs(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            client.user.with_raw_response.list_pinned_hubs(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_public_contributions(self, client: Morta) -> None:
        user = client.user.list_public_contributions(
            "firebase_id",
        )
        assert_matches_type(UserListPublicContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_public_contributions(self, client: Morta) -> None:
        response = client.user.with_raw_response.list_public_contributions(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListPublicContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_public_contributions(self, client: Morta) -> None:
        with client.user.with_streaming_response.list_public_contributions(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListPublicContributionsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_public_contributions(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            client.user.with_raw_response.list_public_contributions(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_public_hubs(self, client: Morta) -> None:
        user = client.user.list_public_hubs()
        assert_matches_type(UserListPublicHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_public_hubs(self, client: Morta) -> None:
        response = client.user.with_raw_response.list_public_hubs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListPublicHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_public_hubs(self, client: Morta) -> None:
        with client.user.with_streaming_response.list_public_hubs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListPublicHubsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_templates(self, client: Morta) -> None:
        user = client.user.list_templates()
        assert_matches_type(UserListTemplatesResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_templates(self, client: Morta) -> None:
        response = client.user.with_raw_response.list_templates()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListTemplatesResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_templates(self, client: Morta) -> None:
        with client.user.with_streaming_response.list_templates() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListTemplatesResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_by_public_id(self, client: Morta) -> None:
        user = client.user.retrieve_by_public_id(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(UserRetrieveByPublicIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_by_public_id(self, client: Morta) -> None:
        response = client.user.with_raw_response.retrieve_by_public_id(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserRetrieveByPublicIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_by_public_id(self, client: Morta) -> None:
        with client.user.with_streaming_response.retrieve_by_public_id(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserRetrieveByPublicIDResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_by_public_id(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `public_id` but received ''"):
            client.user.with_raw_response.retrieve_by_public_id(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_me(self, client: Morta) -> None:
        user = client.user.retrieve_me()
        assert_matches_type(UserRetrieveMeResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_me(self, client: Morta) -> None:
        response = client.user.with_raw_response.retrieve_me()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserRetrieveMeResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_me(self, client: Morta) -> None:
        with client.user.with_streaming_response.retrieve_me() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserRetrieveMeResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: Morta) -> None:
        user = client.user.search(
            query="query",
        )
        assert_matches_type(UserSearchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_with_all_params(self, client: Morta) -> None:
        user = client.user.search(
            query="query",
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(UserSearchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: Morta) -> None:
        response = client.user.with_raw_response.search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserSearchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: Morta) -> None:
        with client.user.with_streaming_response.search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserSearchResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update_account(self, client: Morta) -> None:
        user = client.user.update_account()
        assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_account_with_all_params(self, client: Morta) -> None:
        user = client.user.update_account(
            allow_support_access=True,
            old_password="oldPassword",
            opt_out_ai_email=True,
            opt_out_duplication_email=True,
            opt_out_hub_email=True,
            opt_out_sync_email=True,
            opt_out_welcome_email=True,
            password="password",
            password_confirm="passwordConfirm",
            two_factor_code="twoFactorCode",
        )
        assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_account(self, client: Morta) -> None:
        response = client.user.with_raw_response.update_account()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_account(self, client: Morta) -> None:
        with client.user.with_streaming_response.update_account() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update_profile(self, client: Morta) -> None:
        user = client.user.update_profile()
        assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_profile_with_all_params(self, client: Morta) -> None:
        user = client.user.update_profile(
            allow_support_access=True,
            bio="bio",
            linkedin="linkedin",
            location="location",
            name="name",
            organisation="organisation",
            profile_picture="profilePicture",
            twitter="twitter",
            university="university",
            university_degree="universityDegree",
            website="website",
        )
        assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_profile(self, client: Morta) -> None:
        response = client.user.with_raw_response.update_profile()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_profile(self, client: Morta) -> None:
        with client.user.with_streaming_response.update_profile() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUser:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.create(
            email="dev@stainless.com",
            name="name",
            password="password",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.create(
            email="dev@stainless.com",
            name="name",
            password="password",
            opt_out_ai_email=True,
            opt_out_duplication_email=True,
            opt_out_hub_email=True,
            opt_out_sync_email=True,
            opt_out_welcome_email=True,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.create(
            email="dev@stainless.com",
            name="name",
            password="password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.create(
            email="dev@stainless.com",
            name="name",
            password="password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserCreateResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.retrieve(
            "firebase_id",
        )
        assert_matches_type(UserRetrieveResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.retrieve(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserRetrieveResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.retrieve(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserRetrieveResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            await async_client.user.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_achievements(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.list_achievements(
            "firebase_id",
        )
        assert_matches_type(UserListAchievementsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_achievements(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.list_achievements(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListAchievementsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_achievements(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.list_achievements(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListAchievementsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_achievements(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            await async_client.user.with_raw_response.list_achievements(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_contributions(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.list_contributions(
            "firebase_id",
        )
        assert_matches_type(UserListContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_contributions(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.list_contributions(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_contributions(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.list_contributions(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListContributionsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_contributions(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            await async_client.user.with_raw_response.list_contributions(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_owner_hubs(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.list_owner_hubs()
        assert_matches_type(UserListOwnerHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_owner_hubs(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.list_owner_hubs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListOwnerHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_owner_hubs(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.list_owner_hubs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListOwnerHubsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_pinned_hubs(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.list_pinned_hubs(
            "firebase_id",
        )
        assert_matches_type(UserListPinnedHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_pinned_hubs(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.list_pinned_hubs(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListPinnedHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_pinned_hubs(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.list_pinned_hubs(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListPinnedHubsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_pinned_hubs(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            await async_client.user.with_raw_response.list_pinned_hubs(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_public_contributions(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.list_public_contributions(
            "firebase_id",
        )
        assert_matches_type(UserListPublicContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_public_contributions(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.list_public_contributions(
            "firebase_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListPublicContributionsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_public_contributions(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.list_public_contributions(
            "firebase_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListPublicContributionsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_public_contributions(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            await async_client.user.with_raw_response.list_public_contributions(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_public_hubs(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.list_public_hubs()
        assert_matches_type(UserListPublicHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_public_hubs(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.list_public_hubs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListPublicHubsResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_public_hubs(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.list_public_hubs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListPublicHubsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_templates(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.list_templates()
        assert_matches_type(UserListTemplatesResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_templates(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.list_templates()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListTemplatesResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_templates(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.list_templates() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListTemplatesResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_by_public_id(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.retrieve_by_public_id(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(UserRetrieveByPublicIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_by_public_id(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.retrieve_by_public_id(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserRetrieveByPublicIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_by_public_id(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.retrieve_by_public_id(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserRetrieveByPublicIDResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_by_public_id(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `public_id` but received ''"):
            await async_client.user.with_raw_response.retrieve_by_public_id(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_me(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.retrieve_me()
        assert_matches_type(UserRetrieveMeResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_me(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.retrieve_me()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserRetrieveMeResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_me(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.retrieve_me() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserRetrieveMeResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.search(
            query="query",
        )
        assert_matches_type(UserSearchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.search(
            query="query",
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_view_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(UserSearchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserSearchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserSearchResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_account(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.update_account()
        assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_account_with_all_params(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.update_account(
            allow_support_access=True,
            old_password="oldPassword",
            opt_out_ai_email=True,
            opt_out_duplication_email=True,
            opt_out_hub_email=True,
            opt_out_sync_email=True,
            opt_out_welcome_email=True,
            password="password",
            password_confirm="passwordConfirm",
            two_factor_code="twoFactorCode",
        )
        assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_account(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.update_account()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_account(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.update_account() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserUpdateAccountResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_profile(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.update_profile()
        assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_profile_with_all_params(self, async_client: AsyncMorta) -> None:
        user = await async_client.user.update_profile(
            allow_support_access=True,
            bio="bio",
            linkedin="linkedin",
            location="location",
            name="name",
            organisation="organisation",
            profile_picture="profilePicture",
            twitter="twitter",
            university="university",
            university_degree="universityDegree",
            website="website",
        )
        assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_profile(self, async_client: AsyncMorta) -> None:
        response = await async_client.user.with_raw_response.update_profile()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_profile(self, async_client: AsyncMorta) -> None:
        async with async_client.user.with_streaming_response.update_profile() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserUpdateProfileResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True
