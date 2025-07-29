# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from morta.types import (
    PermissionCreateResponse,
    PermissionUpdateResponse,
    PermissionRetrieveResponse,
    PermissionCreateAllResponse,
    PermissionRetrieveTagResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPermissions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        permission = client.permissions.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )
        assert_matches_type(PermissionCreateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        permission = client.permissions.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
            attribute_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            tag_reference_id="tagReferenceId",
        )
        assert_matches_type(PermissionCreateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.permissions.with_raw_response.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionCreateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.permissions.with_streaming_response.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(PermissionCreateResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        permission = client.permissions.retrieve(
            resource="process",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.permissions.with_raw_response.retrieve(
            resource="process",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.permissions.with_streaming_response.retrieve(
            resource="process",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        permission = client.permissions.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
        )
        assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        permission = client.permissions.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.permissions.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.permissions.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.permissions.with_raw_response.update(
                id="",
                role=0,
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        permission = client.permissions.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.permissions.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.permissions.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert permission is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.permissions.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_create_all(self, client: Morta) -> None:
        permission = client.permissions.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )
        assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_all_with_all_params(self, client: Morta) -> None:
        permission = client.permissions.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
            attribute_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            tag_reference_id="tagReferenceId",
        )
        assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_all(self, client: Morta) -> None:
        response = client.permissions.with_raw_response.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_all(self, client: Morta) -> None:
        with client.permissions.with_streaming_response.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_request(self, client: Morta) -> None:
        permission = client.permissions.request(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="project",
        )
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_request(self, client: Morta) -> None:
        response = client.permissions.with_raw_response.request(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="project",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_request(self, client: Morta) -> None:
        with client.permissions.with_streaming_response.request(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="project",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert permission is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_request(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.permissions.with_raw_response.request(
                id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
                type="project",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.permissions.with_raw_response.request(
                id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                type="project",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_tag(self, client: Morta) -> None:
        permission = client.permissions.retrieve_tag(
            tag_id="tag_id",
        )
        assert_matches_type(PermissionRetrieveTagResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_tag(self, client: Morta) -> None:
        response = client.permissions.with_raw_response.retrieve_tag(
            tag_id="tag_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionRetrieveTagResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_tag(self, client: Morta) -> None:
        with client.permissions.with_streaming_response.retrieve_tag(
            tag_id="tag_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(PermissionRetrieveTagResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPermissions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )
        assert_matches_type(PermissionCreateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
            attribute_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            tag_reference_id="tagReferenceId",
        )
        assert_matches_type(PermissionCreateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.permissions.with_raw_response.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(PermissionCreateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.permissions.with_streaming_response.create(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(PermissionCreateResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.retrieve(
            resource="process",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.permissions.with_raw_response.retrieve(
            resource="process",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.permissions.with_streaming_response.retrieve(
            resource="process",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
        )
        assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.permissions.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.permissions.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(PermissionUpdateResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.permissions.with_raw_response.update(
                id="",
                role=0,
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.permissions.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.permissions.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert permission is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.permissions.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_all(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )
        assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_all_with_all_params(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
            attribute_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            tag_reference_id="tagReferenceId",
        )
        assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_all(self, async_client: AsyncMorta) -> None:
        response = await async_client.permissions.with_raw_response.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_all(self, async_client: AsyncMorta) -> None:
        async with async_client.permissions.with_streaming_response.create_all(
            attribute_kind="user",
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            resource_kind="process",
            role=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(PermissionCreateAllResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_request(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.request(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="project",
        )
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_request(self, async_client: AsyncMorta) -> None:
        response = await async_client.permissions.with_raw_response.request(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="project",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert permission is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_request(self, async_client: AsyncMorta) -> None:
        async with async_client.permissions.with_streaming_response.request(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="project",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert permission is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_request(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.permissions.with_raw_response.request(
                id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
                type="project",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.permissions.with_raw_response.request(
                id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                type="project",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_tag(self, async_client: AsyncMorta) -> None:
        permission = await async_client.permissions.retrieve_tag(
            tag_id="tag_id",
        )
        assert_matches_type(PermissionRetrieveTagResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_tag(self, async_client: AsyncMorta) -> None:
        response = await async_client.permissions.with_raw_response.retrieve_tag(
            tag_id="tag_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(PermissionRetrieveTagResponse, permission, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_tag(self, async_client: AsyncMorta) -> None:
        async with async_client.permissions.with_streaming_response.retrieve_tag(
            tag_id="tag_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(PermissionRetrieveTagResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True
