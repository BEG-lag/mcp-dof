import pytest

from mcp_dof.search import (
    PRACTICE_AREAS,
    QueryError,
    fold,
    parse_query,
    practice_area_query,
)

ASEA = (
    "Acuerdo por el que se establecen acciones de simplificación para trámites que se realizan "
    "ante la Agencia Nacional de Seguridad Industrial y de Protección al Medio Ambiente del "
    "Sector Hidrocarburos"
)


def test_fold_removes_accents_and_case() -> None:
    assert fold("ENERGÍA Eléctrica") == "energia electrica"


def test_words_match_as_prefixes_without_accents() -> None:
    query = parse_query("electric energia")
    assert query.matches("Comisión Federal de Electricidad: tarifas de energía")
    assert not query.matches("Tarifas de energía")  # AND: both words required


def test_prefix_does_not_match_inside_words() -> None:
    assert not parse_query("trica").matches("energía eléctrica")


def test_alternatives_with_pipe_and_or() -> None:
    for raw in ("petróleo | hidrocarburos", "petróleo OR hidrocarburos"):
        assert parse_query(raw).matches(ASEA)


def test_quoted_phrases_keep_word_order() -> None:
    assert parse_query('"medio ambiente"').matches(ASEA)
    assert not parse_query('"ambiente medio"').matches(ASEA)


def test_acronyms_match_whole_words_only() -> None:
    query = parse_query("CFE")
    assert query.matches("Acuerdo de la CFE sobre tarifas")
    assert not query.matches("CFEXYZ")


@pytest.mark.parametrize("raw", ["", "   ", '""'])
def test_empty_queries_are_rejected(raw: str) -> None:
    with pytest.raises(QueryError):
        parse_query(raw)


def test_too_short_keywords_are_rejected() -> None:
    with pytest.raises(QueryError, match="at least 3"):
        parse_query("de la")


def test_practice_area_presets_parse_and_match() -> None:
    for key in PRACTICE_AREAS:
        assert practice_area_query(key).alternatives
    assert practice_area_query("hidrocarburos").matches(ASEA)
    assert practice_area_query("comercio-exterior").matches("Cuota compensatoria definitiva")


def test_unknown_practice_area_lists_options() -> None:
    with pytest.raises(QueryError, match="hidrocarburos"):
        practice_area_query("astrologia")
