# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.table import (
    SyncUpdateResponse,
    SyncGetSyncInfoResponse,
    SyncDeleteIntegrationResponse,
    SyncSyncWithIntegrationResponse,
    SyncRetryIntegrationSyncResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSync:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        sync = client.table.sync.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncUpdateResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        sync = client.table.sync.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            company_id="companyId",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            doc_types=["string"],
            enterprise_id="enterpriseId",
            folder_id="folderId",
            hub_id="hubId",
            license_id="licenseId",
            model_id="modelId",
            project_id="projectId",
            project_ids=["string"],
            properties=["string"],
            region="region",
            top_folder_id="topFolderId",
            type="Projects",
        )
        assert_matches_type(SyncUpdateResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.table.sync.with_raw_response.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = response.parse()
        assert_matches_type(SyncUpdateResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.table.sync.with_streaming_response.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = response.parse()
            assert_matches_type(SyncUpdateResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.sync.with_raw_response.update(
                integration_name="integration_name",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_name` but received ''"):
            client.table.sync.with_raw_response.update(
                integration_name="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_integration(self, client: Morta) -> None:
        sync = client.table.sync.delete_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncDeleteIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete_integration(self, client: Morta) -> None:
        response = client.table.sync.with_raw_response.delete_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = response.parse()
        assert_matches_type(SyncDeleteIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete_integration(self, client: Morta) -> None:
        with client.table.sync.with_streaming_response.delete_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = response.parse()
            assert_matches_type(SyncDeleteIntegrationResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete_integration(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.sync.with_raw_response.delete_integration(
                integration_name="integration_name",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_name` but received ''"):
            client.table.sync.with_raw_response.delete_integration(
                integration_name="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_sync_info(self, client: Morta) -> None:
        sync = client.table.sync.get_sync_info(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncGetSyncInfoResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_sync_info(self, client: Morta) -> None:
        response = client.table.sync.with_raw_response.get_sync_info(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = response.parse()
        assert_matches_type(SyncGetSyncInfoResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_sync_info(self, client: Morta) -> None:
        with client.table.sync.with_streaming_response.get_sync_info(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = response.parse()
            assert_matches_type(SyncGetSyncInfoResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_sync_info(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.sync.with_raw_response.get_sync_info(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retry_integration_sync(self, client: Morta) -> None:
        sync = client.table.sync.retry_integration_sync(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncRetryIntegrationSyncResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retry_integration_sync(self, client: Morta) -> None:
        response = client.table.sync.with_raw_response.retry_integration_sync(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = response.parse()
        assert_matches_type(SyncRetryIntegrationSyncResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retry_integration_sync(self, client: Morta) -> None:
        with client.table.sync.with_streaming_response.retry_integration_sync(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = response.parse()
            assert_matches_type(SyncRetryIntegrationSyncResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retry_integration_sync(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.sync.with_raw_response.retry_integration_sync(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_sync_with_integration(self, client: Morta) -> None:
        sync = client.table.sync.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_sync_with_integration_with_all_params(self, client: Morta) -> None:
        sync = client.table.sync.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            company_id="companyId",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            doc_types=["string"],
            enterprise_id="enterpriseId",
            folder_id="folderId",
            hub_id="hubId",
            license_id="licenseId",
            model_id="modelId",
            project_id="projectId",
            project_ids=["string"],
            properties=["string"],
            region="region",
            top_folder_id="topFolderId",
            type="Projects",
        )
        assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_sync_with_integration(self, client: Morta) -> None:
        response = client.table.sync.with_raw_response.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = response.parse()
        assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_sync_with_integration(self, client: Morta) -> None:
        with client.table.sync.with_streaming_response.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = response.parse()
            assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_sync_with_integration(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            client.table.sync.with_raw_response.sync_with_integration(
                integration_name="integration_name",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_name` but received ''"):
            client.table.sync.with_raw_response.sync_with_integration(
                integration_name="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncSync:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        sync = await async_client.table.sync.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncUpdateResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        sync = await async_client.table.sync.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            company_id="companyId",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            doc_types=["string"],
            enterprise_id="enterpriseId",
            folder_id="folderId",
            hub_id="hubId",
            license_id="licenseId",
            model_id="modelId",
            project_id="projectId",
            project_ids=["string"],
            properties=["string"],
            region="region",
            top_folder_id="topFolderId",
            type="Projects",
        )
        assert_matches_type(SyncUpdateResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.sync.with_raw_response.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = await response.parse()
        assert_matches_type(SyncUpdateResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.table.sync.with_streaming_response.update(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = await response.parse()
            assert_matches_type(SyncUpdateResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.sync.with_raw_response.update(
                integration_name="integration_name",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_name` but received ''"):
            await async_client.table.sync.with_raw_response.update(
                integration_name="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_integration(self, async_client: AsyncMorta) -> None:
        sync = await async_client.table.sync.delete_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncDeleteIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete_integration(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.sync.with_raw_response.delete_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = await response.parse()
        assert_matches_type(SyncDeleteIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete_integration(self, async_client: AsyncMorta) -> None:
        async with async_client.table.sync.with_streaming_response.delete_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = await response.parse()
            assert_matches_type(SyncDeleteIntegrationResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete_integration(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.sync.with_raw_response.delete_integration(
                integration_name="integration_name",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_name` but received ''"):
            await async_client.table.sync.with_raw_response.delete_integration(
                integration_name="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_sync_info(self, async_client: AsyncMorta) -> None:
        sync = await async_client.table.sync.get_sync_info(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncGetSyncInfoResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_sync_info(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.sync.with_raw_response.get_sync_info(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = await response.parse()
        assert_matches_type(SyncGetSyncInfoResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_sync_info(self, async_client: AsyncMorta) -> None:
        async with async_client.table.sync.with_streaming_response.get_sync_info(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = await response.parse()
            assert_matches_type(SyncGetSyncInfoResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_sync_info(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.sync.with_raw_response.get_sync_info(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retry_integration_sync(self, async_client: AsyncMorta) -> None:
        sync = await async_client.table.sync.retry_integration_sync(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncRetryIntegrationSyncResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retry_integration_sync(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.sync.with_raw_response.retry_integration_sync(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = await response.parse()
        assert_matches_type(SyncRetryIntegrationSyncResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retry_integration_sync(self, async_client: AsyncMorta) -> None:
        async with async_client.table.sync.with_streaming_response.retry_integration_sync(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = await response.parse()
            assert_matches_type(SyncRetryIntegrationSyncResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retry_integration_sync(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.sync.with_raw_response.retry_integration_sync(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_sync_with_integration(self, async_client: AsyncMorta) -> None:
        sync = await async_client.table.sync.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_sync_with_integration_with_all_params(self, async_client: AsyncMorta) -> None:
        sync = await async_client.table.sync.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            company_id="companyId",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            doc_types=["string"],
            enterprise_id="enterpriseId",
            folder_id="folderId",
            hub_id="hubId",
            license_id="licenseId",
            model_id="modelId",
            project_id="projectId",
            project_ids=["string"],
            properties=["string"],
            region="region",
            top_folder_id="topFolderId",
            type="Projects",
        )
        assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_sync_with_integration(self, async_client: AsyncMorta) -> None:
        response = await async_client.table.sync.with_raw_response.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sync = await response.parse()
        assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_sync_with_integration(self, async_client: AsyncMorta) -> None:
        async with async_client.table.sync.with_streaming_response.sync_with_integration(
            integration_name="integration_name",
            table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sync = await response.parse()
            assert_matches_type(SyncSyncWithIntegrationResponse, sync, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_sync_with_integration(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_id` but received ''"):
            await async_client.table.sync.with_raw_response.sync_with_integration(
                integration_name="integration_name",
                table_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_name` but received ''"):
            await async_client.table.sync.with_raw_response.sync_with_integration(
                integration_name="",
                table_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
