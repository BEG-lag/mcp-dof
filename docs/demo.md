# Demo transcript

Recorded on 2026-11-17 with `uv run python scripts/demo.py --write`: a real MCP client talking to `mcp-dof` over stdio, which queries the live SIDOF API. Nothing below was edited. Timings include network latency and a cold cache.

## tools/list

`list_edition`, `get_note`, `search_notes`, `get_indicators`, `get_indicator_history`

## list_edition

`{"date": "2026-11-13"}` · 0.4 s · ok

````markdown
# DOF 2026-11-13 · Friday

66 notes in 2 edition(s): matutina, vespertina.
44 avisos judiciales y generales hidden (pass include_avisos=true to list them).

## Edición matutina · 61 notes (44 avisos hidden) · [edition PDF](https://sidof.segob.gob.mx/dof/sidof/documentos/pdf/330805)

**PODER EJECUTIVO › PRESIDENCIA DE LA REPUBLICA**
- `5803757` Decreto por el que se expide la Ley de Ingresos de la Federación para el Ejercicio Fiscal de 2027. · p. 4 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803757&fecha=13/11/2026)
- `5803758` Decreto por el que se reforman, adicionan y derogan diversas disposiciones de la Ley del Impuesto sobre la Renta y se expiden disposiciones de vigencia transitoria. · p. 52 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803758&fecha=13/11/2026)
- `5803759` Decreto por el que se reforman, adicionan y derogan diversas disposiciones de la Ley Federal de Derechos. · p. 88 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803759&fecha=13/11/2026)
- `5803760` Decreto por el que se declara de utilidad pública y se ordena la ocupación temporal de 8,072.018 m² (ocho mil setenta y dos punto cero dieciocho metros cuadrados), correspondientes a 16 (dieciséis) inmuebles de propiedad privada, en el municipio de Cortazar, estado de Guanajuato (Segunda publicación). · p. 110 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803760&fecha=13/11/2026)
- `5803761` Decreto por el que se declara de utilidad pública y se ordena la ocupación temporal de 8,324.038 m² (ocho mil trescientos veinticuatro punto cero treinta y ocho metros cuadrados), correspondientes a 3 (tres) inmuebles de propiedad privada, en el municipio de Mineral de la Reforma, en el estado de Hidalgo (Segunda publicación). · p. 114 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803761&fecha=13/11/2026)

**PODER EJECUTIVO › SECRETARIA DE BIENESTAR**
- `5803763` Programa Institucional del Instituto Nacional de las Personas Adultas Mayores 2026-2030. · p. 117 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803763&fecha=13/11/2026)

**PODER EJECUTIVO › SECRETARIA DE INFRAESTRUCTURA, COMUNICACIONES Y TRANSPORTES**
- `5803765` Acuerdo por el que se implementa la jornada de facilidades denominada Mes del Apto Médico conforme a las condiciones que se indican. · p. 136 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803765&fecha=13/11/2026)

**PODER EJECUTIVO › SECRETARIA DE SALUD**
- `5803767` Acuerdo por el que se establece el Comité Nacional por la Calidad en Salud (CONCALIDAD). · p. 142 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803767&fecha=13/11/2026)

**ORGANISMOS DESCONCENTRADOS O DESCENTRALIZADOS › INSTITUTO MEXICANO DEL SEGURO SOCIAL**
- `5803769` Aviso mediante el cual se designa al Titular de la Jefatura de Servicios Jurídicos, Licenciado Yan Jorge Vargas Serrano, para que supla las ausencias del Doctor Julio Mercado Castruita, Titular del Órgano de Operación Administrativa Desconcentrada Estatal Chihuahua del Instituto Mexicano del Seguro Social, autorizándole a firmar y despachar la documentación incluyendo la suscripción de las resoluciones que debe emitir este Órgano. · p. 147 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803769&fecha=13/11/2026)

**PODER JUDICIAL › SUPREMA CORTE DE JUSTICIA DE LA NACION**
- `5803771` Sentencia dictada por el Tribunal Pleno de la Suprema Corte de Justicia de la Nación en la Controversia Constitucional 92/2026, así como el Voto Concurrente de la señora Ministra Lenia Batres Guadarrama. · p. 148 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803771&fecha=13/11/2026)

**PODER JUDICIAL › ORGANO DE ADMINISTRACION JUDICIAL**
- `5803773` Acuerdo General del Pleno del Órgano de Administración Judicial que reforma el similar por el que se designan a las personas titulares de diversos órganos auxiliares. · p. 176 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803773&fecha=13/11/2026)

**ORGANISMOS AUTONOMOS › BANCO DE MEXICO**
- `5803775` Tipo de cambio para solventar obligaciones denominadas en moneda extranjera pagaderas en la República Mexicana. · p. 178 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803775&fecha=13/11/2026)
- `5803776` Tasas de interés interbancarias de equilibrio. · p. 178 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803776&fecha=13/11/2026)
- `5803777` Tasa de interés interbancaria de equilibrio de fondeo a un día hábil bancario. · p. 178 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803777&fecha=13/11/2026)
- `5803778` Circular 13/2026 dirigida a las instituciones de crédito, relativa a las Modificaciones a la Circular 3/2025 (Seguridad Informática). · p. 179 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803778&fecha=13/11/2026)
- `5803779` Circular 14/2026 dirigida a las instituciones de crédito, sociedades financieras de objeto múltiple reguladas y no reguladas, sociedades financieras populares, sociedades financieras comunitarias, sociedades cooperativas de ahorro y préstamo, uniones de crédito, entidades financieras que actúen como fiduciarias en fideicomisos que otorguen crédito al público, instituciones de financiamiento colectivo de deuda, así como sociedades que, de manera habitual, otorguen créditos, préstamos o financiamientos al público, relativa a las Modificaciones a la Circular 21/2009 (Costo Anual Total -CAT-). · p. 187 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803779&fecha=13/11/2026)

**ORGANISMOS AUTONOMOS › INSTITUTO NACIONAL ELECTORAL**
- `5803781` Acuerdo del Consejo General del Instituto Nacional Electoral por el que se determinan los Lineamientos para la contabilidad, rendición de cuentas y fiscalización, así como los gastos que se consideran como de precampaña y apoyo de la ciudadanía, correspondientes a los Procesos Electorales Federal y Locales Concurrentes 2026-2027, así como de los Procesos Electorales Extraordinarios que se pudieran derivar de éstos. · p. 195 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803781&fecha=13/11/2026)

## Edición vespertina · 5 notes · [edition PDF](https://sidof.segob.gob.mx/dof/sidof/documentos/pdf/330825)

**PODER EJECUTIVO › PRESIDENCIA DE LA REPUBLICA**
- `5803837` Decreto por el que se reforman, adicionan y derogan diversas disposiciones del Código Penal Federal y de la Ley Federal de Protección a la Propiedad Industrial. · p. 3 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803837&fecha=13/11/2026)
- `5803838` Decreto por el que se adicionan las fracciones X Bis y X Ter al artículo 58 de la Ley General de Turismo. · p. 9 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803838&fecha=13/11/2026)

**PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO**
- `5803840` Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · p. 10 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803840&fecha=13/11/2026)
- `5803841` Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · p. 11 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803841&fecha=13/11/2026)
- `5803842` Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · p. 14 · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803842&fecha=13/11/2026)

_Unofficial data from the public SIDOF API. Only the printed/official DOF is authoritative. Not legal advice._
````

## search_notes

`{"practice_area": "hidrocarburos", "date_from": "2026-10-01", "date_to": "2026-11-13"}` · 10.7 s · ok

````markdown
# DOF search: practice area `hidrocarburos`

Range 2026-10-01 to 2026-11-13: scanned 44 days (32 with publications, 535 notes). Found 32 matching notes.

- **2026-11-13** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · `5803840` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803840&fecha=13/11/2026)

- **2026-11-13** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · `5803841` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803841&fecha=13/11/2026)

- **2026-11-13** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · `5803842` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803842&fecha=13/11/2026)

- **2026-11-06** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · `5803257` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803257&fecha=06/11/2026)

- **2026-11-06** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · `5803258` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803258&fecha=06/11/2026)

- **2026-11-06** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · `5803259` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803259&fecha=06/11/2026)

- **2026-11-05** · matutina · PODER EJECUTIVO › SECRETARIA DE ENERGIA
  Acuerdo de la Comisión Nacional de Energía por el que se expiden las Disposiciones Administrativas de Carácter General que regulan la actividad de comercialización de gas natural, petrolíferos, gas licuado de petróleo y petroquímicos. · `5803022` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5803022&fecha=05/11/2026)

- **2026-11-02** · matutina · PODER EJECUTIVO › SECRETARIA DE MEDIO AMBIENTE Y RECURSOS NATURALES
  Acuerdo por el que se establecen acciones de simplificación para trámites que se realizan ante la Agencia Nacional de Seguridad Industrial y de Protección al Medio Ambiente del Sector Hidrocarburos, así como se expiden y modifican los formatos que se mencionan. · `5802719` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802719&fecha=02/11/2026)

- **2026-10-30** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · `5802697` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802697&fecha=30/10/2026)

- **2026-10-30** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · `5802698` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802698&fecha=30/10/2026)

- **2026-10-30** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · `5802699` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802699&fecha=30/10/2026)

- **2026-10-29** · matutina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los estímulos fiscales a la gasolina y al diésel en los sectores pesquero y agropecuario para el mes de noviembre de 2026. · `5802460` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802460&fecha=29/10/2026)

- **2026-10-28** · matutina · PODER EJECUTIVO › SECRETARIA DE ENERGIA
  Acuerdo por el que la Secretaría de Energía emite los Lineamientos para la aprobación, actualización y vigilancia de los Organismos de Evaluación de la Conformidad que evalúan la conformidad de las Normas Oficiales Mexicanas que regulan las especificaciones de calidad de los Hidrocarburos, Petrolíferos y Petroquímicos y del registro de los laboratorios extranjeros que emitan documentos equivalentes a las Normas Oficiales Mexicanas que regulan las especificaciones de calidad. · `5802362` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802362&fecha=28/10/2026)

- **2026-10-27** · matutina · PODER EJECUTIVO › SECRETARIA DE MEDIO AMBIENTE Y RECURSOS NATURALES
  Acuerdo por el que se delega en las Direcciones de Área, adscritas a las Direcciones Generales de la Unidad de Gestión Industrial y de la Unidad de Supervisión, Inspección y Vigilancia Industrial, de la Agencia Nacional de Seguridad Industrial y de Protección al Medio Ambiente del Sector Hidrocarburos, el ejercicio de las facultades que se indican. · `5802182` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802182&fecha=27/10/2026)

- **2026-10-27** · matutina · PODER EJECUTIVO › SECRETARIA DE ENERGIA
  Acuerdo de la Comisión Nacional de Energía por el que se inicia el procedimiento administrativo de caducidad a los titulares de ciento treinta y dos permisos de comercialización de hidrocarburos, petrolíferos y petroquímicos, por presuntamente ubicarse en la hipótesis de caducidad prevista en el artículo 88, fracción I, inciso b, de la Ley del Sector Hidrocarburos. · `5802184` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802184&fecha=27/10/2026)

- **2026-10-23** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · `5802082` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802082&fecha=23/10/2026)

- **2026-10-23** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · `5802083` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802083&fecha=23/10/2026)

- **2026-10-23** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · `5802084` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5802084&fecha=23/10/2026)

- **2026-10-20** · matutina · PODER EJECUTIVO › SECRETARIA DE MEDIO AMBIENTE Y RECURSOS NATURALES
  Acuerdo por el cual se abroga el diverso mediante el cual se delegan a la Dirección General de Gestión de Operación Integral de la Agencia Nacional de Seguridad Industrial y de Protección al Medio Ambiente del Sector Hidrocarburos, las facultades que se indican, publicado en el Diario Oficial de la Federación el 24 de diciembre de 2025. · `5801542` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5801542&fecha=20/10/2026)

- **2026-10-16** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · `5801457` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5801457&fecha=16/10/2026)

- **2026-10-16** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · `5801458` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5801458&fecha=16/10/2026)

- **2026-10-16** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · `5801459` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5801459&fecha=16/10/2026)

- **2026-10-14** · matutina · PODER EJECUTIVO › SECRETARIA DE ENERGIA
  Acuerdo de la Comisión Nacional de Energía por el que se emiten las Disposiciones Administrativas de Carácter General por las que se establecen los criterios para la determinación de las vigencias de los títulos de permisos previstos en el artículo 11 del Reglamento de las actividades a que se refiere el Título Tercero de la Ley de Hidrocarburos. · `5801164` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5801164&fecha=14/10/2026)

- **2026-10-14** · matutina · EMPRESAS PUBLICAS DEL ESTADO MEXICANO › PETROLEOS MEXICANOS
  Acuerdo por el que se establecen acciones de simplificación al registro de proveedores de Petróleos Mexicanos a través de la Herramienta Integral de Información de Proveedores (HIIP). · `5801172` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5801172&fecha=14/10/2026)

- **2026-10-09** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · `5800917` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800917&fecha=09/10/2026)

- **2026-10-09** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · `5800918` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800918&fecha=09/10/2026)

- **2026-10-09** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · `5800919` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800919&fecha=09/10/2026)

- **2026-10-05** · matutina · PODER EJECUTIVO › SECRETARIA DE MEDIO AMBIENTE Y RECURSOS NATURALES
  Norma Oficial Mexicana de Emergencia NOM-EM-009-ASEA- 2026, Distribución de Gas Licuado de Petróleo por medio de Auto-tanque y Vehículo de Reparto. · `5800282` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800282&fecha=05/10/2026)

- **2026-10-02** · matutina · PODER EJECUTIVO › SECRETARIA DE MEDIO AMBIENTE Y RECURSOS NATURALES
  Norma Oficial Mexicana de Emergencia NOM-EM-008-ASEA- 2026, Transporte de Gas Licuado de Petróleo por medio de Auto-tanque y Semirremolque. · `5800169` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800169&fecha=02/10/2026)

- **2026-10-02** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el que se dan a conocer los porcentajes, los montos del estímulo fiscal y las cuotas disminuidas del impuesto especial sobre producción y servicios, así como las cantidades por litro aplicables a los combustibles que se indican, correspondientes al periodo que se especifica. · `5800257` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800257&fecha=02/10/2026)

- **2026-10-02** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con los Estados Unidos de América, correspondientes al periodo que se especifica. · `5800258` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800258&fecha=02/10/2026)

- **2026-10-02** · vespertina · PODER EJECUTIVO › SECRETARIA DE HACIENDA Y CREDITO PUBLICO
  Acuerdo por el cual se dan a conocer los montos de los estímulos fiscales aplicables a la enajenación de gasolinas en la región fronteriza con Guatemala, correspondientes al periodo que se especifica. · `5800259` · [DOF](https://dof.gob.mx/nota_detalle.php?codigo=5800259&fecha=02/10/2026)

_Unofficial data from the public SIDOF API. Only the printed/official DOF is authoritative. Not legal advice._
````

## get_note

`{"code": 5803775}` · 0.2 s · ok

````markdown
# Tipo de cambio para solventar obligaciones denominadas en moneda extranjera pagaderas en la República Mexicana.

| Field | Value |
| --- | --- |
| Code | `5803775` |
| Published | 2026-11-13 (matutina) |
| Issuer | ORGANISMOS AUTONOMOS › BANCO DE MEXICO |
| Page | 178 |
| Official page | https://dof.gob.mx/nota_detalle.php?codigo=5803775&fecha=13/11/2026 |
| Word file | https://sidof.segob.gob.mx/dof/sidof/documentos/doc/5803775 |
| Edition PDF | https://sidof.segob.gob.mx/dof/sidof/documentos/pdf/330805 |

---

## TIPO de cambio para solventar obligaciones denominadas en moneda extranjera pagaderas en la República Mexicana.

### Al margen un logotipo, que dice: Banco de México.- ''2026, Año de Margarita Maza Parada''.

TIPO DE CAMBIO PARA SOLVENTAR OBLIGACIONES DENOMINADAS EN MONEDA EXTRANJERA PAGADERAS EN LA REPÚBLICA MEXICANA

El Banco de México, con fundamento en los artículos 8o. de la Ley Monetaria de los Estados Unidos Mexicanos; 35 de la Ley del Banco de México, así como 8o. y 10 del Reglamento Interior del Banco de México, y según lo previsto en el Capítulo V del Título Tercero de su Circular 3/2012, informa que el tipo de cambio obtenido el día de hoy fue de $18.6188 M.N. (dieciocho pesos con seis mil ciento ochenta y ocho diezmilésimos moneda nacional) por un dólar de los EE.UU.A.

La equivalencia del peso mexicano con otras monedas extranjeras se calculará atendiendo a la cotización que rija para estas últimas contra el dólar de los EE.UU.A., en los mercados internacionales el día en que se haga el pago. Estas cotizaciones serán dadas a conocer, a solicitud de los interesados, por las instituciones de crédito del país.

Atentamente,

Ciudad de México, a 12 de noviembre de 2026.- BANCO DE MÉXICO: Gerente de Instrumentación de Operaciones, Lic. **Pilar María Figueredo Díaz**.- Rúbrica.- Subgerente de Operaciones de Mercado, Lic. **Carlos Miguel Vélez Martínez**.- Rúbrica.- Subgerente de Instrumentación de Operaciones Internacionales, Lic. **Luis Murray Arriaga**.- Rúbrica.- Subgerente de Cambios Nacionales, Lic. **Diego Rafael Toledo Polis**.- Rúbrica.

---

_Characters 0 to 1,581 of 1,581. End of note._

_Unofficial data from the public SIDOF API. Only the printed/official DOF is authoritative. Not legal advice._
````

## get_indicators

`{"date": "2026-11-17"}` · 0.2 s · ok

````markdown
# DOF financial indicators · 2026-11-17 (Tuesday)

| Indicator | Value | Unit | Published | Key |
| --- | --- | --- | --- | --- |
| Tipo de cambio FIX (dólar) | 18.5525 | MXN per USD | 2026-11-17 | `usd` |
| UDIS | 8.913896 | MXN per UDI | 2026-11-17 | `udis` |
| TIIE 28 días | 6.5147% | % annual | 2026-11-17 | `tiie28` |
| TIIE 91 días | 6.5492% | % annual | 2026-11-17 | `tiie91` |
| TIIE 182 días | 6.5995% | % annual | 2026-11-17 | `tiie182` |
| TIIE de fondeo | 6.26% | % annual | 2026-11-17 | `tiie_fondeo` |

Dates are DOF publication dates. Banco de México determines the FIX exchange rate and the TIIE on the previous business day.

_Unofficial data from the public SIDOF API. Only the printed/official DOF is authoritative. Not legal advice._
````

## get_indicator_history

`{"indicator": "usd", "date_from": "2026-11-01", "date_to": "2026-11-17"}` · 0.2 s · ok

````markdown
# Tipo de cambio FIX (dólar) · 2026-11-01 to 2026-11-17

10 published values (MXN per USD). First 18.7962 on 2026-11-03, last 18.5525 on 2026-11-17, change -0.2437 (-1.30%). Low 18.5525 on 2026-11-17, high 18.7962 on 2026-11-03.

| Date | Value |
| --- | --- |
| 2026-11-03 | 18.7962 |
| 2026-11-04 | 18.7592 |
| 2026-11-05 | 18.6285 |
| 2026-11-06 | 18.7147 |
| 2026-11-09 | 18.6297 |
| 2026-11-10 | 18.5983 |
| 2026-11-11 | 18.6678 |
| 2026-11-12 | 18.6192 |
| 2026-11-13 | 18.6188 |
| 2026-11-17 | 18.5525 |

_Unofficial data from the public SIDOF API. Only the printed/official DOF is authoritative. Not legal advice._
````
