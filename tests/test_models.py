from datetime import date

from conftest import load_fixture
from mcp_dof.models import (
    Edition,
    parse_day,
    parse_indicators,
    parse_note_detail,
)

DAY = date(2026, 11, 13)


def test_parse_day_skips_untitled_separator_rows() -> None:
    payload = load_fixture("notas/13-11-2026")
    raw_rows = sum(len(payload[k]) for k in ("NotasMatutinas", "NotasVespertinas"))
    index = parse_day(payload, DAY)
    assert raw_rows == 77
    assert len(index.notes) == 66
    assert all(note.title for note in index.notes)


def test_parse_day_groups_editions_in_publication_order() -> None:
    index = parse_day(load_fixture("notas/13-11-2026"), DAY)
    assert index.editions == [Edition.MATUTINA, Edition.VESPERTINA]
    matutina = index.by_edition(Edition.MATUTINA)
    assert matutina[0].code == 5803757
    assert [n.order for n in matutina] == sorted(n.order for n in matutina)


def test_note_ref_fields_and_links() -> None:
    index = parse_day(load_fixture("notas/13-11-2026"), DAY)
    note = next(n for n in index.notes if n.code == 5803775)
    assert note.issuer == "ORGANISMOS AUTONOMOS › BANCO DE MEXICO"
    assert note.page == 178
    assert note.has_doc
    assert note.has_pdf
    assert note.official_url == (
        "https://dof.gob.mx/nota_detalle.php?codigo=5803775&fecha=13/11/2026"
    )
    assert note.edition_pdf_url
    assert note.edition_pdf_url.endswith("/documentos/pdf/330805")


def test_avisos_are_flagged() -> None:
    index = parse_day(load_fixture("notas/13-11-2026"), DAY)
    avisos = [n for n in index.notes if n.is_aviso]
    assert len(avisos) == 44
    assert all(n.issuer == "AVISOS JUDICIALES Y GENERALES" for n in avisos)


def test_empty_day_parses_to_no_notes() -> None:
    index = parse_day(load_fixture("notas/16-11-2026"), date(2026, 11, 16))
    assert index.notes == []
    assert index.editions == []


def test_parse_note_detail() -> None:
    note = parse_note_detail(load_fixture("notas/nota/5803775"))
    assert note is not None
    assert note.edition is Edition.MATUTINA
    assert note.branch == "ORGANISMOS AUTONOMOS"
    assert note.html
    assert "18.6188" in note.html


def test_parse_note_detail_missing_note() -> None:
    assert parse_note_detail(load_fixture("notas/nota/9999999")) is None
    assert parse_note_detail({}) is None


def test_parse_indicators() -> None:
    values = parse_indicators(load_fixture("indicadores/13-11-2026"))
    by_key = {v.type.key: v for v in values if v.type}
    assert by_key["usd"].value == 18.6188
    assert by_key["tiie28"].raw == "6.5147%"
    assert by_key["tiie28"].value == 6.5147
    assert by_key["udis"].day == DAY
