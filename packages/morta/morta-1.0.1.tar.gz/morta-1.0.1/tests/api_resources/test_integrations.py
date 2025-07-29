# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from morta import Morta, AsyncMorta
from morta.types import (
    IntegrationCreatePassthroughResponse,
)
from tests.utils import assert_matches_type
from morta._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIntegrations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_passthrough(self, client: Morta) -> None:
        integration = client.integrations.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
        )
        assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_passthrough_with_all_params(self, client: Morta) -> None:
        integration = client.integrations.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data={},
            headers={},
            on_behalf_user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_passthrough(self, client: Morta) -> None:
        response = client.integrations.with_raw_response.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_passthrough(self, client: Morta) -> None:
        with client.integrations.with_streaming_response.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_passthrough_download(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        integration = client.integrations.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
        )
        assert integration.is_closed
        assert integration.json() == {"foo": "bar"}
        assert cast(Any, integration.is_closed) is True
        assert isinstance(integration, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_passthrough_download_with_all_params(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        integration = client.integrations.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data={},
            headers={},
            on_behalf_user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert integration.is_closed
        assert integration.json() == {"foo": "bar"}
        assert cast(Any, integration.is_closed) is True
        assert isinstance(integration, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create_passthrough_download(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        integration = client.integrations.with_raw_response.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
        )

        assert integration.is_closed is True
        assert integration.http_request.headers.get("X-Stainless-Lang") == "python"
        assert integration.json() == {"foo": "bar"}
        assert isinstance(integration, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create_passthrough_download(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.integrations.with_streaming_response.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
        ) as integration:
            assert not integration.is_closed
            assert integration.http_request.headers.get("X-Stainless-Lang") == "python"

            assert integration.json() == {"foo": "bar"}
            assert cast(Any, integration.is_closed) is True
            assert isinstance(integration, StreamedBinaryAPIResponse)

        assert cast(Any, integration.is_closed) is True


class TestAsyncIntegrations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_passthrough(self, async_client: AsyncMorta) -> None:
        integration = await async_client.integrations.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
        )
        assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_passthrough_with_all_params(self, async_client: AsyncMorta) -> None:
        integration = await async_client.integrations.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data={},
            headers={},
            on_behalf_user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_passthrough(self, async_client: AsyncMorta) -> None:
        response = await async_client.integrations.with_raw_response.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_passthrough(self, async_client: AsyncMorta) -> None:
        async with async_client.integrations.with_streaming_response.create_passthrough(
            method="GET",
            path="path",
            source_system="viewpoint",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(IntegrationCreatePassthroughResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_passthrough_download(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        integration = await async_client.integrations.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
        )
        assert integration.is_closed
        assert await integration.json() == {"foo": "bar"}
        assert cast(Any, integration.is_closed) is True
        assert isinstance(integration, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_passthrough_download_with_all_params(
        self, async_client: AsyncMorta, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        integration = await async_client.integrations.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            data={},
            headers={},
            on_behalf_user_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert integration.is_closed
        assert await integration.json() == {"foo": "bar"}
        assert cast(Any, integration.is_closed) is True
        assert isinstance(integration, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create_passthrough_download(
        self, async_client: AsyncMorta, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        integration = await async_client.integrations.with_raw_response.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
        )

        assert integration.is_closed is True
        assert integration.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await integration.json() == {"foo": "bar"}
        assert isinstance(integration, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create_passthrough_download(
        self, async_client: AsyncMorta, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/v1/integrations/passthrough-download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.integrations.with_streaming_response.create_passthrough_download(
            method="GET",
            path="path",
            source_system="viewpoint",
        ) as integration:
            assert not integration.is_closed
            assert integration.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await integration.json() == {"foo": "bar"}
            assert cast(Any, integration.is_closed) is True
            assert isinstance(integration, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, integration.is_closed) is True
