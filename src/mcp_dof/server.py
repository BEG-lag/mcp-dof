"""The mcp-dof MCP server: tools, resources and prompts over the SIDOF API."""

from __future__ import annotations

import argparse
import json
import os
from datetime import timedelta
from typing import Annotated, Literal

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from . import __version__
from .client import NoteNotFoundError, SidofClient, SidofError
from .dates import DateError, iter_days, parse_date, parse_range
from .formatting import (
    render_edition,
    render_indicators,
    render_note,
    render_search,
    render_series,
)
from .markdown import html_to_markdown, slice_text
from .models import INDICATORS, Edition, NoteRef
from .search import PRACTICE_AREAS, QueryError, parse_query, practice_area_query

INSTRUCTIONS = """\
Tools for Mexico's Diario Oficial de la Federación (DOF), the official gazette where
federal laws, decrees, regulations, NOMs and agency resolutions are published.

Typical flow: list_edition (what was published on a day) or search_notes (titles over
a date range, optionally with a practice_area preset) -> get_note (full text as
Markdown, paginated with `start`). get_indicators and get_indicator_history return the
exchange rate (FIX), UDIS and TIIE published in the DOF.

Dates accept YYYY-MM-DD, DD-MM-YYYY, 'today' or 'yesterday' (Mexico City time).
Always cite the official link returned by the tools. The data comes from the public
SIDOF API; only the printed/official DOF is authoritative and nothing here is legal
advice.
"""

READ_ONLY = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}

EditionChoice = Literal["all", "matutina", "vespertina", "extraordinaria"]
IndicatorKey = Literal[
    "usd", "udis", "tiie28", "tiie91", "tiie182", "tiie_fondeo", "cpp", "ccp", "ccp_udis", "ccp_usd"
]


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


MAX_SEARCH_DAYS = _env_int("MCP_DOF_MAX_SEARCH_DAYS", 92)
MAX_SERIES_DAYS = 400

_client: SidofClient | None = None


def get_client() -> SidofClient:
    """Return the shared SIDOF client, creating it on first use."""
    global _client
    if _client is None:
        _client = SidofClient(
            timeout=_env_float("MCP_DOF_TIMEOUT", 20.0),
            min_interval=_env_float("MCP_DOF_MIN_INTERVAL", 0.25),
        )
    return _client


def set_client(client: SidofClient | None) -> None:
    """Swap the shared client (used by tests to inject a mock transport)."""
    global _client
    _client = client


def _editions(choice: str) -> list[Edition]:
    if choice == "all":
        return list(Edition)
    return [Edition(choice)]


mcp = FastMCP(
    name="dof",
    instructions=INSTRUCTIONS,
    version=__version__,
    website_url="https://github.com/BEG-lag/mcp-dof",
)


# ---------------------------------------------------------------------- tools


@mcp.tool(annotations=READ_ONLY)
async def list_edition(
    date: Annotated[
        str, Field(description="Publication date: YYYY-MM-DD, DD-MM-YYYY, 'today' or 'yesterday'.")
    ] = "today",
    edition: Annotated[
        EditionChoice, Field(description="Which edition to list. 'all' lists every edition.")
    ] = "all",
    include_avisos: Annotated[
        bool,
        Field(
            description="Also list 'avisos judiciales y generales' (edictos, notices). "
            "They are numerous and usually noise, so they are hidden by default."
        ),
    ] = False,
) -> str:
    """List the DOF table of contents for a day, grouped by edition and issuing agency.

    Each note shows its code (use it with get_note), title, page and official link.
    """
    try:
        day = parse_date(date)
        client = get_client()
        index = await client.day_index(day)
        latest = None
        selected = _editions(edition)
        if not any(n.edition in selected for n in index.notes):
            for previous in iter_days(
                day - timedelta(days=7), day - timedelta(days=1), newest_first=True
            ):
                earlier = await client.day_index(previous)
                if any(n.edition in selected for n in earlier.notes):
                    latest = previous
                    break
    except (DateError, SidofError) as exc:
        raise ToolError(str(exc)) from exc
    return render_edition(
        index, editions=selected, include_avisos=include_avisos, latest_day=latest
    )


@mcp.tool(annotations=READ_ONLY)
async def get_note(
    code: Annotated[
        int,
        Field(description="Note code (codNota), e.g. 5803775. Returned by the other tools.", gt=0),
    ],
    start: Annotated[
        int, Field(description="Character offset to start from, for long notes.", ge=0)
    ] = 0,
    max_chars: Annotated[
        int, Field(description="Maximum characters of body text to return.", ge=1000, le=100_000)
    ] = 20_000,
) -> str:
    """Get the full text of a DOF note as clean Markdown, with metadata and official links.

    Long instruments (laws, budgets, NOMs) are paginated: the footer tells you the `start`
    value for the next call.
    """
    try:
        note = await get_client().note(code)
    except NoteNotFoundError as exc:
        raise ToolError(f"{exc} Check the code with list_edition or search_notes.") from exc
    except SidofError as exc:
        raise ToolError(str(exc)) from exc
    markdown = html_to_markdown(note.html) if note.html else ""
    if start and start >= len(markdown):
        raise ToolError(
            f"start={start} is past the end of the note ({len(markdown):,} characters)."
        )
    body, next_start = slice_text(markdown, start, max_chars)
    return render_note(note, body, start=start, next_start=next_start, total_chars=len(markdown))


@mcp.tool(annotations=READ_ONLY)
async def search_notes(
    ctx: Context,
    query: Annotated[
        str,
        Field(
            description="Keywords matched against titles and issuing agencies, accent and case "
            'insensitive. Words are prefixes (eléctric matches eléctrica). Use "quotes" for '
            "phrases and | for alternatives, e.g. 'hidrocarburos | \"gas natural\"'. Optional "
            "when practice_area is given."
        ),
    ] = "",
    date_from: Annotated[
        str | None, Field(description="Start date (inclusive). Defaults to 30 days before date_to.")
    ] = None,
    date_to: Annotated[
        str | None, Field(description="End date (inclusive). Defaults to today.")
    ] = None,
    practice_area: Annotated[
        str | None,
        Field(
            description="Preset keyword set: "
            + ", ".join(sorted(PRACTICE_AREAS))
            + ". Combined with query using AND when both are given."
        ),
    ] = None,
    edition: Annotated[EditionChoice, Field(description="Restrict to one edition.")] = "all",
    include_avisos: Annotated[
        bool, Field(description="Include avisos judiciales y generales (titles are usually codes).")
    ] = False,
    limit: Annotated[int, Field(description="Maximum results to return.", ge=1, le=200)] = 50,
) -> str:
    """Search DOF note titles over a date range (up to 92 days per call), newest first.

    SIDOF has no working full-text search, so this scans each day's table of contents.
    Results are cached, so refining a query over the same range is fast.
    """
    try:
        start, end = parse_range(date_from, date_to, default_days=30, max_days=MAX_SEARCH_DAYS)
        filters = []
        if query.strip():
            filters.append(parse_query(query))
        if practice_area:
            filters.append(practice_area_query(practice_area))
        if not filters:
            raise QueryError("Pass a query, a practice_area, or both.")
    except (DateError, QueryError) as exc:
        raise ToolError(str(exc)) from exc

    label = " AND ".join(
        [f"`{query.strip()}`"] * bool(query.strip())
        + [f"practice area `{practice_area}`"] * bool(practice_area)
    )
    editions = _editions(edition)
    client = get_client()
    days = list(iter_days(start, end, newest_first=True))
    matches: list[NoteRef] = []
    days_with_notes = notes_scanned = 0
    for i, day in enumerate(days, start=1):
        try:
            index = await client.day_index(day)
        except SidofError as exc:
            raise ToolError(f"{exc} (while scanning {day.isoformat()})") from exc
        if index.notes:
            days_with_notes += 1
        for note in index.notes:
            if note.edition not in editions or (note.is_aviso and not include_avisos):
                continue
            notes_scanned += 1
            if all(f.matches_note(note) for f in filters):
                matches.append(note)
        await ctx.report_progress(progress=i, total=len(days), message=day.isoformat())
    return render_search(
        query=label,
        start=start,
        end=end,
        matches=matches,
        limit=limit,
        days_scanned=len(days),
        days_with_notes=days_with_notes,
        notes_scanned=notes_scanned,
    )


@mcp.tool(annotations=READ_ONLY)
async def get_indicators(
    date: Annotated[
        str,
        Field(
            description="DOF publication date. If nothing was published that day (weekend, "
            "holiday) the latest earlier publication is returned."
        ),
    ] = "today",
) -> str:
    """Get the financial indicators published in the DOF: FIX exchange rate, UDIS and TIIE."""
    try:
        day = parse_date(date)
        values = await get_client().latest_indicators(day)
    except (DateError, SidofError) as exc:
        raise ToolError(str(exc)) from exc
    return render_indicators(day, values)


@mcp.tool(annotations=READ_ONLY)
async def get_indicator_history(
    indicator: Annotated[
        IndicatorKey,
        Field(
            description="usd (FIX exchange rate), udis, tiie28, tiie91, tiie182, tiie_fondeo, "
            "cpp, ccp, ccp_udis or ccp_usd."
        ),
    ],
    date_from: Annotated[
        str | None, Field(description="Start date (inclusive). Defaults to 30 days before date_to.")
    ] = None,
    date_to: Annotated[
        str | None, Field(description="End date (inclusive). Defaults to today.")
    ] = None,
) -> str:
    """Get the published values of one indicator over a date range (up to 400 days)."""
    indicator_type = INDICATORS[indicator]
    try:
        start, end = parse_range(date_from, date_to, default_days=30, max_days=MAX_SERIES_DAYS)
        values = await get_client().indicator_series(indicator_type.code, start, end)
    except (DateError, SidofError) as exc:
        raise ToolError(str(exc)) from exc
    return render_series(indicator_type.name, indicator_type.unit, start, end, values)


# ------------------------------------------------------------------ resources


@mcp.resource(
    "dof://edition/{date}",
    mime_type="application/json",
    description="Normalized table of contents for one day (all editions) as JSON.",
)
async def edition_resource(date: str) -> str:
    index = await get_client().day_index(parse_date(date))
    return json.dumps(index.to_dict(), ensure_ascii=False, indent=2)


@mcp.resource(
    "dof://note/{code}",
    mime_type="text/markdown",
    description="Full text of a note as Markdown (not paginated).",
)
async def note_resource(code: str) -> str:
    note = await get_client().note(int(code))
    body = html_to_markdown(note.html) if note.html else ""
    return render_note(note, body, start=0, next_start=None, total_chars=len(body))


@mcp.resource(
    "dof://practice-areas",
    mime_type="application/json",
    description="Keyword presets accepted by search_notes(practice_area=...).",
)
def practice_areas_resource() -> str:
    data = [{"key": a.key, "name": a.name, "query": a.query} for a in PRACTICE_AREAS.values()]
    return json.dumps(data, ensure_ascii=False, indent=2)


# -------------------------------------------------------------------- prompts


@mcp.prompt
def regulatory_digest(
    practice_area: Annotated[
        str, Field(description="One of: " + ", ".join(sorted(PRACTICE_AREAS)))
    ] = "energia",
    date_from: Annotated[
        str, Field(description="Start date, YYYY-MM-DD. Empty: last 7 days.")
    ] = "",
    date_to: Annotated[str, Field(description="End date, YYYY-MM-DD. Empty: today.")] = "",
    language: Annotated[str, Field(description="Language of the digest, e.g. es or en.")] = "es",
) -> str:
    """Draft a regulatory digest of the DOF for a practice area and period."""
    area = PRACTICE_AREAS.get(practice_area)
    area_name = area.name if area else practice_area
    period = (
        f"from {date_from or '7 days ago'} to {date_to or 'today'}"
        if date_from or date_to
        else "for the last 7 days"
    )
    range_args = f'date_from="{date_from}", ' if date_from else "date_from=<7 days before today>, "
    range_args += f'date_to="{date_to}"' if date_to else "date_to=today"
    return f"""You are helping a Mexican lawyer review the Diario Oficial de la Federación (DOF).
Prepare a regulatory digest for the practice area "{area_name}" {period}.

Steps:
1. Call search_notes(practice_area="{practice_area}", {range_args}).
   If the area is not a preset, use relevant Spanish keywords in `query` instead.
2. Discard false positives (the presets match title keywords, so some hits will be unrelated).
3. For each relevant note, call get_note to read at least the first page and, for long
   instruments, the transitory articles (artículos transitorios) when they matter.
4. Write the digest in {language}:
   - Executive summary (3 to 5 bullets).
   - Table: date, issuer, instrument (linked to its official DOF URL), effect, who is affected.
   - Entry into force, deadlines and consultation periods you found, with the exact source text.
   - Suggested follow-ups for the legal team.
5. Cite every claim with the official link. Do not infer dates that the text does not state.
6. End with: "Unofficial digest based on SIDOF data. Only the printed/official DOF is
   authoritative. This is not legal advice; validate with the competent authority."
"""


# ----------------------------------------------------------------- entrypoint


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mcp-dof", description="MCP server for Mexico's Diario Oficial de la Federación."
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="stdio (default, for Claude Desktop/Code) or streamable HTTP.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for --transport http.")
    parser.add_argument("--port", type=int, default=8000, help="Port for --transport http.")
    parser.add_argument("--version", action="version", version=f"mcp-dof {__version__}")
    args = parser.parse_args(argv)
    if args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port, show_banner=False)
    else:
        mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
