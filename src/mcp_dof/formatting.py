"""Markdown renderers for tool results.

Tool results are read by language models first and humans second, so they are
compact Markdown with stable identifiers (note codes) and absolute links.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date
from itertools import groupby

from .models import DayIndex, Edition, IndicatorValue, NoteDetail, NoteRef

DISCLAIMER = (
    "_Unofficial data from the public SIDOF API. Only the printed/official DOF is "
    "authoritative. Not legal advice._"
)

_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def weekday(day: date) -> str:
    return _WEEKDAYS[day.weekday()]


def _note_line(note: NoteRef) -> str:
    page = f" · p. {note.page}" if note.page else ""
    return f"- `{note.code}` {note.title}{page} · [DOF]({note.official_url})"


def render_edition(
    index: DayIndex,
    *,
    editions: Sequence[Edition],
    include_avisos: bool,
    latest_day: date | None = None,
) -> str:
    day = index.day
    header = f"# DOF {day.isoformat()} · {weekday(day)}"
    selected = [n for n in index.notes if n.edition in editions]

    if not selected:
        lines = [header, ""]
        what = (
            "No DOF edition"
            if len(editions) == len(Edition)
            else "No " + "/".join(e.value for e in editions) + " edition"
        )
        lines.append(f"{what} was published on {day.isoformat()} ({weekday(day)}).")
        if index.notes:
            lines.append(
                "Editions available that day: " + ", ".join(e.value for e in index.editions) + "."
            )
        else:
            lines.append("The DOF does not publish on weekends and most official holidays.")
        if latest_day and latest_day != day:
            lines.append(
                f"The most recent earlier edition is from {latest_day.isoformat()} "
                f"({weekday(latest_day)}); call list_edition with that date."
            )
        return "\n".join(lines) + "\n"

    avisos = [n for n in selected if n.is_aviso]
    shown = selected if include_avisos else [n for n in selected if not n.is_aviso]
    present = [e for e in Edition if e in editions and any(n.edition is e for n in selected)]

    lines = [
        header,
        "",
        f"{len(selected)} notes in {len(present)} edition(s): "
        + ", ".join(e.value for e in present)
        + ".",
    ]
    if avisos and not include_avisos:
        lines.append(
            f"{len(avisos)} avisos judiciales y generales hidden "
            "(pass include_avisos=true to list them)."
        )
    for edition in present:
        notes = [n for n in shown if n.edition is edition]
        total = sum(1 for n in selected if n.edition is edition)
        pdf = next((n.edition_pdf_url for n in notes if n.edition_pdf_url), None)
        if pdf is None:
            pdf = next((n.edition_pdf_url for n in selected if n.edition is edition), None)
        pdf_link = f" · [edition PDF]({pdf})" if pdf else ""
        hidden = total - len(notes)
        hidden_note = f" ({hidden} avisos hidden)" if hidden else ""
        lines += ["", f"## Edición {edition.value} · {total} notes{hidden_note}{pdf_link}"]
        for issuer, group in groupby(notes, key=lambda n: n.issuer):
            lines += ["", f"**{issuer}**"]
            lines += [_note_line(n) for n in group]
    lines += ["", DISCLAIMER]
    return "\n".join(lines) + "\n"


def render_note(
    note: NoteDetail,
    body: str,
    *,
    start: int,
    next_start: int | None,
    total_chars: int,
) -> str:
    edition = f" ({note.edition.value})" if note.edition else ""
    rows = [
        ("Code", f"`{note.code}`"),
        ("Published", f"{note.day.isoformat()}{edition}"),
        ("Issuer", note.issuer),
        ("Page", str(note.page) if note.page else "n/a"),
        ("Official page", note.official_url),
    ]
    if note.doc_url:
        rows.append(("Word file", note.doc_url))
    if note.edition_pdf_url:
        rows.append(("Edition PDF", note.edition_pdf_url))
    lines = [f"# {note.title}", "", "| Field | Value |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in rows]
    lines += ["", "---", ""]
    if body:
        lines.append(body.rstrip())
    else:
        lines.append(
            "_SIDOF has no HTML text for this note. Use the Word file or the edition PDF "
            "linked above._"
        )
    lines += ["", "---", ""]
    if body:
        end = next_start if next_start is not None else total_chars
        position = f"Characters {start:,} to {end:,} of {total_chars:,}."
        if next_start is not None:
            position += (
                f" More text available: call get_note(code={note.code}, start={next_start})."
            )
        else:
            position += " End of note."
        lines += [f"_{position}_", ""]
    lines.append(DISCLAIMER)
    return "\n".join(lines) + "\n"


def render_search(
    *,
    query: str,
    start: date,
    end: date,
    matches: Sequence[NoteRef],
    limit: int,
    days_scanned: int,
    days_with_notes: int,
    notes_scanned: int,
) -> str:
    lines = [
        f"# DOF search: {query}",
        "",
        f"Range {start.isoformat()} to {end.isoformat()}: scanned {days_scanned} days "
        f"({days_with_notes} with publications, {notes_scanned:,} notes). "
        f"Found {len(matches)} matching notes"
        + (f"; showing the newest {limit}." if len(matches) > limit else "."),
    ]
    if not matches:
        lines += [
            "",
            "No titles matched. Try a shorter stem (e.g. `eléctric`), alternatives with `|`, "
            "or a wider date range.",
        ]
    for note in matches[:limit]:
        lines += [
            "",
            f"- **{note.day.isoformat()}** · {note.edition.value} · {note.issuer}",
            f"  {note.title} · `{note.code}` · [DOF]({note.official_url})",
        ]
    lines += ["", DISCLAIMER]
    return "\n".join(lines) + "\n"


def render_indicators(requested: date, values: Iterable[IndicatorValue]) -> str:
    values = list(values)
    header = f"# DOF financial indicators · {requested.isoformat()} ({weekday(requested)})"
    if not values:
        return f"{header}\n\nNo indicators were published on that date or the 10 days before it.\n"
    lines = [header, ""]
    if any(v.day != requested for v in values):
        lines += [
            "_Indicators not published on the requested date are shown with their latest "
            "earlier publication date._",
            "",
        ]
    lines += ["| Indicator | Value | Unit | Published | Key |", "| --- | --- | --- | --- | --- |"]
    for value in values:
        unit = value.type.unit if value.type else ""
        key = f"`{value.type.key}`" if value.type else str(value.type_code)
        lines.append(f"| {value.name} | {value.raw} | {unit} | {value.day.isoformat()} | {key} |")
    lines += [
        "",
        "Dates are DOF publication dates. Banco de México determines the FIX exchange rate "
        "and the TIIE on the previous business day.",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines) + "\n"


def render_series(
    name: str, unit: str, start: date, end: date, values: Sequence[IndicatorValue]
) -> str:
    lines = [f"# {name} · {start.isoformat()} to {end.isoformat()}", ""]
    numeric = [(v, v.value) for v in values if v.value is not None]
    if not numeric:
        return "\n".join([*lines, "No values were published in that range.", ""])
    first, last = numeric[0], numeric[-1]
    low = min(numeric, key=lambda p: p[1])
    high = max(numeric, key=lambda p: p[1])
    change = last[1] - first[1]
    pct = f" ({change / first[1] * 100:+.2f}%)" if first[1] else ""
    lines += [
        f"{len(values)} published values ({unit}). First {first[0].raw} on "
        f"{first[0].day.isoformat()}, last {last[0].raw} on {last[0].day.isoformat()}, "
        f"change {change:+.4f}{pct}. Low {low[0].raw} on {low[0].day.isoformat()}, "
        f"high {high[0].raw} on {high[0].day.isoformat()}.",
        "",
        "| Date | Value |",
        "| --- | --- |",
    ]
    lines += [f"| {v.day.isoformat()} | {v.raw} |" for v in values]
    lines += ["", DISCLAIMER]
    return "\n".join(lines) + "\n"
