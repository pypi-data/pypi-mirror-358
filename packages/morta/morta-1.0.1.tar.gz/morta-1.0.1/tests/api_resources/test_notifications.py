# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from morta.types import (
    NotificationCreateResponse,
    NotificationDeleteResponse,
    NotificationUpdateResponse,
    NotificationListEventsResponse,
    NotificationListEventTypesResponse,
)
from tests.utils import assert_matches_type
from morta._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNotifications:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        notification = client.notifications.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
        )
        assert_matches_type(NotificationCreateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        notification = client.notifications.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
            custom_headers=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            processes=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            tables=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(NotificationCreateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.notifications.with_raw_response.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = response.parse()
        assert_matches_type(NotificationCreateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.notifications.with_streaming_response.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = response.parse()
            assert_matches_type(NotificationCreateResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        notification = client.notifications.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
        )
        assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        notification = client.notifications.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
            custom_headers=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            description="description",
            processes=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            tables=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
        )
        assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.notifications.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = response.parse()
        assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.notifications.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = response.parse()
            assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.notifications.with_raw_response.update(
                id="",
                webhook_url="webhookUrl",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        notification = client.notifications.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(NotificationDeleteResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.notifications.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = response.parse()
        assert_matches_type(NotificationDeleteResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.notifications.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = response.parse()
            assert_matches_type(NotificationDeleteResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.notifications.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_event_types(self, client: Morta) -> None:
        notification = client.notifications.list_event_types()
        assert_matches_type(NotificationListEventTypesResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_event_types(self, client: Morta) -> None:
        response = client.notifications.with_raw_response.list_event_types()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = response.parse()
        assert_matches_type(NotificationListEventTypesResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_event_types(self, client: Morta) -> None:
        with client.notifications.with_streaming_response.list_event_types() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = response.parse()
            assert_matches_type(NotificationListEventTypesResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_events(self, client: Morta) -> None:
        notification = client.notifications.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
        )
        assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_events_with_all_params(self, client: Morta) -> None:
        notification = client.notifications.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            page=1,
            search="search",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            users=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            verb=["string"],
        )
        assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_events(self, client: Morta) -> None:
        response = client.notifications.with_raw_response.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = response.parse()
        assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_events(self, client: Morta) -> None:
        with client.notifications.with_streaming_response.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = response.parse()
            assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_events(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            client.notifications.with_raw_response.list_events(
                resource_id="",
                type="process",
            )


class TestAsyncNotifications:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
        )
        assert_matches_type(NotificationCreateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
            custom_headers=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            processes=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            tables=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(NotificationCreateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.notifications.with_raw_response.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = await response.parse()
        assert_matches_type(NotificationCreateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.notifications.with_streaming_response.create(
            description="description",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                }
            ],
            webhook_url="webhookUrl",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = await response.parse()
            assert_matches_type(NotificationCreateResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
        )
        assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
            custom_headers=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            description="description",
            processes=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            tables=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            triggers=[
                {
                    "resource": "resource",
                    "verb": "verb",
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
        )
        assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.notifications.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = await response.parse()
        assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.notifications.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            webhook_url="webhookUrl",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = await response.parse()
            assert_matches_type(NotificationUpdateResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.notifications.with_raw_response.update(
                id="",
                webhook_url="webhookUrl",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(NotificationDeleteResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.notifications.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = await response.parse()
        assert_matches_type(NotificationDeleteResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.notifications.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = await response.parse()
            assert_matches_type(NotificationDeleteResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.notifications.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_event_types(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.list_event_types()
        assert_matches_type(NotificationListEventTypesResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_event_types(self, async_client: AsyncMorta) -> None:
        response = await async_client.notifications.with_raw_response.list_event_types()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = await response.parse()
        assert_matches_type(NotificationListEventTypesResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_event_types(self, async_client: AsyncMorta) -> None:
        async with async_client.notifications.with_streaming_response.list_event_types() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = await response.parse()
            assert_matches_type(NotificationListEventTypesResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_events(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
        )
        assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_events_with_all_params(self, async_client: AsyncMorta) -> None:
        notification = await async_client.notifications.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            page=1,
            search="search",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            users=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            verb=["string"],
        )
        assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncMorta) -> None:
        response = await async_client.notifications.with_raw_response.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notification = await response.parse()
        assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncMorta) -> None:
        async with async_client.notifications.with_streaming_response.list_events(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="process",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notification = await response.parse()
            assert_matches_type(NotificationListEventsResponse, notification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_events(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            await async_client.notifications.with_raw_response.list_events(
                resource_id="",
                type="process",
            )
