# Reauditoría de Work 1 y auditoría/remediación de Work 2

Fecha de corte: 30 de agosto de 2026.

Este es el informe canónico posterior a la remediación. El informe original de
Work 2 queda como registro histórico y no debe usarse para heredar PASS, cifras
de tests ni autorización de publicación.

## Veredicto ejecutivo

| Alcance | Estado | Decisión |
|---|---|---|
| Work 1: decisiones de arquitectura pedagógica y runtime | VERDE | El piloto continúa siendo una base válida y Work 2 conserva sus invariantes. |
| Work 1: evidencia browser histórica | SUSTITUIDA | Los artefactos anteriores no prueban el código actual; los esquemas v1 ya no son válidos. |
| Work 2: código y gates locales ejecutables | VERDE | Correcciones aplicadas, regeneradas y comprobadas después de integrar `origin/main`. |
| Push/PR y CI | VERDE | PR #9 abierto en borrador; `pages` green en eventos `push` y `pull_request` sobre el snapshot remoto `d03141f2`. |
| Merge | ÁMBAR | El PR es mergeable/clean, pero branch protection no pudo inspeccionarse por API y no existe autorización de merge. |
| Publicación de Pages | ROJO | El deploy automático está deshabilitado. Publicar exige dispatch manual desde `main` y autorización previa de privacidad/contenido. |
| Baseline docente V2 | ROJO | Falta una dry-run humana cronometrada con el equipo real de aula. |
| Evaluación oficial | ROJO | Faltan fuente privada, bancos nuevos, allowlist y leakage/history gate. |

La auditoría se reabrió sobre `ee7df0863af141b7a43be44d2db5c269d68c12ab`.
La remediación técnica inicial se congeló en `df369717`; `origin/main`
(`fde4cbb3`) se integró sin rebase en `55866a86`. Una primera candidata,
`afbd5421`, fue rechazada por la reauditoría independiente al reproducir gaps
de rollback y procedencia. Este informe incorpora ese segundo ciclo de
corrección. El estado anterior a P0 quedó preservado en el checkpoint WIP
`7c8a3177`. El SHA exacto de cierre se registra en el handoff final, porque un
commit no puede incluir su propio hash de forma inmutable.

## Método de auditoría

Se aplicó la metodología general de auditoría y la auditoría cuantitativa al
plan, a su ejecución y a los artefactos resultantes. No se aceptaron como prueba
los PASS narrados por Work 1 o Work 2.

Cada afirmación material se contrastó mediante uno o varios de estos mecanismos:

- trazabilidad requisito → fuente → generado → test → gate;
- invariantes ejecutables y fixtures negativas;
- mutaciones adversariales que deben fallar y hacer rollback;
- conjuntos cerrados con cardinalidad exacta;
- regeneración determinista y comprobación de no-drift;
- dos builds independientes de Pages;
- validadores de evidencia separados de los runners browser;
- red-team paralelo de motor, pedagogía, Desktop, Pages, dependencias y CI.

## Plan ejecutado

| Fase | Resultado |
|---|---|
| Congelar baseline y criterios | Cerrada. Work 1 se trató como histórico y Work 2 se volvió a derivar desde fuentes. |
| Auditar en paralelo | Cerrada para motor/capstone, pedagogía, Desktop, Pages, locks, workflows y documentación. |
| Corregir y regresionar | Cerrada. Todo hallazgo reproducible local dispone de corrección o gate fail-closed. |
| Regenerar | Cerrada: L1–L14, índice, reportes pedagógicos y práctica L15. |
| Integrar `origin/main` | Cerrada mediante merge explícito; conflictos Pages resueltos conservando readiness y endurecimiento. |
| Validar el resultado integrado | Cerrada para todos los gates ejecutables en este host. |
| Evidencia browser CI | Cerrada sobre `d03141f2`: WebKit móvil, L1–L14 y agregador green. |
| Dry-run y privacidad | Abiertas; requieren validación humana y la arquitectura privada de evaluación. |

## Hallazgos materiales cerrados

| Grupo | Hallazgo auditado | Disposición |
|---|---|---|
| Motor | Overfill, FOK parcial, remanentes no representables, mutación tardía de `Order`, timestamp con pérdida y notional no contable. | Planificación exacta con `Fraction`, validación antes de commit y rollback autoritativo. |
| Motor | Generadores diferidos y callbacks podían mutar aliases de market/portfolio, corromper la forma del libro, alterar atributos/RNG o dejar estado parcial al lanzar. | Materialización bajo guardia, snapshots internos recursivamente sellados, rollback in-place de contenedores y RNG con identidad preservada, y eliminación de atributos añadidos durante el hook. |
| Motor | Los guards copiaban el replay y recorrían todo el historial de fills en cada hook. | Replay inmutable y ledger persistente privado de `Backtest`; checkpoints, detección y rollback de fills son O(1), con regresiones que prohíben escanear el historial. |
| Motor/contabilidad | La tolerancia simétrica `math.isclose` aceptaba pérdidas o excesos absolutos grandes a escalas extremas; el umbral posterior rechazaba un primer fill representable de VWAP. | Fidelidad exacta con `Fraction`, ligada solo al efecto esperado (1 parte por cien mil millones), signo obligatorio y rechazo atómico de progreso nulo, overfill y distorsión material. |
| Contabilidad | `PositionTracker`, VWAP, MM y simulación podían aceptar progreso tragado o distorsionado por redondeo/mutación. | Comprobación del efecto económico, configuración revalidada y fallos atómicos. |
| Simulación | `A·exp(-κδ)` se aplicaba como probabilidad por paso en vez de intensidad de horizonte; además `s0≤0.5` se aceptaba aunque el libro sintético no podía construir un bid positivo. | Probabilidad por paso corregida, dominio del semispread validado antes del lifecycle y escenarios/capstone recalibrados con referencias bloqueadas por tests. |
| L8/L9 | Se mezclaba el matcher didáctico con el core exacto y `Market.step/reset` no enseñaba commit conjunto. | Modelo `StudentMatchingEngine` separado; core canónico visible; commits de índice/book/timestamp y reset atómicos. |
| L12 | El material visible de VWAP no garantizaba target final ni retry del residual. | Ejemplo y estrategia sincronizados con ejecución exacta/fail-closed. |
| Capstone | Score, checksum y baseline podían confundirse con acreditación o usar una simulación sin fills. | Feedback no agregable a nota, no ranking sin reejecución y baseline calibrado con `ARRIVAL_INTENSITY=630`. |
| Pedagogía | Rutas mixtas, tiempos, guiones, APIs, snapshots L4–L7 y claims de datos podían dar falsos verdes. | Contrato aditivo por stage, guard privado de fidelidad de notional desde L4 sin filtrar APIs futuras, guion embebido L1–L14, `Market.from_csv` trazable y provenance sintético explícito. |
| Gobernanza documental | El piloto remitía a un informe histórico como estado vigente, el plan nombraba `VWAPStrategy.run` y dos golden sources seguían rotulados como propuestas. | Cadena canónica dirigida a este informe, API corregida a `on_book_update`/`Backtest.run` y estados autoritativos alineados con `AGENTS.md`. |
| Desktop | Modales, foco, scroll, deep links, breakpoint 901–960 y OPTIONAL tenían huecos de cobertura. | Runtime y plan cerrado endurecidos; 132 registros y 661 estados recalculables. |
| Evidencia | Un corpus sintético podía aparentar PASS con browser ficticio, sin PNG ni hashes completos. | Esquema browser v2: launcher y payload completos, 32 inputs, 9 PNG mínimas y validadores independientes. |
| Pages | Manifest abierto, RFQ accidental, path collisions, symlinks, staging, Mermaid CDN, variantes de red dinámica y falsos positivos del propio guard CSP permitían deriva, fuga o builds imposibles. | Proyección cerrada de 28 notebooks core, rutas seguras, bloqueo estático/browser de HTTP, WebSocket, `object`, `embed`, SVG, manifest y protocolos concatenados, y allowlist criptográfica limitada a los cinco redirects same-origin generados por JupyterLite. |
| Pages/JupyterLite | Pyodide se registraba dos veces: por autodiscovery y por argumento explícito de build. | Se usa exclusivamente el autodiscovery de JupyterLite 0.8.1 y se valida previamente la extensión exacta instalada bajo `sys.prefix`. |
| Pages/JupyterLite | El E2E bloqueaba el service worker que implementa `/api/drive` y buscaba la clase obsoleta `.jp-Toolbar-kernelStatus`. | El laboratorio permite solo el service worker same-origin endurecido y observa `.jp-KernelStatus-widget`; site estático, CSP, configuración y worker mantienen el cierre offline. |
| Pages | El build podía atribuir a `GITHUB_SHA` fuentes modificadas que no existían en ese commit. | `.pages-integrity.json` schema 2; builder y checker contrastan todos los inputs y fuentes con los blobs del commit, rechazan symlinks y comparan dos builds byte a byte. |
| WebKit | Un PASS no probaba identidad exacta, un único dispatch ni ejecución real de kernel por shard. | Evidencia por site y L1–L14 con browser/payload v2, nonce, prompt, idle y cardinalidad exacta; cada shard se revalida antes del upload y un job agregado exige los 15 JSON y 29 targets exactos. |
| Dependencias/CI | Lock incompleto, instalación no reproducible y deploy desacoplado o automático. | Lock CPython 3.11 con hashes/binarios, acciones fijadas por SHA, curso reusable y publicación manual-only desde `main`. |

## Evidencia local válida tras el merge

| Gate | Resultado |
|---|---|
| Contrato pedagógico | `PED-CHECK-01..09` green para L1–L15. |
| Reportes derivados | `pedagogy_reports.py --check` sin drift. |
| Ejercicios | 293/293 autovalidados en L1–L14. |
| Python | 523/523 tests locales; el job remoto `validate` repitió 523 green con Python 3.11.9. |
| Motor | Smoke end-to-end green. |
| Fuzz de matching | `fuzz_matching.py --seed 20260828 --cases 120000`: digest `a1caad709e7f4af466fa6b8d26b7a58a698556344584eb636673ce94b9b9cab5`, 28.872 éxitos, 91.128 rechazos atómicos y 0 violaciones de atomicidad, overfill, FOK, mutación, salida o identidad. |
| Scripts consolidados | 16/16 ejecutados. |
| Contratos Node | 52/52 en la validación local completa; Pages conserva además 30 contratos focalizados para runner y auditor independiente. |
| Desktop estático | 132 IDs, 661 estados, 14 overrides, 32 inputs y contrato de 9 PNG. |
| Curso/L15 | Regeneración completa y práctica pública de 40 preguntas sin drift. |
| Pages local | Dos builds: 51 HTML y 28 notebooks docentes/editables cada uno; manifests idénticos, una sola extensión Pyodide autodetectada y redirects JupyterLite same-origin validados. No sustituye la ejecución browser de CI. |
| Higiene | Sintaxis Python/JS, YAML, fuentes tracked y `git diff --check` green. |

La ejecución local de Chromium/WebKit no se presenta como PASS. El launcher
WebKit fijado fue identificado, pero este host carece de varias dependencias
del sistema, incluida `libgstreamer-1.0.so.0`; los workflows las instalan y
deben producir los artefactos canónicos sobre el mismo SHA comprometido. Toda
evidencia Desktop/WebKit v1 queda invalidada.

## Evidencia remota P1

| Superficie | Evidencia verificada |
|---|---|
| Rama/PR | Rama pública `fix/work2-audit-remediation`; PR #9 abierto, draft, mergeable y `clean` contra `main@fde4cbb3`. |
| Snapshot funcional | `d03141f2d52dcf6b5c1ca0a5d5f6e279099f9d51`; árbol `dd52dac007b381a7e7e29766041202105c787542`. |
| Workflow por push | `pages` run #70 (`33313959540`): success. |
| Workflow del PR | `pages` run #71 (`33313961526`): success. |
| Curso reusable | `validate` y `e2e`: success; incluye PED-CHECK-01..09, 523 tests y fuzz de 120.000 casos sin violaciones. |
| Pages/WebKit | Build reproducible de 51 HTML/28 notebooks, WebKit móvil y shards L1–L14: success. Cada notebook ejecuta un único dispatch y una única ejecución de kernel. |
| Evidencia cerrada | Agregador: success; 17 artefactos vigentes vinculados al mismo head SHA (site, Desktop y 15 evidencias Pages). |
| Publicación | Los jobs de preparación y deploy quedaron `skipped`; no se publicó Pages. |
| Branch protection | `NEEDS_VERIFICATION`: el endpoint de protección devolvió 403 para la integración y el endpoint de rulesets no expuso reglas. |

El commit de sincronización documental posterior no cambia código ni contratos.
Como un documento no puede contener de forma inmutable su propio SHA, el head
vigente y sus checks se consultan en el PR; cualquier cambio posterior exige
de nuevo CI green sobre ese head exacto.

## Riesgos y trabajo residual

### Bloqueantes externos

1. Verificar o configurar branch protection y checks requeridos antes del
   merge; la integración actual no permite leer esa política.
2. Revisar el PR, retirarlo de draft y solicitar autorización explícita antes
   de fusionar.
3. Ejecutar `work2-teaching-dry-run.md` con proyector/equipo real; corregir y
   repetir cualquier lesson fuera de tolerancia.
4. Crear y autorizar la fuente privada, rotar bancos oficiales y aplicar
   allowlist, leakage e history gate antes de una publicación/evaluación real.

### Residual técnico no bloqueante

- No queda un defecto funcional local reproducible abierto en el alcance
  Work 1/Work 2. La publicación manual continúa siendo una contención
  operativa, no un sustituto de la arquitectura
  privada→allowlist→pública exigida por `ARCHITECTURE.md`.

## Criterio de escalada

- **GO local, GO P1 y GO para revisión técnica del PR.**
- **NO-GO merge** hasta verificar branch protection, completar la revisión y
  recibir autorización explícita de merge.
- **NO-GO baseline docente V2** hasta la dry-run humana.
- **NO-GO publicación segura/evaluación oficial** hasta cerrar la topología
  privada y renovar material ya divulgado.
