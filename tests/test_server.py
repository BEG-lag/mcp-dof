"""End-to-end tests through a real MCP client session (in memory, no network)."""

import json

import pytest

pytestmark = pytest.mark.anyio

TOOLS = {"list_edition", "get_note", "search_notes", "get_indicators", "get_indicator_history"}


async def call(client, tool: str, **arguments) -> str:
    result = await client.call_tool(tool, arguments)
    assert not result.is_error, result.content
    return result.content[0].text


async def call_error(client, tool: str, **arguments) -> str:
    result = await client.call_tool(tool, arguments, raise_on_error=False)
    assert result.is_error
    return result.content[0].text


async def test_tools_are_listed_as_read_only(mcp_client) -> None:
    tools = {t.name: t for t in await mcp_client.list_tools()}
    assert set(tools) == TOOLS
    for tool in tools.values():
        assert tool.annotations.read_only_hint is True
        assert tool.description


async def test_prompts_and_resources_are_listed(mcp_client) -> None:
    prompts = {p.name for p in await mcp_client.list_prompts()}
    assert prompts == {"regulatory_digest"}
    templates = {t.uri_template for t in await mcp_client.list_resource_templates()}
    assert templates == {"dof://edition/{date}", "dof://note/{code}"}
    resources = {str(r.uri) for r in await mcp_client.list_resources()}
    assert resources == {"dof://practice-areas"}


async def test_list_edition_groups_by_issuer_and_hides_avisos(mcp_client) -> None:
    text = await call(mcp_client, "list_edition", date="2026-11-13")
    assert text.startswith("# DOF 2026-11-13 · Friday")
    assert "66 notes in 2 edition(s): matutina, vespertina." in text
    assert "44 avisos judiciales y generales hidden" in text
    assert "**PODER EJECUTIVO › PRESIDENCIA DE LA REPUBLICA**" in text
    assert "`5803757` Decreto por el que se expide la Ley de Ingresos" in text
    assert "[edition PDF](https://sidof.segob.gob.mx/dof/sidof/documentos/pdf/330805)" in text
    assert "Aviso REF" not in text
    assert "Only the printed/official DOF is authoritative" in text


async def test_list_edition_can_include_avisos_and_filter_editions(mcp_client) -> None:
    with_avisos = await call(mcp_client, "list_edition", date="13-11-2026", include_avisos=True)
    assert "Aviso REF:" in with_avisos
    evening = await call(mcp_client, "list_edition", date="2026-11-13", edition="vespertina")
    assert "## Edición vespertina" in evening
    assert "## Edición matutina" not in evening


async def test_list_edition_on_a_holiday_points_to_the_last_edition(mcp_client) -> None:
    text = await call(mcp_client, "list_edition", date="2026-11-16")
    assert "No DOF edition was published on 2026-11-16 (Monday)" in text
    assert "most recent earlier edition is from 2026-11-13 (Friday)" in text


async def test_list_edition_rejects_bad_dates(mcp_client) -> None:
    message = await call_error(mcp_client, "list_edition", date="13 de noviembre")
    assert "YYYY-MM-DD" in message


async def test_get_note_returns_markdown_with_metadata(mcp_client) -> None:
    text = await call(mcp_client, "get_note", code=5803775)
    assert text.startswith("# Tipo de cambio para solventar obligaciones")
    assert "| Published | 2026-11-13 (matutina) |" in text
    assert "| Official page | https://dof.gob.mx/nota_detalle.php?codigo=5803775" in text
    assert "**Pilar María Figueredo Díaz**" in text
    assert "End of note." in text


async def test_get_note_paginates_long_text(mcp_client) -> None:
    first = await call(mcp_client, "get_note", code=5803775, max_chars=1000)
    assert "More text available: call get_note(code=5803775, start=" in first
    start = int(first.split("start=")[1].split(")")[0])
    second = await call(mcp_client, "get_note", code=5803775, start=start)
    assert "End of note." in second
    assert "Rúbrica." in second


async def test_get_note_unknown_code(mcp_client) -> None:
    message = await call_error(mcp_client, "get_note", code=9999999)
    assert "There is no DOF note with code 9999999" in message


async def test_search_notes_matches_titles_across_days(mcp_client) -> None:
    text = await call(
        mcp_client,
        "search_notes",
        query="tipo de cambio",
        date_from="2026-11-11",
        date_to="2026-11-16",
    )
    assert "scanned 6 days (3 with publications" in text
    assert "Found 3 matching notes." in text
    assert text.index("**2026-11-13**") < text.index("**2026-11-11**")  # newest first


async def test_search_notes_with_practice_area_and_edition(mcp_client) -> None:
    text = await call(
        mcp_client,
        "search_notes",
        practice_area="fiscal",
        edition="vespertina",
        date_from="2026-11-13",
        date_to="2026-11-13",
    )
    assert "practice area `fiscal`" in text
    assert "estímulo fiscal" in text
    assert "matutina" not in text


async def test_search_notes_validates_input(mcp_client) -> None:
    assert "Pass a query" in await call_error(mcp_client, "search_notes", date_to="2026-11-13")
    too_wide = await call_error(
        mcp_client, "search_notes", query="ley", date_from="2026-01-01", date_to="2026-11-13"
    )
    assert "maximum is 92" in too_wide


async def test_get_indicators_completes_weekends(mcp_client) -> None:
    text = await call(mcp_client, "get_indicators", date="2026-11-15")
    assert "| Tipo de cambio FIX (dólar) | 18.6188 | MXN per USD | 2026-11-13 | `usd` |" in text
    assert "| UDIS | 8.909257 | MXN per UDI | 2026-11-15 | `udis` |" in text


async def test_get_indicator_history(mcp_client) -> None:
    text = await call(
        mcp_client,
        "get_indicator_history",
        indicator="usd",
        date_from="2026-11-01",
        date_to="2026-11-13",
    )
    assert "9 published values (MXN per USD)" in text
    assert "| 2026-11-13 | 18.6188 |" in text


async def test_regulatory_digest_prompt(mcp_client) -> None:
    prompt = await mcp_client.get_prompt(
        "regulatory_digest", {"practice_area": "hidrocarburos", "date_from": "2026-11-01"}
    )
    text = prompt.messages[0].content.text
    assert 'Prepare a regulatory digest for the practice area "Hidrocarburos"' in text
    assert 'search_notes(practice_area="hidrocarburos", date_from="2026-11-01"' in text
    assert "not legal advice" in text


async def test_edition_resource_is_json(mcp_client) -> None:
    contents = await mcp_client.read_resource("dof://edition/2026-11-13")
    data = json.loads(contents[0].text)
    assert data["total"] == 66
    assert data["notes"][0]["official_url"].startswith("https://dof.gob.mx/nota_detalle.php")


async def test_practice_areas_resource(mcp_client) -> None:
    contents = await mcp_client.read_resource("dof://practice-areas")
    keys = {area["key"] for area in json.loads(contents[0].text)}
    assert {"energia", "hidrocarburos", "mineria"} <= keys
