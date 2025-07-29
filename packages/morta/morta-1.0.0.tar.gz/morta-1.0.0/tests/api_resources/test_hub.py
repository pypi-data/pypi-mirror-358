# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from morta.types import (
    HubCreateResponse,
    HubDeleteResponse,
    HubUpdateResponse,
    HubGetTagsResponse,
    HubRestoreResponse,
    HubAISearchResponse,
    HubRetrieveResponse,
    HubGetTablesResponse,
    HubGetMembersResponse,
    HubRemoveUserResponse,
    HubGetAIAnswersResponse,
    HubGetDocumentsResponse,
    HubGetResourcesResponse,
    HubGetVariablesResponse,
    HubChangeUserRoleResponse,
    HubUploadTemplateResponse,
    HubSearchResourcesResponse,
    HubGetDeletedTablesResponse,
    HubGetNotificationsResponse,
    HubGetInvitedMembersResponse,
    HubPermanentlyDeleteResponse,
    HubGetDeletedDocumentsResponse,
    HubInviteMultipleUsersResponse,
    HubCreateHeadingStylingResponse,
    HubGetSentNotificationsResponse,
    HubUpdateHeadingStylingResponse,
    HubGetDuplicatedChildrenResponse,
    HubDeleteTopHeadingStylingResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHub:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        hub = client.hub.create(
            name="name",
        )
        assert_matches_type(HubCreateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.hub.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubCreateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.hub.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubCreateResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        hub = client.hub.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubRetrieveResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.hub.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubRetrieveResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.hub.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubRetrieveResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        hub = client.hub.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubUpdateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        hub = client.hub.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            ai_search_enabled=True,
            allow_document_export=True,
            allow_table_export=True,
            bulk_update_text={
                "replace_text": "replaceText",
                "search_text": "searchText",
            },
            default_banner="defaultBanner",
            default_date_format="defaultDateFormat",
            default_datetime_format="defaultDatetimeFormat",
            default_header_background_color="defaultHeaderBackgroundColor",
            default_header_text_color="defaultHeaderTextColor",
            default_process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domains_access=["string"],
            font_colour="fontColour",
            hide_process_created=True,
            logo="logo",
            mfa_required=True,
            name="name",
            primary_colour="primaryColour",
            process_title_alignment="left",
            process_title_bold=True,
            process_title_colour="processTitleColour",
            process_title_font_size=0,
            process_title_italic=True,
            process_title_underline=True,
            public=True,
            word_template="wordTemplate",
        )
        assert_matches_type(HubUpdateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.hub.with_raw_response.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubUpdateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.hub.with_streaming_response.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubUpdateResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.update(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        hub = client.hub.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.hub.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.hub.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubDeleteResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_ai_search(self, client: Morta) -> None:
        hub = client.hub.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )
        assert_matches_type(HubAISearchResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_ai_search_with_all_params(self, client: Morta) -> None:
        hub = client.hub.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
            process_public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubAISearchResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_ai_search(self, client: Morta) -> None:
        response = client.hub.with_raw_response.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubAISearchResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_ai_search(self, client: Morta) -> None:
        with client.hub.with_streaming_response.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubAISearchResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_ai_search(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.ai_search(
                hub_id="",
                search="search",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_change_user_role(self, client: Morta) -> None:
        hub = client.hub.change_user_role(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role="owner",
        )
        assert_matches_type(HubChangeUserRoleResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_change_user_role(self, client: Morta) -> None:
        response = client.hub.with_raw_response.change_user_role(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role="owner",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubChangeUserRoleResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_change_user_role(self, client: Morta) -> None:
        with client.hub.with_streaming_response.change_user_role(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role="owner",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubChangeUserRoleResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_change_user_role(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.change_user_role(
                firebase_id="firebase_id",
                hub_id="",
                role="owner",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            client.hub.with_raw_response.change_user_role(
                firebase_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                role="owner",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_create_heading_styling(self, client: Morta) -> None:
        hub = client.hub.create_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubCreateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_heading_styling(self, client: Morta) -> None:
        response = client.hub.with_raw_response.create_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubCreateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_heading_styling(self, client: Morta) -> None:
        with client.hub.with_streaming_response.create_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubCreateHeadingStylingResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create_heading_styling(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.create_heading_styling(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_create_knowledge_base(self, client: Morta) -> None:
        hub = client.hub.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_knowledge_base_with_all_params(self, client: Morta) -> None:
        hub = client.hub.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            link="link",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_knowledge_base(self, client: Morta) -> None:
        response = client.hub.with_raw_response.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_knowledge_base(self, client: Morta) -> None:
        with client.hub.with_streaming_response.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create_knowledge_base(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.create_knowledge_base(
                hub_id="",
                source="source",
                text="text",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_top_heading_styling(self, client: Morta) -> None:
        hub = client.hub.delete_top_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubDeleteTopHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete_top_heading_styling(self, client: Morta) -> None:
        response = client.hub.with_raw_response.delete_top_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubDeleteTopHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete_top_heading_styling(self, client: Morta) -> None:
        with client.hub.with_streaming_response.delete_top_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubDeleteTopHeadingStylingResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete_top_heading_styling(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.delete_top_heading_styling(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate(self, client: Morta) -> None:
        hub = client.hub.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate_with_all_params(self, client: Morta) -> None:
        hub = client.hub.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            duplicate_permissions=True,
            lock_resource=True,
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_duplicate(self, client: Morta) -> None:
        response = client.hub.with_raw_response.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_duplicate(self, client: Morta) -> None:
        with client.hub.with_streaming_response.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_duplicate(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.duplicate(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_ai_answers(self, client: Morta) -> None:
        hub = client.hub.get_ai_answers(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetAIAnswersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_ai_answers(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_ai_answers(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetAIAnswersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_ai_answers(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_ai_answers(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetAIAnswersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_ai_answers(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_ai_answers(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_deleted_documents(self, client: Morta) -> None:
        hub = client.hub.get_deleted_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDeletedDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_deleted_documents(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_deleted_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetDeletedDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_deleted_documents(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_deleted_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetDeletedDocumentsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_deleted_documents(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_deleted_documents(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_deleted_tables(self, client: Morta) -> None:
        hub = client.hub.get_deleted_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDeletedTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_deleted_tables(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_deleted_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetDeletedTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_deleted_tables(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_deleted_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetDeletedTablesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_deleted_tables(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_deleted_tables(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_documents(self, client: Morta) -> None:
        hub = client.hub.get_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_documents(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_documents(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetDocumentsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_documents(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_documents(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_duplicated_children(self, client: Morta) -> None:
        hub = client.hub.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDuplicatedChildrenResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_duplicated_children(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetDuplicatedChildrenResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_duplicated_children(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetDuplicatedChildrenResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_duplicated_children(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_duplicated_children(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_invited_members(self, client: Morta) -> None:
        hub = client.hub.get_invited_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetInvitedMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_invited_members(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_invited_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetInvitedMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_invited_members(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_invited_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetInvitedMembersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_invited_members(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_invited_members(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_members(self, client: Morta) -> None:
        hub = client.hub.get_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_members(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_members(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetMembersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_members(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_members(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_notifications(self, client: Morta) -> None:
        hub = client.hub.get_notifications(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_notifications(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_notifications(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_notifications(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_notifications(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetNotificationsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_notifications(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_notifications(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_resources(self, client: Morta) -> None:
        hub = client.hub.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_resources_with_all_params(self, client: Morta) -> None:
        hub = client.hub.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            admin_view=True,
            exclude_processes=True,
            exclude_tables=True,
            only_admin=True,
            only_deleted=True,
            project_permissions=True,
            type_id="typeId",
        )
        assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_resources(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_resources(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_resources(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_resources(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_sent_notifications(self, client: Morta) -> None:
        hub = client.hub.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_sent_notifications_with_all_params(self, client: Morta) -> None:
        hub = client.hub.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            notification_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page=1,
            size=1,
        )
        assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_sent_notifications(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_sent_notifications(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_sent_notifications(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_sent_notifications(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_tables(self, client: Morta) -> None:
        hub = client.hub.get_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_tables(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_tables(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetTablesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_tables(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_tables(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_tags(self, client: Morta) -> None:
        hub = client.hub.get_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_tags(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_tags(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetTagsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_tags(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_tags(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_variables(self, client: Morta) -> None:
        hub = client.hub.get_variables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetVariablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_variables(self, client: Morta) -> None:
        response = client.hub.with_raw_response.get_variables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubGetVariablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_variables(self, client: Morta) -> None:
        with client.hub.with_streaming_response.get_variables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubGetVariablesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_variables(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.get_variables(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_invite_multiple_users(self, client: Morta) -> None:
        hub = client.hub.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_invite_multiple_users_with_all_params(self, client: Morta) -> None:
        hub = client.hub.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            emails=["dev@stainless.com"],
            project_role="member",
            tags=["string"],
        )
        assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_invite_multiple_users(self, client: Morta) -> None:
        response = client.hub.with_raw_response.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_invite_multiple_users(self, client: Morta) -> None:
        with client.hub.with_streaming_response.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_invite_multiple_users(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.invite_multiple_users(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_permanently_delete(self, client: Morta) -> None:
        hub = client.hub.permanently_delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubPermanentlyDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_permanently_delete(self, client: Morta) -> None:
        response = client.hub.with_raw_response.permanently_delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubPermanentlyDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_permanently_delete(self, client: Morta) -> None:
        with client.hub.with_streaming_response.permanently_delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubPermanentlyDeleteResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_permanently_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.permanently_delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_remove_user(self, client: Morta) -> None:
        hub = client.hub.remove_user(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubRemoveUserResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_remove_user(self, client: Morta) -> None:
        response = client.hub.with_raw_response.remove_user(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubRemoveUserResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_remove_user(self, client: Morta) -> None:
        with client.hub.with_streaming_response.remove_user(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubRemoveUserResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_remove_user(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.remove_user(
                firebase_id="firebase_id",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            client.hub.with_raw_response.remove_user(
                firebase_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_request_contributor_access(self, client: Morta) -> None:
        hub = client.hub.request_contributor_access(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_request_contributor_access(self, client: Morta) -> None:
        response = client.hub.with_raw_response.request_contributor_access(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_request_contributor_access(self, client: Morta) -> None:
        with client.hub.with_streaming_response.request_contributor_access(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_request_contributor_access(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.request_contributor_access(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_restore(self, client: Morta) -> None:
        hub = client.hub.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubRestoreResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_restore(self, client: Morta) -> None:
        response = client.hub.with_raw_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubRestoreResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_restore(self, client: Morta) -> None:
        with client.hub.with_streaming_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubRestoreResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_restore(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.restore(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_search_resources(self, client: Morta) -> None:
        hub = client.hub.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )
        assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_resources_with_all_params(self, client: Morta) -> None:
        hub = client.hub.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
            process_public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search_resources(self, client: Morta) -> None:
        response = client.hub.with_raw_response.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search_resources(self, client: Morta) -> None:
        with client.hub.with_streaming_response.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_search_resources(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.search_resources(
                hub_id="",
                search="search",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_set_column_coloring(self, client: Morta) -> None:
        hub = client.hub.set_column_coloring(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_set_column_coloring(self, client: Morta) -> None:
        response = client.hub.with_raw_response.set_column_coloring(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_set_column_coloring(self, client: Morta) -> None:
        with client.hub.with_streaming_response.set_column_coloring(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_set_column_coloring(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.set_column_coloring(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_set_column_format(self, client: Morta) -> None:
        hub = client.hub.set_column_format(
            kind="kind",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_set_column_format(self, client: Morta) -> None:
        response = client.hub.with_raw_response.set_column_format(
            kind="kind",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_set_column_format(self, client: Morta) -> None:
        with client.hub.with_streaming_response.set_column_format(
            kind="kind",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_set_column_format(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.set_column_format(
                kind="kind",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `kind` but received ''"):
            client.hub.with_raw_response.set_column_format(
                kind="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_train_knowledge_base(self, client: Morta) -> None:
        hub = client.hub.train_knowledge_base(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_train_knowledge_base(self, client: Morta) -> None:
        response = client.hub.with_raw_response.train_knowledge_base(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_train_knowledge_base(self, client: Morta) -> None:
        with client.hub.with_streaming_response.train_knowledge_base(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_train_knowledge_base(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.train_knowledge_base(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_heading_styling(self, client: Morta) -> None:
        hub = client.hub.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_heading_styling_with_all_params(self, client: Morta) -> None:
        hub = client.hub.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bold=True,
            colour="colour",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            font_size=0,
            italic=True,
            numbering_style=0,
            start_at0=True,
            underline=True,
        )
        assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_heading_styling(self, client: Morta) -> None:
        response = client.hub.with_raw_response.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_heading_styling(self, client: Morta) -> None:
        with client.hub.with_streaming_response.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_heading_styling(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.update_heading_styling(
                style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `style_id` but received ''"):
            client.hub.with_raw_response.update_heading_styling(
                style_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_upload_template(self, client: Morta) -> None:
        hub = client.hub.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_upload_template_with_all_params(self, client: Morta) -> None:
        hub = client.hub.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            file=b"raw file contents",
        )
        assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upload_template(self, client: Morta) -> None:
        response = client.hub.with_raw_response.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = response.parse()
        assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upload_template(self, client: Morta) -> None:
        with client.hub.with_streaming_response.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = response.parse()
            assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_upload_template(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.with_raw_response.upload_template(
                hub_id="",
            )


class TestAsyncHub:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.create(
            name="name",
        )
        assert_matches_type(HubCreateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubCreateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubCreateResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubRetrieveResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubRetrieveResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubRetrieveResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubUpdateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            ai_search_enabled=True,
            allow_document_export=True,
            allow_table_export=True,
            bulk_update_text={
                "replace_text": "replaceText",
                "search_text": "searchText",
            },
            default_banner="defaultBanner",
            default_date_format="defaultDateFormat",
            default_datetime_format="defaultDatetimeFormat",
            default_header_background_color="defaultHeaderBackgroundColor",
            default_header_text_color="defaultHeaderTextColor",
            default_process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domains_access=["string"],
            font_colour="fontColour",
            hide_process_created=True,
            logo="logo",
            mfa_required=True,
            name="name",
            primary_colour="primaryColour",
            process_title_alignment="left",
            process_title_bold=True,
            process_title_colour="processTitleColour",
            process_title_font_size=0,
            process_title_italic=True,
            process_title_underline=True,
            public=True,
            word_template="wordTemplate",
        )
        assert_matches_type(HubUpdateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubUpdateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.update(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubUpdateResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.update(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubDeleteResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_ai_search(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )
        assert_matches_type(HubAISearchResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_ai_search_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
            process_public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubAISearchResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_ai_search(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubAISearchResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_ai_search(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.ai_search(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubAISearchResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_ai_search(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.ai_search(
                hub_id="",
                search="search",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_change_user_role(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.change_user_role(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role="owner",
        )
        assert_matches_type(HubChangeUserRoleResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_change_user_role(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.change_user_role(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role="owner",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubChangeUserRoleResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_change_user_role(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.change_user_role(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            role="owner",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubChangeUserRoleResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_change_user_role(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.change_user_role(
                firebase_id="firebase_id",
                hub_id="",
                role="owner",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            await async_client.hub.with_raw_response.change_user_role(
                firebase_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                role="owner",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_heading_styling(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.create_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubCreateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_heading_styling(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.create_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubCreateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_heading_styling(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.create_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubCreateHeadingStylingResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create_heading_styling(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.create_heading_styling(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_knowledge_base(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_knowledge_base_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            link="link",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_knowledge_base(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_knowledge_base(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.create_knowledge_base(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source="source",
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create_knowledge_base(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.create_knowledge_base(
                hub_id="",
                source="source",
                text="text",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_top_heading_styling(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.delete_top_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubDeleteTopHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete_top_heading_styling(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.delete_top_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubDeleteTopHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete_top_heading_styling(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.delete_top_heading_styling(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubDeleteTopHeadingStylingResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete_top_heading_styling(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.delete_top_heading_styling(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            duplicate_permissions=True,
            lock_resource=True,
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_duplicate(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_duplicate(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.duplicate(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_duplicate(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.duplicate(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_ai_answers(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_ai_answers(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetAIAnswersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_ai_answers(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_ai_answers(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetAIAnswersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_ai_answers(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_ai_answers(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetAIAnswersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_ai_answers(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_ai_answers(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_deleted_documents(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_deleted_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDeletedDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_deleted_documents(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_deleted_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetDeletedDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_deleted_documents(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_deleted_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetDeletedDocumentsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_deleted_documents(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_deleted_documents(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_deleted_tables(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_deleted_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDeletedTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_deleted_tables(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_deleted_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetDeletedTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_deleted_tables(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_deleted_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetDeletedTablesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_deleted_tables(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_deleted_tables(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_documents(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_documents(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetDocumentsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_documents(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_documents(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetDocumentsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_documents(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_documents(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetDuplicatedChildrenResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetDuplicatedChildrenResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetDuplicatedChildrenResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_duplicated_children(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_invited_members(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_invited_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetInvitedMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_invited_members(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_invited_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetInvitedMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_invited_members(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_invited_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetInvitedMembersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_invited_members(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_invited_members(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_members(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_members(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetMembersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_members(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_members(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetMembersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_members(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_members(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_notifications(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_notifications(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_notifications(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_notifications(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_notifications(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_notifications(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetNotificationsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_notifications(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_notifications(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_resources(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_resources_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            admin_view=True,
            exclude_processes=True,
            exclude_tables=True,
            only_admin=True,
            only_deleted=True,
            project_permissions=True,
            type_id="typeId",
        )
        assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_resources(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_resources(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetResourcesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_resources(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_resources(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_sent_notifications(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_sent_notifications_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            notification_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page=1,
            size=1,
        )
        assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_sent_notifications(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_sent_notifications(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_sent_notifications(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetSentNotificationsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_sent_notifications(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_sent_notifications(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_tables(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_tables(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetTablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_tables(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_tables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetTablesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_tables(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_tables(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_tags(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_tags(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetTagsResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_tags(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_tags(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetTagsResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_tags(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_tags(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_variables(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.get_variables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubGetVariablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_variables(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.get_variables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubGetVariablesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_variables(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.get_variables(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubGetVariablesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_variables(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.get_variables(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_invite_multiple_users(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_invite_multiple_users_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            emails=["dev@stainless.com"],
            project_role="member",
            tags=["string"],
        )
        assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_invite_multiple_users(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_invite_multiple_users(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.invite_multiple_users(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubInviteMultipleUsersResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_invite_multiple_users(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.invite_multiple_users(
                hub_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_permanently_delete(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.permanently_delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubPermanentlyDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_permanently_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.permanently_delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubPermanentlyDeleteResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_permanently_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.permanently_delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubPermanentlyDeleteResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_permanently_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.permanently_delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_remove_user(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.remove_user(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubRemoveUserResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_remove_user(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.remove_user(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubRemoveUserResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_remove_user(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.remove_user(
            firebase_id="firebase_id",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubRemoveUserResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_remove_user(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.remove_user(
                firebase_id="firebase_id",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `firebase_id` but received ''"):
            await async_client.hub.with_raw_response.remove_user(
                firebase_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_request_contributor_access(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.request_contributor_access(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_request_contributor_access(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.request_contributor_access(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_request_contributor_access(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.request_contributor_access(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_request_contributor_access(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.request_contributor_access(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_restore(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubRestoreResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_restore(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubRestoreResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_restore(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubRestoreResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_restore(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.restore(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_resources(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )
        assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_resources_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
            process_public_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search_resources(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search_resources(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.search_resources(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            search="search",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubSearchResourcesResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_search_resources(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.search_resources(
                hub_id="",
                search="search",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_column_coloring(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.set_column_coloring(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_set_column_coloring(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.set_column_coloring(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_set_column_coloring(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.set_column_coloring(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_set_column_coloring(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.set_column_coloring(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_column_format(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.set_column_format(
            kind="kind",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_set_column_format(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.set_column_format(
            kind="kind",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_set_column_format(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.set_column_format(
            kind="kind",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_set_column_format(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.set_column_format(
                kind="kind",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `kind` but received ''"):
            await async_client.hub.with_raw_response.set_column_format(
                kind="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_train_knowledge_base(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.train_knowledge_base(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_train_knowledge_base(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.train_knowledge_base(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert hub is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_train_knowledge_base(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.train_knowledge_base(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert hub is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_train_knowledge_base(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.train_knowledge_base(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_heading_styling(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_heading_styling_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            bold=True,
            colour="colour",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            font_size=0,
            italic=True,
            numbering_style=0,
            start_at0=True,
            underline=True,
        )
        assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_heading_styling(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_heading_styling(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.update_heading_styling(
            style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubUpdateHeadingStylingResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_heading_styling(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.update_heading_styling(
                style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `style_id` but received ''"):
            await async_client.hub.with_raw_response.update_heading_styling(
                style_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_upload_template(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_upload_template_with_all_params(self, async_client: AsyncMorta) -> None:
        hub = await async_client.hub.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            file=b"raw file contents",
        )
        assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upload_template(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.with_raw_response.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hub = await response.parse()
        assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upload_template(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.with_streaming_response.upload_template(
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hub = await response.parse()
            assert_matches_type(HubUploadTemplateResponse, hub, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_upload_template(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.with_raw_response.upload_template(
                hub_id="",
            )
