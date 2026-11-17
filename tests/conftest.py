"""Shared fixtures: an offline SIDOF served from recorded JSON files."""

from __future__ import annotations

import json
import os
import re
from collections.abc import AsyncIterator, Callable
from pathlib import Path

import httpx
import pytest
from fastmcp import Client

from mcp_dof import server
from mcp_dof.client import SidofClient

FIXTURES = Path(__file__).parent / "fixtures"
API_PREFIX = "/dof/sidof/"

EMPTY_DAY = {
    "messageCode": 200,
    "response": "OK",
    "NotasExtraordinarias": [],
    "imagenesDiario": [],
    "NotasVespertinas": [],
    "NotasMatutinas": [],
    "audioSumario": [],
}
_DAY_PATH = re.compile(r"^notas/\d{2}-\d{2}-\d{4}$")
_INDICATOR_DAY_PATH = re.compile(r"^indicadores/\d{2}-\d{2}-\d{4}$")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--live", action="store_true", help="run tests against the real SIDOF API")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--live") or os.environ.get("MCP_DOF_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="live test: pass --live or set MCP_DOF_LIVE=1")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def load_fixture(api_path: str) -> dict:
    name = api_path.strip("/").replace("/", "__") + ".json"
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FakeSidof:
    """Serves recorded fixtures; unknown days behave like holidays."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.overrides: dict[str, list[httpx.Response]] = {}

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path.removeprefix(API_PREFIX)
        if queued := self.overrides.get(path):
            return queued.pop(0)
        try:
            return httpx.Response(200, json=load_fixture(path))
        except FileNotFoundError:
            if _DAY_PATH.match(path):
                return httpx.Response(200, json=EMPTY_DAY)
            if _INDICATOR_DAY_PATH.match(path):
                return httpx.Response(200, json={"messageCode": 200, "response": "OK"})
            return httpx.Response(404, json={"messageCode": 404, "response": "not recorded"})

    def paths(self) -> list[str]:
        return [r.url.path.removeprefix(API_PREFIX) for r in self.requests]


@pytest.fixture
def fake_sidof() -> FakeSidof:
    return FakeSidof()


@pytest.fixture
def make_client(fake_sidof: FakeSidof) -> Callable[..., SidofClient]:
    def factory(**kwargs: object) -> SidofClient:
        options = {"min_interval": 0.0, "backoff": 0.0} | kwargs
        return SidofClient(transport=httpx.MockTransport(fake_sidof), **options)

    return factory


@pytest.fixture
async def sidof(make_client: Callable[..., SidofClient]) -> AsyncIterator[SidofClient]:
    client = make_client()
    yield client
    await client.aclose()


@pytest.fixture
async def mcp_client(sidof: SidofClient) -> AsyncIterator[Client]:
    server.set_client(sidof)
    async with Client(server.mcp) as client:
        yield client
    server.set_client(None)
