# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from trellis import Trellis, AsyncTrellis
from tests.utils import assert_matches_type
from trellis.types import (
    TransformListResponse,
    TransformCreateResponse,
    TransformUpdateResponse,
    TransformAutoschemaResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTransforms:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Trellis) -> None:
        transform = client.transforms.create(
            proj_id="proj_id",
            transform_params={"model": "model"},
        )
        assert_matches_type(TransformCreateResponse, transform, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Trellis) -> None:
        transform = client.transforms.create(
            proj_id="proj_id",
            transform_params={
                "model": "model",
                "mode": "document",
                "operations": [
                    {
                        "column_name": "column_name",
                        "column_type": "text",
                        "task_description": "Derive the invoice amount from {{Invoices}}, and add it to the rent from {{Rent Amount}}.",
                        "transform_type": "extraction",
                        "api_request": {
                            "method": "GET",
                            "url": "url",
                            "body": {},
                            "headers": {},
                        },
                        "default_value": {},
                        "has_default": True,
                        "operations": [{}],
                        "options": [
                            {
                                "color": "red",
                                "name": "name",
                                "visual_index": 0,
                                "linked_entity_id": "linked_entity_id",
                            }
                        ],
                        "output_values": {"foo": "string"},
                        "prompt_type": "text",
                        "run_function_code": "run_function_code",
                    }
                ],
                "table_preferences": {
                    "advanced_reasoning": True,
                    "included_table_names": ["string"],
                },
            },
            actions={"run_on_extract": True},
            transform_name="transform_name",
            api_version="2025-03",
        )
        assert_matches_type(TransformCreateResponse, transform, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Trellis) -> None:
        response = client.transforms.with_raw_response.create(
            proj_id="proj_id",
            transform_params={"model": "model"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = response.parse()
        assert_matches_type(TransformCreateResponse, transform, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Trellis) -> None:
        with client.transforms.with_streaming_response.create(
            proj_id="proj_id",
            transform_params={"model": "model"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = response.parse()
            assert_matches_type(TransformCreateResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Trellis) -> None:
        transform = client.transforms.update(
            transform_id="transform_id",
        )
        assert_matches_type(TransformUpdateResponse, transform, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Trellis) -> None:
        transform = client.transforms.update(
            transform_id="transform_id",
            asset_ids=["string"],
            include_reference=True,
            row_ids=["string"],
            api_version="2025-03",
        )
        assert_matches_type(TransformUpdateResponse, transform, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Trellis) -> None:
        response = client.transforms.with_raw_response.update(
            transform_id="transform_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = response.parse()
        assert_matches_type(TransformUpdateResponse, transform, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Trellis) -> None:
        with client.transforms.with_streaming_response.update(
            transform_id="transform_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = response.parse()
            assert_matches_type(TransformUpdateResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Trellis) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transform_id` but received ''"):
            client.transforms.with_raw_response.update(
                transform_id="",
            )

    @parametrize
    def test_method_list(self, client: Trellis) -> None:
        transform = client.transforms.list()
        assert_matches_type(TransformListResponse, transform, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Trellis) -> None:
        transform = client.transforms.list(
            include_transform_params=True,
            limit=1,
            offset=0,
            order="asc",
            order_by="updated_at",
            proj_ids=["string"],
            search_term="search_term",
            transform_ids=["string"],
            api_version="2025-03",
        )
        assert_matches_type(TransformListResponse, transform, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Trellis) -> None:
        response = client.transforms.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = response.parse()
        assert_matches_type(TransformListResponse, transform, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Trellis) -> None:
        with client.transforms.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = response.parse()
            assert_matches_type(TransformListResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_autoschema(self, client: Trellis) -> None:
        transform = client.transforms.autoschema(
            transform_id="transform_id",
        )
        assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

    @parametrize
    def test_method_autoschema_with_all_params(self, client: Trellis) -> None:
        transform = client.transforms.autoschema(
            transform_id="transform_id",
            api_version="2025-03",
        )
        assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

    @parametrize
    def test_raw_response_autoschema(self, client: Trellis) -> None:
        response = client.transforms.with_raw_response.autoschema(
            transform_id="transform_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = response.parse()
        assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

    @parametrize
    def test_streaming_response_autoschema(self, client: Trellis) -> None:
        with client.transforms.with_streaming_response.autoschema(
            transform_id="transform_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = response.parse()
            assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_autoschema(self, client: Trellis) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transform_id` but received ''"):
            client.transforms.with_raw_response.autoschema(
                transform_id="",
            )


class TestAsyncTransforms:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.create(
            proj_id="proj_id",
            transform_params={"model": "model"},
        )
        assert_matches_type(TransformCreateResponse, transform, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.create(
            proj_id="proj_id",
            transform_params={
                "model": "model",
                "mode": "document",
                "operations": [
                    {
                        "column_name": "column_name",
                        "column_type": "text",
                        "task_description": "Derive the invoice amount from {{Invoices}}, and add it to the rent from {{Rent Amount}}.",
                        "transform_type": "extraction",
                        "api_request": {
                            "method": "GET",
                            "url": "url",
                            "body": {},
                            "headers": {},
                        },
                        "default_value": {},
                        "has_default": True,
                        "operations": [{}],
                        "options": [
                            {
                                "color": "red",
                                "name": "name",
                                "visual_index": 0,
                                "linked_entity_id": "linked_entity_id",
                            }
                        ],
                        "output_values": {"foo": "string"},
                        "prompt_type": "text",
                        "run_function_code": "run_function_code",
                    }
                ],
                "table_preferences": {
                    "advanced_reasoning": True,
                    "included_table_names": ["string"],
                },
            },
            actions={"run_on_extract": True},
            transform_name="transform_name",
            api_version="2025-03",
        )
        assert_matches_type(TransformCreateResponse, transform, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTrellis) -> None:
        response = await async_client.transforms.with_raw_response.create(
            proj_id="proj_id",
            transform_params={"model": "model"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = await response.parse()
        assert_matches_type(TransformCreateResponse, transform, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTrellis) -> None:
        async with async_client.transforms.with_streaming_response.create(
            proj_id="proj_id",
            transform_params={"model": "model"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = await response.parse()
            assert_matches_type(TransformCreateResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.update(
            transform_id="transform_id",
        )
        assert_matches_type(TransformUpdateResponse, transform, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.update(
            transform_id="transform_id",
            asset_ids=["string"],
            include_reference=True,
            row_ids=["string"],
            api_version="2025-03",
        )
        assert_matches_type(TransformUpdateResponse, transform, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTrellis) -> None:
        response = await async_client.transforms.with_raw_response.update(
            transform_id="transform_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = await response.parse()
        assert_matches_type(TransformUpdateResponse, transform, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTrellis) -> None:
        async with async_client.transforms.with_streaming_response.update(
            transform_id="transform_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = await response.parse()
            assert_matches_type(TransformUpdateResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTrellis) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transform_id` but received ''"):
            await async_client.transforms.with_raw_response.update(
                transform_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.list()
        assert_matches_type(TransformListResponse, transform, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.list(
            include_transform_params=True,
            limit=1,
            offset=0,
            order="asc",
            order_by="updated_at",
            proj_ids=["string"],
            search_term="search_term",
            transform_ids=["string"],
            api_version="2025-03",
        )
        assert_matches_type(TransformListResponse, transform, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTrellis) -> None:
        response = await async_client.transforms.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = await response.parse()
        assert_matches_type(TransformListResponse, transform, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTrellis) -> None:
        async with async_client.transforms.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = await response.parse()
            assert_matches_type(TransformListResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_autoschema(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.autoschema(
            transform_id="transform_id",
        )
        assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

    @parametrize
    async def test_method_autoschema_with_all_params(self, async_client: AsyncTrellis) -> None:
        transform = await async_client.transforms.autoschema(
            transform_id="transform_id",
            api_version="2025-03",
        )
        assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

    @parametrize
    async def test_raw_response_autoschema(self, async_client: AsyncTrellis) -> None:
        response = await async_client.transforms.with_raw_response.autoschema(
            transform_id="transform_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transform = await response.parse()
        assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

    @parametrize
    async def test_streaming_response_autoschema(self, async_client: AsyncTrellis) -> None:
        async with async_client.transforms.with_streaming_response.autoschema(
            transform_id="transform_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transform = await response.parse()
            assert_matches_type(TransformAutoschemaResponse, transform, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_autoschema(self, async_client: AsyncTrellis) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transform_id` but received ''"):
            await async_client.transforms.with_raw_response.autoschema(
                transform_id="",
            )
