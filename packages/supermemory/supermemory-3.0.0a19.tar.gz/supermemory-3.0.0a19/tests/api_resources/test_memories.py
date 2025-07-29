# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from supermemory import Supermemory, AsyncSupermemory
from tests.utils import assert_matches_type
from supermemory.types import (
    MemoryAddResponse,
    MemoryGetResponse,
    MemoryUpdateResponse,
    MemoryUploadFileResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMemories:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Supermemory) -> None:
        memory = client.memories.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
        )
        assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Supermemory) -> None:
        memory = client.memories.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
            container_tags=["user_123", "project_123"],
            custom_id="mem_abc123",
            metadata={
                "source": "web",
                "category": "technology",
                "tag_1": "ai",
                "tag_2": "machine-learning",
                "readingTime": 5,
                "isPublic": True,
            },
        )
        assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Supermemory) -> None:
        response = client.memories.with_raw_response.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = response.parse()
        assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Supermemory) -> None:
        with client.memories.with_streaming_response.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = response.parse()
            assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Supermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.memories.with_raw_response.update(
                id="",
                content="This is a detailed article about machine learning concepts...",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Supermemory) -> None:
        memory = client.memories.delete(
            "id",
        )
        assert memory is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Supermemory) -> None:
        response = client.memories.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = response.parse()
        assert memory is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Supermemory) -> None:
        with client.memories.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = response.parse()
            assert memory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Supermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.memories.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_add(self, client: Supermemory) -> None:
        memory = client.memories.add(
            content="This is a detailed article about machine learning concepts...",
        )
        assert_matches_type(MemoryAddResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_add_with_all_params(self, client: Supermemory) -> None:
        memory = client.memories.add(
            content="This is a detailed article about machine learning concepts...",
            container_tags=["user_123", "project_123"],
            custom_id="mem_abc123",
            metadata={
                "source": "web",
                "category": "technology",
                "tag_1": "ai",
                "tag_2": "machine-learning",
                "readingTime": 5,
                "isPublic": True,
            },
        )
        assert_matches_type(MemoryAddResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_add(self, client: Supermemory) -> None:
        response = client.memories.with_raw_response.add(
            content="This is a detailed article about machine learning concepts...",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = response.parse()
        assert_matches_type(MemoryAddResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_add(self, client: Supermemory) -> None:
        with client.memories.with_streaming_response.add(
            content="This is a detailed article about machine learning concepts...",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = response.parse()
            assert_matches_type(MemoryAddResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Supermemory) -> None:
        memory = client.memories.get(
            "id",
        )
        assert_matches_type(MemoryGetResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Supermemory) -> None:
        response = client.memories.with_raw_response.get(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = response.parse()
        assert_matches_type(MemoryGetResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Supermemory) -> None:
        with client.memories.with_streaming_response.get(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = response.parse()
            assert_matches_type(MemoryGetResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Supermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.memories.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_upload_file(self, client: Supermemory) -> None:
        memory = client.memories.upload_file(
            file=b"raw file contents",
        )
        assert_matches_type(MemoryUploadFileResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upload_file(self, client: Supermemory) -> None:
        response = client.memories.with_raw_response.upload_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = response.parse()
        assert_matches_type(MemoryUploadFileResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upload_file(self, client: Supermemory) -> None:
        with client.memories.with_streaming_response.upload_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = response.parse()
            assert_matches_type(MemoryUploadFileResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMemories:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncSupermemory) -> None:
        memory = await async_client.memories.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
        )
        assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncSupermemory) -> None:
        memory = await async_client.memories.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
            container_tags=["user_123", "project_123"],
            custom_id="mem_abc123",
            metadata={
                "source": "web",
                "category": "technology",
                "tag_1": "ai",
                "tag_2": "machine-learning",
                "readingTime": 5,
                "isPublic": True,
            },
        )
        assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSupermemory) -> None:
        response = await async_client.memories.with_raw_response.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = await response.parse()
        assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSupermemory) -> None:
        async with async_client.memories.with_streaming_response.update(
            id="id",
            content="This is a detailed article about machine learning concepts...",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = await response.parse()
            assert_matches_type(MemoryUpdateResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncSupermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.memories.with_raw_response.update(
                id="",
                content="This is a detailed article about machine learning concepts...",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncSupermemory) -> None:
        memory = await async_client.memories.delete(
            "id",
        )
        assert memory is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncSupermemory) -> None:
        response = await async_client.memories.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = await response.parse()
        assert memory is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncSupermemory) -> None:
        async with async_client.memories.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = await response.parse()
            assert memory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncSupermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.memories.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_add(self, async_client: AsyncSupermemory) -> None:
        memory = await async_client.memories.add(
            content="This is a detailed article about machine learning concepts...",
        )
        assert_matches_type(MemoryAddResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_add_with_all_params(self, async_client: AsyncSupermemory) -> None:
        memory = await async_client.memories.add(
            content="This is a detailed article about machine learning concepts...",
            container_tags=["user_123", "project_123"],
            custom_id="mem_abc123",
            metadata={
                "source": "web",
                "category": "technology",
                "tag_1": "ai",
                "tag_2": "machine-learning",
                "readingTime": 5,
                "isPublic": True,
            },
        )
        assert_matches_type(MemoryAddResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_add(self, async_client: AsyncSupermemory) -> None:
        response = await async_client.memories.with_raw_response.add(
            content="This is a detailed article about machine learning concepts...",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = await response.parse()
        assert_matches_type(MemoryAddResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncSupermemory) -> None:
        async with async_client.memories.with_streaming_response.add(
            content="This is a detailed article about machine learning concepts...",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = await response.parse()
            assert_matches_type(MemoryAddResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncSupermemory) -> None:
        memory = await async_client.memories.get(
            "id",
        )
        assert_matches_type(MemoryGetResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSupermemory) -> None:
        response = await async_client.memories.with_raw_response.get(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = await response.parse()
        assert_matches_type(MemoryGetResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSupermemory) -> None:
        async with async_client.memories.with_streaming_response.get(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = await response.parse()
            assert_matches_type(MemoryGetResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSupermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.memories.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_upload_file(self, async_client: AsyncSupermemory) -> None:
        memory = await async_client.memories.upload_file(
            file=b"raw file contents",
        )
        assert_matches_type(MemoryUploadFileResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upload_file(self, async_client: AsyncSupermemory) -> None:
        response = await async_client.memories.with_raw_response.upload_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        memory = await response.parse()
        assert_matches_type(MemoryUploadFileResponse, memory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upload_file(self, async_client: AsyncSupermemory) -> None:
        async with async_client.memories.with_streaming_response.upload_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            memory = await response.parse()
            assert_matches_type(MemoryUploadFileResponse, memory, path=["response"])

        assert cast(Any, response.is_closed) is True
