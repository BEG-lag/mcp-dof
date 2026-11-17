"""Keyword matching over DOF titles and practice-area presets.

SIDOF does not expose a working full-text search endpoint (see docs/api.md), so
``search_notes`` scans the daily tables of contents in a date range and matches
titles locally. Matching is designed for Spanish legal text:

* case and accent insensitive (``energia`` matches ``Energía``);
* words match at the start of a word, so ``eléctric`` finds ``eléctrica`` and
  ``eléctrico``;
* short all-caps acronyms (``CFE``, ``ISR``) must match a whole word;
* ``"exact phrase"`` keeps words together;
* ``|`` or `` OR `` separates alternatives; inside an alternative every term
  must match (AND).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .models import NoteRef

_PHRASE_OR_WORD = re.compile(r'"([^"]+)"|(\S+)')
_OR_SPLIT = re.compile(r"\s*\|\s*|\s+OR\s+")


def fold(text: str) -> str:
    """Casefold and strip diacritics so that ``Energía`` and ``energia`` compare equal."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


@dataclass(frozen=True)
class Term:
    text: str
    whole_word: bool

    @property
    def pattern(self) -> re.Pattern[str]:
        escaped = r"\s+".join(re.escape(part) for part in self.text.split())
        suffix = r"\b" if self.whole_word else ""
        return re.compile(rf"(?<![\w]){escaped}{suffix}")


@dataclass(frozen=True)
class Query:
    """A parsed query: OR of alternatives, each an AND of terms."""

    alternatives: tuple[tuple[Term, ...], ...]
    source: str

    def matches(self, text: str) -> bool:
        folded = fold(text)
        return any(
            all(term.pattern.search(folded) for term in alternative)
            for alternative in self.alternatives
        )

    def matches_note(self, note: NoteRef) -> bool:
        haystack = " ".join(filter(None, [note.title, note.agency, note.branch]))
        return self.matches(haystack)


class QueryError(ValueError):
    pass


def parse_query(raw: str) -> Query:
    raw = (raw or "").strip()
    if not raw:
        raise QueryError("The search query is empty. Pass one or more keywords.")
    alternatives: list[tuple[Term, ...]] = []
    for chunk in _OR_SPLIT.split(raw):
        terms: list[Term] = []
        for phrase, word in _PHRASE_OR_WORD.findall(chunk):
            token = (phrase or word).strip()
            if not token:
                continue
            is_acronym = token.isupper() and token.isalnum() and len(token) <= 6
            terms.append(Term(text=fold(token), whole_word=is_acronym))
        if terms:
            alternatives.append(tuple(terms))
    if not alternatives:
        raise QueryError(f"Could not find any keyword in {raw!r}.")
    if all(len(t.text) < 3 and not t.whole_word for alt in alternatives for t in alt):
        raise QueryError("Keywords need at least 3 characters (or be an acronym like CFE).")
    return Query(alternatives=tuple(alternatives), source=raw)


@dataclass(frozen=True)
class PracticeArea:
    key: str
    name: str
    query: str


PRACTICE_AREAS: dict[str, PracticeArea] = {
    area.key: area
    for area in (
        PracticeArea(
            "energia",
            "Energía y electricidad",
            "energía | eléctric | electricidad | CFE | CENACE | CNE | SENER | renovable"
            ' | "transición energética"',
        ),
        PracticeArea(
            "hidrocarburos",
            "Hidrocarburos",
            "hidrocarburo | petróle | petrolífero | gas natural | gas licuado | PEMEX"
            " | ASEA | gasolina | diésel | combustible | gasoducto",
        ),
        PracticeArea(
            "mineria",
            "Minería",
            'miner | litio | "Servicio Geológico Mexicano" | metalúrgic | concesiones mineras',
        ),
        PracticeArea(
            "fiscal",
            "Fiscal",
            "fiscal | impuesto | tributari | ISR | IVA | IEPS | SAT | miscelánea | estímulo"
            " | contribuyente | aduan",
        ),
        PracticeArea(
            "ambiental",
            "Ambiental",
            "ambiental | SEMARNAT | PROFEPA | ecológic | áreas naturales | residuos"
            ' | emisiones | "cambio climático" | "aguas nacionales" | hídric | CONAGUA',
        ),
        PracticeArea(
            "competencia",
            "Competencia económica",
            '"competencia económica" | antimonopolio | concentración | prácticas monopólicas',
        ),
        PracticeArea(
            "financiero",
            "Financiero",
            '"Banco de México" | CNBV | "instituciones de crédito" | seguros | fianzas'
            " | CONDUSEF | valores | fintech | financier",
        ),
        PracticeArea(
            "comercio_exterior",
            "Comercio exterior",
            'arancel | "comercio exterior" | antidumping | "cuota compensatoria" | cupo'
            ' | importación | exportación | "Impuestos Generales de Importación"',
        ),
        PracticeArea(
            "laboral",
            "Laboral y seguridad social",
            'laboral | trabajo | "salario mínimo" | IMSS | "Seguro Social" | INFONAVIT'
            " | pensiones | sindica",
        ),
        PracticeArea(
            "datos_personales",
            "Datos personales y transparencia",
            '"datos personales" | transparencia | "acceso a la información" | privacidad',
        ),
        PracticeArea(
            "normas",
            "Normas Oficiales Mexicanas",
            'NOM | "norma oficial mexicana" | "proyecto de norma" | NMX',
        ),
        PracticeArea(
            "telecom",
            "Telecomunicaciones",
            'telecomunicaciones | radiodifusión | espectro | "Agencia de Transformación Digital"'
            " | satelital",
        ),
    )
}


def practice_area_query(key: str) -> Query:
    normalized = fold(key).replace("-", "_").replace(" ", "_")
    area = PRACTICE_AREAS.get(normalized)
    if area is None:
        options = ", ".join(sorted(PRACTICE_AREAS))
        raise QueryError(f"Unknown practice_area {key!r}. Options: {options}.")
    return parse_query(area.query)
