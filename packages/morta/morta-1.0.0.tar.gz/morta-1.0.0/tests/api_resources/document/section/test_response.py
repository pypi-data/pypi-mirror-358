# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.document.section import (
    ResponseResetResponse,
    ResponseCreateResponse,
    ResponseDeleteResponse,
    ResponseSubmitResponse,
    ResponseUpdateResponse,
    ResponseRestoreResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestResponse:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        response = client.document.section.response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        response = client.document.section.response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            type="Flexible",
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        http_response = client.document.section.response.with_raw_response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.document.section.response.with_streaming_response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseCreateResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.response.with_raw_response.create(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.response.with_raw_response.create(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        response = client.document.section.response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseUpdateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        response = client.document.section.response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            enable_submission=True,
            pdf_include_response=True,
            reset_after_response=True,
            type="Flexible",
            type_options={},
        )
        assert_matches_type(ResponseUpdateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        http_response = client.document.section.response.with_raw_response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseUpdateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.document.section.response.with_streaming_response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseUpdateResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.response.with_raw_response.update(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.response.with_raw_response.update(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            client.document.section.response.with_raw_response.update(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        response = client.document.section.response.delete(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseDeleteResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        http_response = client.document.section.response.with_raw_response.delete(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseDeleteResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.document.section.response.with_streaming_response.delete(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseDeleteResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.response.with_raw_response.delete(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.response.with_raw_response.delete(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            client.document.section.response.with_raw_response.delete(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_reset(self, client: Morta) -> None:
        response = client.document.section.response.reset(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseResetResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_reset(self, client: Morta) -> None:
        http_response = client.document.section.response.with_raw_response.reset(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseResetResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_reset(self, client: Morta) -> None:
        with client.document.section.response.with_streaming_response.reset(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseResetResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_reset(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.response.with_raw_response.reset(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.response.with_raw_response.reset(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            client.document.section.response.with_raw_response.reset(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_restore(self, client: Morta) -> None:
        response = client.document.section.response.restore(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseRestoreResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_restore(self, client: Morta) -> None:
        http_response = client.document.section.response.with_raw_response.restore(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseRestoreResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_restore(self, client: Morta) -> None:
        with client.document.section.response.with_streaming_response.restore(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseRestoreResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_restore(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.response.with_raw_response.restore(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.response.with_raw_response.restore(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            client.document.section.response.with_raw_response.restore(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: Morta) -> None:
        response = client.document.section.response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseSubmitResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_with_all_params(self, client: Morta) -> None:
        response = client.document.section.response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            response={},
        )
        assert_matches_type(ResponseSubmitResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: Morta) -> None:
        http_response = client.document.section.response.with_raw_response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseSubmitResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: Morta) -> None:
        with client.document.section.response.with_streaming_response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseSubmitResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_submit(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.response.with_raw_response.submit(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.response.with_raw_response.submit(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            client.document.section.response.with_raw_response.submit(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncResponse:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            type="Flexible",
        )
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        http_response = await async_client.document.section.response.with_raw_response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseCreateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.response.with_streaming_response.create(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseCreateResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.response.with_raw_response.create(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.response.with_raw_response.create(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseUpdateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            enable_submission=True,
            pdf_include_response=True,
            reset_after_response=True,
            type="Flexible",
            type_options={},
        )
        assert_matches_type(ResponseUpdateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        http_response = await async_client.document.section.response.with_raw_response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseUpdateResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.response.with_streaming_response.update(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseUpdateResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.response.with_raw_response.update(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.response.with_raw_response.update(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            await async_client.document.section.response.with_raw_response.update(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.delete(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseDeleteResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        http_response = await async_client.document.section.response.with_raw_response.delete(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseDeleteResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.response.with_streaming_response.delete(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseDeleteResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.response.with_raw_response.delete(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.response.with_raw_response.delete(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            await async_client.document.section.response.with_raw_response.delete(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_reset(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.reset(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseResetResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_reset(self, async_client: AsyncMorta) -> None:
        http_response = await async_client.document.section.response.with_raw_response.reset(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseResetResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_reset(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.response.with_streaming_response.reset(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseResetResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_reset(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.response.with_raw_response.reset(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.response.with_raw_response.reset(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            await async_client.document.section.response.with_raw_response.reset(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_restore(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.restore(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseRestoreResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_restore(self, async_client: AsyncMorta) -> None:
        http_response = await async_client.document.section.response.with_raw_response.restore(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseRestoreResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_restore(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.response.with_streaming_response.restore(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseRestoreResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_restore(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.response.with_raw_response.restore(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.response.with_raw_response.restore(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            await async_client.document.section.response.with_raw_response.restore(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ResponseSubmitResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            response={},
        )
        assert_matches_type(ResponseSubmitResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncMorta) -> None:
        http_response = await async_client.document.section.response.with_raw_response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseSubmitResponse, response, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.response.with_streaming_response.submit(
            document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseSubmitResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_submit(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.response.with_raw_response.submit(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.response.with_raw_response.submit(
                document_response_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_response_id` but received ''"):
            await async_client.document.section.response.with_raw_response.submit(
                document_response_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
