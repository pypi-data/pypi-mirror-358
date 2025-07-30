# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from trellis import Trellis, AsyncTrellis
from tests.utils import assert_matches_type
from trellis.types import Assets, AssetDeleteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAssets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Trellis) -> None:
        asset = client.assets.list()
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Trellis) -> None:
        asset = client.assets.list(
            asset_ids=["string"],
            entity_field_id="entity_field_id",
            entity_id="entity_id",
            limit=1,
            offset=0,
            operation_id="operation_id",
            order="asc",
            order_by="updated_at",
            proj_id="proj_id",
            row_id="row_id",
            status="uploading",
            transform_id="transform_id",
            api_version="2025-03",
        )
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Trellis) -> None:
        response = client.assets.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Trellis) -> None:
        with client.assets.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(Assets, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Trellis) -> None:
        asset = client.assets.delete(
            asset_id="asset_id",
        )
        assert_matches_type(AssetDeleteResponse, asset, path=["response"])

    @parametrize
    def test_method_delete_with_all_params(self, client: Trellis) -> None:
        asset = client.assets.delete(
            asset_id="asset_id",
            api_version="2025-03",
        )
        assert_matches_type(AssetDeleteResponse, asset, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Trellis) -> None:
        response = client.assets.with_raw_response.delete(
            asset_id="asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(AssetDeleteResponse, asset, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Trellis) -> None:
        with client.assets.with_streaming_response.delete(
            asset_id="asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(AssetDeleteResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Trellis) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            client.assets.with_raw_response.delete(
                asset_id="",
            )

    @parametrize
    def test_method_upload(self, client: Trellis) -> None:
        asset = client.assets.upload(
            urls=["string"],
        )
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    def test_method_upload_with_all_params(self, client: Trellis) -> None:
        asset = client.assets.upload(
            urls=["string"],
            cells=[
                {
                    "row_id": "your-first-row-id",
                    "field_id": "field_id",
                    "op_id": "your-first-operation-id",
                },
                {
                    "row_id": "your-second-row-id",
                    "field_id": "field_id",
                    "op_id": "your-second-operation-id",
                },
                {
                    "row_id": "your-third-row-id",
                    "field_id": "field_id",
                    "op_id": "your-third-operation-id",
                },
            ],
            chunk_strategy="chunk_strategy",
            entity_id="entity_id",
            ext_file_names=["string"],
            ext_ids=["string"],
            file_type="file_type",
            file_types=["string"],
            include_header=True,
            main_keys=["string"],
            parse_strategy="parse_strategy",
            process_with_workflow=True,
            proj_id="proj_id",
            transform_id="transform_id",
            api_version="2025-03",
        )
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    def test_raw_response_upload(self, client: Trellis) -> None:
        response = client.assets.with_raw_response.upload(
            urls=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    def test_streaming_response_upload(self, client: Trellis) -> None:
        with client.assets.with_streaming_response.upload(
            urls=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(Assets, asset, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAssets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncTrellis) -> None:
        asset = await async_client.assets.list()
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTrellis) -> None:
        asset = await async_client.assets.list(
            asset_ids=["string"],
            entity_field_id="entity_field_id",
            entity_id="entity_id",
            limit=1,
            offset=0,
            operation_id="operation_id",
            order="asc",
            order_by="updated_at",
            proj_id="proj_id",
            row_id="row_id",
            status="uploading",
            transform_id="transform_id",
            api_version="2025-03",
        )
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTrellis) -> None:
        response = await async_client.assets.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTrellis) -> None:
        async with async_client.assets.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(Assets, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncTrellis) -> None:
        asset = await async_client.assets.delete(
            asset_id="asset_id",
        )
        assert_matches_type(AssetDeleteResponse, asset, path=["response"])

    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncTrellis) -> None:
        asset = await async_client.assets.delete(
            asset_id="asset_id",
            api_version="2025-03",
        )
        assert_matches_type(AssetDeleteResponse, asset, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTrellis) -> None:
        response = await async_client.assets.with_raw_response.delete(
            asset_id="asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(AssetDeleteResponse, asset, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTrellis) -> None:
        async with async_client.assets.with_streaming_response.delete(
            asset_id="asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(AssetDeleteResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTrellis) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            await async_client.assets.with_raw_response.delete(
                asset_id="",
            )

    @parametrize
    async def test_method_upload(self, async_client: AsyncTrellis) -> None:
        asset = await async_client.assets.upload(
            urls=["string"],
        )
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncTrellis) -> None:
        asset = await async_client.assets.upload(
            urls=["string"],
            cells=[
                {
                    "row_id": "your-first-row-id",
                    "field_id": "field_id",
                    "op_id": "your-first-operation-id",
                },
                {
                    "row_id": "your-second-row-id",
                    "field_id": "field_id",
                    "op_id": "your-second-operation-id",
                },
                {
                    "row_id": "your-third-row-id",
                    "field_id": "field_id",
                    "op_id": "your-third-operation-id",
                },
            ],
            chunk_strategy="chunk_strategy",
            entity_id="entity_id",
            ext_file_names=["string"],
            ext_ids=["string"],
            file_type="file_type",
            file_types=["string"],
            include_header=True,
            main_keys=["string"],
            parse_strategy="parse_strategy",
            process_with_workflow=True,
            proj_id="proj_id",
            transform_id="transform_id",
            api_version="2025-03",
        )
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncTrellis) -> None:
        response = await async_client.assets.with_raw_response.upload(
            urls=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(Assets, asset, path=["response"])

    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncTrellis) -> None:
        async with async_client.assets.with_streaming_response.upload(
            urls=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(Assets, asset, path=["response"])

        assert cast(Any, response.is_closed) is True
