# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from supermemory import Supermemory, AsyncSupermemory
from tests.utils import assert_matches_type
from supermemory.types import ConnectionGetResponse, ConnectionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConnections:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Supermemory) -> None:
        connection = client.connections.create(
            provider="notion",
        )
        assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Supermemory) -> None:
        connection = client.connections.create(
            provider="notion",
            container_tags=["string"],
            document_limit=1,
            metadata={"foo": "string"},
            redirect_url="redirectUrl",
        )
        assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Supermemory) -> None:
        response = client.connections.with_raw_response.create(
            provider="notion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Supermemory) -> None:
        with client.connections.with_streaming_response.create(
            provider="notion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Supermemory) -> None:
        connection = client.connections.get(
            "connectionId",
        )
        assert_matches_type(ConnectionGetResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Supermemory) -> None:
        response = client.connections.with_raw_response.get(
            "connectionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(ConnectionGetResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Supermemory) -> None:
        with client.connections.with_streaming_response.get(
            "connectionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(ConnectionGetResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Supermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            client.connections.with_raw_response.get(
                "",
            )


class TestAsyncConnections:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncSupermemory) -> None:
        connection = await async_client.connections.create(
            provider="notion",
        )
        assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSupermemory) -> None:
        connection = await async_client.connections.create(
            provider="notion",
            container_tags=["string"],
            document_limit=1,
            metadata={"foo": "string"},
            redirect_url="redirectUrl",
        )
        assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSupermemory) -> None:
        response = await async_client.connections.with_raw_response.create(
            provider="notion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSupermemory) -> None:
        async with async_client.connections.with_streaming_response.create(
            provider="notion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(ConnectionCreateResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncSupermemory) -> None:
        connection = await async_client.connections.get(
            "connectionId",
        )
        assert_matches_type(ConnectionGetResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSupermemory) -> None:
        response = await async_client.connections.with_raw_response.get(
            "connectionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(ConnectionGetResponse, connection, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSupermemory) -> None:
        async with async_client.connections.with_streaming_response.get(
            "connectionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(ConnectionGetResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSupermemory) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            await async_client.connections.with_raw_response.get(
                "",
            )
