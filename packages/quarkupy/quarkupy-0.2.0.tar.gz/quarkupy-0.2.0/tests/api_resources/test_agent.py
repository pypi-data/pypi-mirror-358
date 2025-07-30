# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quarkupy, AsyncQuarkupy
from tests.utils import assert_matches_type
from quarkupy.types import AgentRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAgent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quarkupy) -> None:
        agent = client.agent.retrieve()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quarkupy) -> None:
        response = client.agent.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quarkupy) -> None:
        with client.agent.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_chat_rag_demo(self, client: Quarkupy) -> None:
        agent = client.agent.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_chat_rag_demo_with_all_params(self, client: Quarkupy) -> None:
        agent = client.agent.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
            search_limit=0,
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_chat_rag_demo(self, client: Quarkupy) -> None:
        response = client.agent.with_raw_response.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_chat_rag_demo(self, client: Quarkupy) -> None:
        with client.agent.with_streaming_response.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(object, agent, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAgent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuarkupy) -> None:
        agent = await async_client.agent.retrieve()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuarkupy) -> None:
        response = await async_client.agent.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuarkupy) -> None:
        async with async_client.agent.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_chat_rag_demo(self, async_client: AsyncQuarkupy) -> None:
        agent = await async_client.agent.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_chat_rag_demo_with_all_params(self, async_client: AsyncQuarkupy) -> None:
        agent = await async_client.agent.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
            search_limit=0,
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_chat_rag_demo(self, async_client: AsyncQuarkupy) -> None:
        response = await async_client.agent.with_raw_response.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_chat_rag_demo(self, async_client: AsyncQuarkupy) -> None:
        async with async_client.agent.with_streaming_response.create_chat_rag_demo(
            openai_api_key="openai_api_key",
            query="query",
            table_name="table_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(object, agent, path=["response"])

        assert cast(Any, response.is_closed) is True
