# The SIDOF API, as observed

SIDOF (Sistema de Información del Diario Oficial de la Federación) is run by the
Secretaría de Gobernación. It exposes a public, unauthenticated JSON API that the DOF
website and mobile apps use. This page records what was verified by probing it on
**2026-11-17**. It is unofficial documentation: endpoints can change without notice.

The official reference documents are linked from <https://sidof.segob.gob.mx/datos_abiertos>
(PDF and sample JSON for "Diarios", "Documentos", "Indicadores" and "Notas"). They show
the host `sidofqa.segob.gob.mx` (a QA server); the production host below answers the
same paths.

## Basics

| Item | Value |
| --- | --- |
| Base URL | `https://sidof.segob.gob.mx/dof/sidof` |
| Auth | None |
| Format | JSON, UTF-8. Every body has `messageCode` and `response` (`"OK"` on success). |
| Dates in paths | `DD-MM-YYYY` (for example `13-11-2026`) |
| CORS | `Access-Control-Allow-Origin: *` on API responses |
| Typical latency | 70 to 250 ms for indexes and indicators; about 2 s for a very long note |

### Quirks worth knowing

* **`Accept: application/json` alone returns HTTP 406.** Send `*/*` or
  `application/json, */*;q=0.8`. (`curl` and browsers work because they send `*/*`.)
* An **invalid date** (`32-13-2026`) returns HTTP 500 with `"response": "INTERNAL_SERVER_ERROR"`.
  Validate dates client side.
* A **day without publication** (weekend, holiday) returns HTTP 200 with empty arrays.
* A **note code that does not exist** returns HTTP 200 with `"Nota": []`; a non numeric
  code returns HTTP 500 with `{}`.
* Missing values are often the **string** `"null"`, and booleans are `"S"`/`"N"`.
* Every edition's table of contents interleaves **untitled rows**: one per issuing agency,
  acting as a section header. They have no `titulo` and `existeDoc: "N"`. Skip them.
* `codOrgaUno` means different things in different endpoints: the branch **code**
  (`"PE"`) in `/notas/{fecha}` but the branch **name** (`"PODER EJECUTIVO"`) in
  `/notas/nota/{codNota}`.

## Notes (tables of contents and full text)

### `GET /notas/{DD-MM-YYYY}`: every note published on a date

```json
{
  "messageCode": 200,
  "response": "OK",
  "NotasMatutinas": [ ... ],
  "NotasVespertinas": [ ... ],
  "NotasExtraordinarias": [ ... ],
  "imagenesDiario": [{ "MAT": true }, { "VES": true }],
  "audioSumario": [{ "MAT": {} }, { "VES": {} }]
}
```

Each note:

| Field | Example | Meaning |
| --- | --- | --- |
| `codNota` | `5803757` | Unique note id. Used by every other endpoint. |
| `titulo` | `"Decreto por el que se expide la Ley de Ingresos..."` | Title. Absent on separator rows. |
| `fecha` | `"13-11-2026"` | Publication date. |
| `codDiario` | `330805` | Id of the edition (one per edition and section). |
| `codSeccion` | `"UNICA"` | Section (`PRIMERA`, `SEGUNDA`... on multi-section days). |
| `nombreCodOrgaUno` / `codOrgaUno` | `"PODER EJECUTIVO"` / `"PE"` | Branch: `PE`, `PJ`, `OA` (autonomous), `OD` (decentralized), `AV` (avisos), ... |
| `codOrgaDos` | `"PRESIDENCIA DE LA REPUBLICA"` | Issuing agency. `null` for avisos. |
| `pagina` / `paginaHasta` | `4` / `0` | Page in the printed edition. |
| `orden` | `2.0` | Order inside the edition. Sort by it; the array is not always sorted. |
| `tipoNota` | `"AVISO"` or `"null"` | `AVISO` marks avisos judiciales y generales. |
| `existeHtml`, `existeDoc`, `existePdf`, `existeImagen` | `"S"` | Availability flags. |
| `estado` | `2` | Publication status (meaning not documented). |

Avisos judiciales y generales (edictos, notices of shareholder meetings, etc.) are a large
share of each edition and their titles in this endpoint are only codes such as
`"Aviso REF:581596"`.

Coverage check: fetching every date from 2025-01-01 to 2026-11-17 (682 requests, done by the
companion project [dof-diario](https://github.com/BEG-lag/dof-diario)) found editions on 484
dates and 43,994 titled rows, 75.7% of them avisos. No row came under `NotasExtraordinarias` in
that period: editions published on weekends or holidays (for example 2025-02-02 and 2025-09-14)
are filed as vespertina or matutina.

### `GET /notas/nota/{codNota}`: one note with its full HTML

```json
{
  "messageCode": 200,
  "response": "OK",
  "Nota": {
    "codNota": 5803775,
    "titulo": "Tipo de cambio para solventar obligaciones...",
    "fecha": "13-11-2026",
    "codDiario": 330805,
    "codEdicion": "MAT",
    "cadenaContenido": "<!DOCTYPE HTML PUBLIC ...><HTML>...</HTML>",
    "codOrgaUno": "ORGANISMOS AUTONOMOS",
    "codOrgaDos": "BANCO DE MEXICO",
    "pagina": 178,
    "existeDoc": "S",
    "existePdf": "S",
    "tamanioContenido": 0
  },
  "tamanioExcesivo": false
}
```

`cadenaContenido` is a complete HTML 4 document exported from a publishing tool: every
run of text is a `<span>` with inline styles, emphasis is `font-weight:bold` in a
`style` attribute, and tables are real `<table>` elements. The Ley de Ingresos 2027
(note 5803757) is about 760,000 characters of HTML, roughly 218,000 characters once
converted to Markdown.

### `GET /notas/obtenerNotasPorDiario/{codDiario}`: notes of one edition

Same notes as above for a single `codDiario`, with more (mostly `null`) fields and the
branch name in `codOrgaUno`.

## Editions and documents

| Endpoint | Returns |
| --- | --- |
| `GET /diarios/porFecha/{DD-MM-YYYY}` | `Matutina`, `Vespertina`, `Extraordinaria` lists with `codDiario`, `codSeccion`, `paginaIni`, `paginaMax` (page count). |
| `GET /diarios/obtieneDiario/{DD-MM-YYYY}/{MAT\|VES\|EXT}` | `{"diario": {"codDiario", "codEdicion", "fecha", "estado"}}` |
| `GET /diarios/{YYYY}` | `ListaDiarios`. In practice it only lists **vespertina** editions (100 for 2025), apparently to drive the calendar. |
| `GET /documentos/pdf/{codDiario}` | The full edition as PDF (`application/pdf`, 2.5 MB for a 16 page vespertina). Range requests are ignored. |
| `GET /documentos/doc/{codNota}` | The note as Word (`application/msword`, served as `.docx`). |

Public pages:

* Official note page: `https://dof.gob.mx/nota_detalle.php?codigo={codNota}&fecha={DD/MM/YYYY}`
  (use the bare domain: `www.dof.gob.mx` served a certificate for another host during testing).
* SIDOF note page: `https://sidof.segob.gob.mx/notas/{codNota}`

## Indicators

| Endpoint | Returns |
| --- | --- |
| `GET /indicadores/` | Today's values. |
| `GET /indicadores/{DD-MM-YYYY}` | Values published that day. |
| `GET /indicadores/{codTipoIndicador}/{DD-MM-YYYY}/{DD-MM-YYYY}` | One indicator over a range, plus `TotalIndicadores`. |

```json
{"codIndicador": 40075, "codTipoIndicador": 158, "fecha": "13-11-2026", "valor": "18.6188"}
```

`valor` is a string; rates carry a `%` suffix. Type codes seen in the SIDOF widget:

| Code | Indicator | Code | Indicator |
| --- | --- | --- | --- |
| 158 | DÓLAR (FIX exchange rate) | 165 | TIIE 28 días |
| 159 | UDIS | 166 | TIIE 91 días |
| 160 | CCP | 174 | TIIE 182 días |
| 161 | CCP-UDIS | 175 | TIIE de fondeo |
| 162 | CPP | 176 to 182 | TIIE 26, 27, 29, 89, 90, 92 and 181 días (historical) |
| 163 | CCP-DÓLARES | | |

Dates are **DOF publication dates**. The FIX published on 2026-11-13 (18.6188) is the
rate Banco de México determined on 2026-11-12, as the note itself says. UDIS are published
for every calendar day; the FIX and the TIIE only on business days, so a weekend date
returns only UDIS.

## Search

The website's advanced search posts to `/busqueda/CargaNotasAvanzadas/`, which forwards a
JSON body to an internal backend (`/dof/sidof/buscarNotas/avanzadaFrontend`). The public
path exists, but every query tried on 2026-11-17 (title and content search, 2024 and 2026
ranges, common words such as "decreto") returned **HTTP 204 No Content**, and the website
wrapper returned `"totalRegistros": 0`.

The legacy site still searches titles: `POST https://dof.gob.mx/busqueda_detalle.php` with
`textobusqueda=<term>` returns an HTML page (320 results for "hidrocarburos", 10 per page).
It is HTML only, so mcp-dof does not depend on it. Instead, `search_notes` scans the daily
`/notas/{fecha}` indexes in a date range and matches titles locally, with caching.

## Being polite

These are government servers with no published rate limit. mcp-dof sends a descriptive
`User-Agent` (`mcp-dof/<version> (+https://github.com/BEG-lag/mcp-dof)`), waits at least
250 ms between requests, retries 429 and 5xx with exponential backoff (honouring
`Retry-After`), uses a 20 s timeout, and caches responses (past editions for 12 hours).
