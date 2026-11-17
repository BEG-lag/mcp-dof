"""Keep the version, server.json, Dockerfile and docs in step (MCP Registry metadata)."""

import json
import re
import tomllib
from pathlib import Path

import pytest

from mcp_dof import __version__

ROOT = Path(__file__).resolve().parent.parent
IMAGE = "ghcr.io/beg-lag/mcp-dof"
SERVER = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))


def test_pyproject_version_matches_package() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == __version__


def test_server_json_version_and_image_tag() -> None:
    assert SERVER["version"] == __version__
    (package,) = SERVER["packages"]
    assert package["registryType"] == "oci"
    assert package["identifier"] == f"{IMAGE}:{__version__}"
    assert "version" not in package  # the registry rejects it for OCI packages


def test_server_json_name_and_description() -> None:
    assert SERVER["name"] == "io.github.BEG-lag/mcp-dof"  # GitHub auth namespace, case-sensitive
    assert len(SERVER["description"]) <= 100


def test_dockerfile_label_proves_ownership() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    label = re.search(r'io\.modelcontextprotocol\.server\.name="([^"]+)"', dockerfile)
    assert label, "Dockerfile must set the io.modelcontextprotocol.server.name label"
    assert label.group(1) == SERVER["name"]


def test_readme_carries_mcp_name() -> None:
    assert f"mcp-name: {SERVER['name']}" in (ROOT / "README.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", ["README.md", "README.es.md", "Dockerfile", "server.json"])
def test_pinned_image_tags_are_current(name: str) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    tags = set(re.findall(re.escape(IMAGE) + r":(\d+\.\d+\.\d+)", text))
    assert tags <= {__version__}, f"{name} pins {sorted(tags)}, current is {__version__}"
