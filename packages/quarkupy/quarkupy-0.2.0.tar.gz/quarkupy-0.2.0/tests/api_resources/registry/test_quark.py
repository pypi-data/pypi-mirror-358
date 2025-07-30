# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quarkupy, AsyncQuarkupy
from tests.utils import assert_matches_type
from quarkupy.types.registry import QuarkRegistryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestQuark:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quarkupy) -> None:
        quark = client.registry.quark.retrieve(
            name="name",
            cat="cat",
        )
        assert_matches_type(QuarkRegistryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quarkupy) -> None:
        response = client.registry.quark.with_raw_response.retrieve(
            name="name",
            cat="cat",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quark = response.parse()
        assert_matches_type(QuarkRegistryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quarkupy) -> None:
        with client.registry.quark.with_streaming_response.retrieve(
            name="name",
            cat="cat",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quark = response.parse()
            assert_matches_type(QuarkRegistryItem, quark, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Quarkupy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cat` but received ''"):
            client.registry.quark.with_raw_response.retrieve(
                name="name",
                cat="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.registry.quark.with_raw_response.retrieve(
                name="",
                cat="cat",
            )


class TestAsyncQuark:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuarkupy) -> None:
        quark = await async_client.registry.quark.retrieve(
            name="name",
            cat="cat",
        )
        assert_matches_type(QuarkRegistryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuarkupy) -> None:
        response = await async_client.registry.quark.with_raw_response.retrieve(
            name="name",
            cat="cat",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quark = await response.parse()
        assert_matches_type(QuarkRegistryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuarkupy) -> None:
        async with async_client.registry.quark.with_streaming_response.retrieve(
            name="name",
            cat="cat",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quark = await response.parse()
            assert_matches_type(QuarkRegistryItem, quark, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncQuarkupy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cat` but received ''"):
            await async_client.registry.quark.with_raw_response.retrieve(
                name="name",
                cat="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.registry.quark.with_raw_response.retrieve(
                name="",
                cat="cat",
            )
