"""Typed views over SIDOF JSON payloads.

SIDOF returns loosely typed JSON: flags are ``"S"``/``"N"`` strings, missing values
are sometimes the literal string ``"null"``, and every edition interleaves
untitled "separator" rows (one per issuing agency) with the real notes. The
parsers here normalize all of that once so the rest of the code can trust it.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any

from .dates import from_sidof

SIDOF_API = "https://sidof.segob.gob.mx/dof/sidof"
SIDOF_SITE = "https://sidof.segob.gob.mx"
DOF_SITE = "https://dof.gob.mx"


class Edition(StrEnum):
    """The three DOF editions that can appear on a given day."""

    MATUTINA = "matutina"
    VESPERTINA = "vespertina"
    EXTRAORDINARIA = "extraordinaria"

    @property
    def code(self) -> str:
        return {"matutina": "MAT", "vespertina": "VES", "extraordinaria": "EXT"}[self.value]

    @classmethod
    def from_code(cls, code: str) -> Edition:
        return {"MAT": cls.MATUTINA, "VES": cls.VESPERTINA, "EXT": cls.EXTRAORDINARIA}[code]


# Keys of the /notas/{fecha} payload, in publication order.
EDITION_KEYS: dict[str, Edition] = {
    "NotasMatutinas": Edition.MATUTINA,
    "NotasVespertinas": Edition.VESPERTINA,
    "NotasExtraordinarias": Edition.EXTRAORDINARIA,
}


def _clean(value: Any) -> Any:
    """Turn SIDOF's empty markers ("null", "", None) into ``None``."""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return None if stripped in {"", "null", "None"} else stripped
    return value


def _flag(value: Any) -> bool:
    return _clean(value) in {"S", "s", True, "1"}


def _int(value: Any) -> int | None:
    value = _clean(value)
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def official_url(code: int, day: date) -> str:
    """Link to the note on the official DOF website."""
    return f"{DOF_SITE}/nota_detalle.php?codigo={code}&fecha={day.strftime('%d/%m/%Y')}"


@dataclass(frozen=True, slots=True)
class NoteRef:
    """One entry of an edition's table of contents."""

    code: int
    title: str
    day: date
    edition: Edition
    section: str | None
    diario_id: int | None
    branch: str | None
    branch_code: str | None
    agency: str | None
    page: int | None
    order: float
    kind: str | None
    has_html: bool
    has_doc: bool
    has_pdf: bool

    @property
    def is_aviso(self) -> bool:
        """Judicial and general notices (edictos, convocatorias de asamblea, etc.)."""
        return self.kind == "AVISO" or self.branch_code == "AV"

    @property
    def issuer(self) -> str:
        """Human readable issuer: ``BRANCH › AGENCY`` or just the branch."""
        if self.agency and self.branch and self.agency != self.branch:
            return f"{self.branch} › {self.agency}"
        return self.agency or self.branch or "Sin dependencia"

    @property
    def official_url(self) -> str:
        return official_url(self.code, self.day)

    @property
    def sidof_url(self) -> str:
        return f"{SIDOF_SITE}/notas/{self.code}"

    @property
    def doc_url(self) -> str | None:
        return f"{SIDOF_API}/documentos/doc/{self.code}" if self.has_doc else None

    @property
    def edition_pdf_url(self) -> str | None:
        return f"{SIDOF_API}/documentos/pdf/{self.diario_id}" if self.diario_id else None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["day"] = self.day.isoformat()
        data["edition"] = self.edition.value
        data["is_aviso"] = self.is_aviso
        data["official_url"] = self.official_url
        return data


@dataclass(slots=True)
class DayIndex:
    """All the notes published on one day, across editions."""

    day: date
    notes: list[NoteRef] = field(default_factory=list)

    @property
    def editions(self) -> list[Edition]:
        return [e for e in Edition if any(n.edition is e for n in self.notes)]

    def by_edition(self, edition: Edition) -> list[NoteRef]:
        return [n for n in self.notes if n.edition is edition]

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.day.isoformat(),
            "editions": [e.value for e in self.editions],
            "total": len(self.notes),
            "notes": [n.to_dict() for n in self.notes],
        }


def parse_note_ref(raw: Mapping[str, Any], edition: Edition, day: date) -> NoteRef | None:
    """Parse one table-of-contents row; returns ``None`` for untitled separator rows."""
    title = _clean(raw.get("titulo"))
    code = _int(raw.get("codNota"))
    if not title or code is None:
        return None
    raw_day = _clean(raw.get("fecha"))
    return NoteRef(
        code=code,
        title=" ".join(title.split()),
        day=from_sidof(raw_day) if raw_day else day,
        edition=edition,
        section=_clean(raw.get("codSeccion")),
        diario_id=_int(raw.get("codDiario")),
        branch=_clean(raw.get("nombreCodOrgaUno")),
        branch_code=_clean(raw.get("codOrgaUno")),
        agency=_clean(raw.get("codOrgaDos")),
        page=_int(raw.get("pagina")),
        order=float(_clean(raw.get("orden")) or 0),
        kind=_clean(raw.get("tipoNota")),
        has_html=_flag(raw.get("existeHtml")),
        has_doc=_flag(raw.get("existeDoc")),
        has_pdf=_flag(raw.get("existePdf")),
    )


def parse_day(payload: Mapping[str, Any], day: date) -> DayIndex:
    """Parse the ``/notas/{DD-MM-YYYY}`` payload."""
    notes: list[NoteRef] = []
    for key, edition in EDITION_KEYS.items():
        rows: Iterable[Mapping[str, Any]] = payload.get(key) or []
        parsed = [ref for raw in rows if (ref := parse_note_ref(raw, edition, day))]
        notes.extend(sorted(parsed, key=lambda n: (n.order, n.code)))
    return DayIndex(day=day, notes=notes)


@dataclass(frozen=True, slots=True)
class NoteDetail:
    """A note with its full HTML body."""

    code: int
    title: str
    day: date
    edition: Edition | None
    branch: str | None
    agency: str | None
    page: int | None
    diario_id: int | None
    html: str | None
    has_doc: bool
    has_pdf: bool
    oversized: bool

    @property
    def issuer(self) -> str:
        if self.agency and self.branch and self.agency != self.branch:
            return f"{self.branch} › {self.agency}"
        return self.agency or self.branch or "Sin dependencia"

    @property
    def official_url(self) -> str:
        return official_url(self.code, self.day)

    @property
    def doc_url(self) -> str | None:
        return f"{SIDOF_API}/documentos/doc/{self.code}" if self.has_doc else None

    @property
    def edition_pdf_url(self) -> str | None:
        return f"{SIDOF_API}/documentos/pdf/{self.diario_id}" if self.diario_id else None


def parse_note_detail(payload: Mapping[str, Any]) -> NoteDetail | None:
    """Parse ``/notas/nota/{codNota}``; returns ``None`` when the note does not exist."""
    raw = payload.get("Nota")
    if not isinstance(raw, Mapping) or _int(raw.get("codNota")) is None:
        return None
    edition_code = _clean(raw.get("codEdicion"))
    raw_day = _clean(raw.get("fecha"))
    if not raw_day:
        return None
    return NoteDetail(
        code=int(raw["codNota"]),
        title=" ".join((_clean(raw.get("titulo")) or "(sin título)").split()),
        day=from_sidof(raw_day),
        edition=Edition.from_code(edition_code) if edition_code in {"MAT", "VES", "EXT"} else None,
        branch=_clean(raw.get("codOrgaUno")),
        agency=_clean(raw.get("codOrgaDos")),
        page=_int(raw.get("pagina")),
        diario_id=_int(raw.get("codDiario")),
        html=_clean(raw.get("cadenaContenido")),
        has_doc=_flag(raw.get("existeDoc")),
        has_pdf=_flag(raw.get("existePdf")),
        oversized=bool(payload.get("tamanioExcesivo")),
    )


@dataclass(frozen=True, slots=True)
class IndicatorType:
    """A financial indicator the DOF publishes (via Banco de México)."""

    key: str
    code: int
    name: str
    unit: str


INDICATORS: dict[str, IndicatorType] = {
    t.key: t
    for t in (
        IndicatorType("usd", 158, "Tipo de cambio FIX (dólar)", "MXN per USD"),
        IndicatorType("udis", 159, "UDIS", "MXN per UDI"),
        IndicatorType("tiie28", 165, "TIIE 28 días", "% annual"),
        IndicatorType("tiie91", 166, "TIIE 91 días", "% annual"),
        IndicatorType("tiie182", 174, "TIIE 182 días", "% annual"),
        IndicatorType("tiie_fondeo", 175, "TIIE de fondeo", "% annual"),
        IndicatorType("cpp", 162, "Costo porcentual promedio (CPP)", "% annual"),
        IndicatorType("ccp", 160, "Costo de captación a plazo (CCP)", "% annual"),
        IndicatorType("ccp_udis", 161, "CCP en UDIS", "% annual"),
        IndicatorType("ccp_usd", 163, "CCP en dólares", "% annual"),
    )
}
INDICATORS_BY_CODE: dict[int, IndicatorType] = {t.code: t for t in INDICATORS.values()}

# Published every business day (UDIS: every calendar day), in display order.
DAILY_INDICATORS: tuple[int, ...] = (158, 159, 165, 166, 174, 175)


@dataclass(frozen=True, slots=True)
class IndicatorValue:
    type: IndicatorType | None
    type_code: int
    day: date
    raw: str

    @property
    def value(self) -> float | None:
        try:
            return float(self.raw.replace("%", "").replace(",", "").strip())
        except ValueError:
            return None

    @property
    def name(self) -> str:
        return self.type.name if self.type else f"Indicador {self.type_code}"


def parse_indicators(payload: Mapping[str, Any]) -> list[IndicatorValue]:
    values: list[IndicatorValue] = []
    for raw in payload.get("ListaIndicadores") or []:
        code = _int(raw.get("codTipoIndicador"))
        raw_day = _clean(raw.get("fecha"))
        raw_value = _clean(raw.get("valor"))
        if code is None or not raw_day or raw_value is None:
            continue
        values.append(
            IndicatorValue(
                type=INDICATORS_BY_CODE.get(code),
                type_code=code,
                day=from_sidof(raw_day),
                raw=str(raw_value),
            )
        )
    return values
