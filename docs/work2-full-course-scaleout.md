# Work 2 — Full-Course Scale-Out (informe histórico)

> **Evidencia sustituida.** Este documento conserva las decisiones y resultados
> del scale-out original, pero sus PASS, cifras y veredicto no son vigentes. La
> reauditoría posterior, las correcciones, la integración con `origin/main` y el
> backlog actual están en [`work1-work2-reaudit.md`](work1-work2-reaudit.md).

## Veredicto ejecutivo

**GO técnico local para push/PR; merge condicionado a CI remota green;
NO-GO para declarar baseline docente V2 o evaluación oficial desplegable.**

La remediación local pasa continuidad, API, generación, motor, assessment público,
build estático y contratos de CI. La matriz Chromium/WebKit/JupyterLite debe volver a
ejecutarse en GitHub Actions sobre el SHA integrado: la evidencia visual anterior
se invalidó porque correspondía al Work 2 pre-remediación. El GO docente exige
además una dry-run humana cronometrada con el equipo real de aula. La evaluación
oficial sigue fail-closed hasta disponer de bancos nuevos en la futura fuente
privada; el banco público solo sirve como práctica.

## Baseline y alcance

- Rama: `v2/full-course-learning-runtime-scaleout`.
- Baseline esperado y encontrado: `6a26397ef8e5ef2d9de8a3811b6cc4c614fb4df8`.
- Ese commit es `Merge Work 1 desktop learning runtime pilot (#7)` y era el HEAD
  de `main`, `origin/main` y `origin/HEAD` al iniciar.
- HEAD funcional auditado antes de añadir este informe:
  `1c43d140e5abb40389ed9f10bb0ef0ae3c8a131b`.
- El SHA del commit que contiene este propio informe se entrega en el handoff
  final: un documento no puede incluir de forma inmutable el hash de su propio
  commit.

El gate inicial confirmó el merge aceptado de Work 1, leyó su informe, el
contrato pedagógico, la arquitectura, el runtime, los manifests, el checker y los
artefactos de auditoría. `main` no había avanzado y no fue necesario reconciliar
commits ni resetear. La suite heredada pasó antes del scale-out.

El alcance conserva el repositorio público actual y no implementa la futura
separación private/public ni añade un banco privado de evaluación. La remediación
sí endurece JupyterLite y hace que Pages dependa del workflow reusable de curso;
eso no sustituye la topología de dos repositorios exigida por `ARCHITECTURE.md`.

La auditoría posterior congeló Work 2 en
`ee7df0863af141b7a43be44d2db5c269d68c12ab` y ejecutó la corrección en
`fix/work2-audit-remediation`. Esa rama no reescribe Work 1/Work 2 ni habilita la
topología privada sin autorización y repositorio destino disponibles.

La reauditoría no acepta como evidencia los PASS históricos de Work 1 ni Work 2:
cada gate se vuelve a derivar del checkout remediado. Los commits de motor y
capstone hasta `c9666508` preceden al cierre de runtime, tiempos, desktop y Pages;
el SHA final se registra en el handoff/PR una vez comprometido el informe.

## Checkpoints

| Checkpoint | Commit | Contenido |
|---|---|---|
| Contrato/checker | `f6c11373` | Grafo L1–L15, registries, rutas, blueprint, checker y reportes. |
| Foundations | `ac272ce6` | Migración y alineación de L1–L6. |
| Engine | `43f67c98` | Migración de L7–L10 y progresión acumulativa del motor. |
| Strategies | `b6c69d27` | L11–L14, métricas, VWAP, market making, A-S y capstone. |
| Assessment | `7c9e6ef0` | L15 y trazabilidad acumulativa de la evaluación. |
| Hardening | `56e98f11` | CI, desktop, mobile, Pages, JupyterLite y artefactos visuales. |
| Documentación | `1c43d140` | Autoría futura, mapa, README y gate de dry-run. |

Los checkpoints anteriores describen el Work 2 original, no la evidencia vigente.
La remediación añade commits separados para assessment/capstone, motor, unidades
A-S, CI/Pages, runtime y contrato pedagógico; el SHA integrado se fija en el PR.

La validación original se ejecutó sobre el conjunto completo de estos checkpoints;
sus conclusiones fueron después reabiertas por la auditoría y no se heredan como
prueba de la rama remediada.

## Arquitectura final

### Contrato verificable

`pedagogy/` es la fuente machine-readable de continuidad. Sus ficheros `.yml`
siguen siendo JSON compatible, por lo que CI no necesita un parser adicional.

- 93 conceptos estables.
- 78 APIs visibles registradas.
- 14 identificadores de notación.
- 15 manifests completos.
- 293 ejercicios clasificados deliberadamente.
- 0 requisitos sin introducción anterior.
- 0 dependencias cuyo único origen sea OPTIONAL.

`pedagogy_check.py` aplica PED-CHECK-01…09: orden de introducción, continuidad de
API, referencias, recalls, clasificación, assessment, carga, bindings al paquete
acumulativo y consistencia entre registries/manifests.

Los reportes derivados son:

- [`course-dependency-report.md`](course-dependency-report.md): primera
  introducción, reutilización, recalls y assessment.
- [`student-journey-audit.md`](student-journey-audit.md): entrada, construcción,
  práctica, rutas, pieza acumulativa y necesidad causal de la siguiente lesson.

### Un contenido, varios recorridos

Los cuerpos de `framework/_build/` siguen siendo la única fuente editorial. El
runtime compartido interpreta las escenas declaradas:

- `?mode=aula`: una escena activa, LIVE por defecto, teclado y sin scroll del
  `body` en desktop.
- `?mode=estudio`: LIVE + REQUIRED en vertical; OPTIONAL solo por opt-in.
- `?mode=aula&profe=1`: guía docente y ampliación explícita de alcance.
- Pantallas de hasta 900 px: fallback vertical de estudio.
- Deep links estables por escena/etapa y progreso persistente por ruta.

El índice usa el mismo estado y presenta cuatro bloques: Foundations L1–L6,
Engine L7–L10, Strategies L11–L14 y Assessment L15.

### Código acumulativo y publicación

Presentación, notebooks, auxiliares, scripts, `exchange/` y objetivos de
assessment se generan o validan contra el mismo contrato. Los snapshots de L4,
L5 y L7 impiden filtrar APIs futuras antes de L8. Desde L8, cada starter expone
solo la superficie que el alumno ya ha construido.

L15 conserva una UX lineal de **práctica acumulativa pública**. No es el examen
oficial y no acredita nota. Pages construye HTML estático, notebooks y un
JupyterLite offline con los archivos de cada lesson; no existe una segunda versión
manual de los notebooks.

## Decisiones pedagógicas y gaps cerrados

| Gap encontrado | Resolución |
|---|---|
| Clasificación legacy por posición | Cada ejercicio L1–L14 tiene ruta y tiempo explícitos; falta o sobra implica fallo de build. |
| Sintaxis usada sin trazabilidad | Registry de Python, requisitos y recalls desde L1 hasta L15. |
| `OrderBook` método/property | `best_bid`, `best_ask`, `spread` y `mid` son properties desde L5; `imbalance(levels=1)` sigue siendo método. |
| Superficie final filtrada a lessons tempranas | Snapshots progresivos: L4 solo LIMIT/MARKET; IOC, FOK, `Side.opposite`, `add_limit` y `reduce` nacen en L8. |
| Promesa L6 desconectada de L10 | Recall visible `decide(...) -> str` → `on_book_update(book) -> list[Action]`, conservando el polimorfismo. |
| L11 mezclaba PnL y ejecución | Parent arrival mide la decisión completa; cada child decision mid mide sus fills; inventario se juzga aparte. |
| L12 podía sobredimensionar la predicción | TWAP/VWAP y slicing son core; predicción dinámica es OPTIONAL, no evaluable y no requerida después. |
| L13 no preparaba toda la notación de L14 | CARA e intensidad de fills quedan como preparación LIVE breve; L14 las recupera sin derivar HJB. |
| `tau` y horizonte inconsistentes | El helper privado `_time_left()` calcula `tau = clip((horizon - time) / horizon, 0, 1)`; `time` conserva una semántica pública estable y al vencimiento desaparece el skew temporal sin fingir liquidación. |
| Capstone competía con la clase | Se separa como proyecto REQUIRED autónomo de 90 min, usando `mi_estrategia.py`; no ocupa el núcleo presencial. |
| Capstone trivialmente puntuable | El starter queda deliberadamente incompleto; `capstone_check.py` no emite feedback ni código hasta implementar la estrategia. |
| Capstone aún puntuable con `reservation_price(mid) = mid` | Una sonda conductual exige quotes finitas, ordenadas y un centro que responda al inventario en ambos sentidos. |
| Código público tratado como acreditación | Se etiqueta como autoinforme no autenticado y el leaderboard no rankea nada sin verificación externa; el score queda como feedback formativo fuera del 10/20/40/30. |
| Assessment sin trazabilidad completa | La práctica pública cubre L1–L14 y cinco tipos de pregunta con IDs semánticos; OPTIONAL queda excluido. Los bancos oficiales permanecen privados/fail-closed. |
| Motor con fills/restos incoherentes | Las LIMIT propias no entran en el libro externo del backtest y no pueden autocruzarse; cancelación, fills parciales, VWAP, snapshots defensivos, símbolo y feedback de market making tienen invariantes y regresiones ejecutables. |
| Inputs no finitos y perfiles VWAP inválidos | Órdenes, niveles, fills, books, portfolio, scoring, quotes y parámetros rechazan NaN/infinito; VWAP exige horizonte entero positivo, perfil exacto, no negativo y normalizado. |
| Ciclos de vida y estados contaminados | `Backtest` y `MMSimulation` son single-use; exigen market/strategy frescos, bloquean acciones desconocidas y comprueban sincronía dinámica del inventario. |
| Modelo A-S contradictorio | Seed entero reproducible y un único contrato `sigma/horizon/kappa` entre estrategia y simulador, sin filtrar la clase L14 al snapshot L13. |
| Tiempos de ruta mixta daban falsos verdes | `scene.duration_minutes` presupuesta la ruta base y cada override declara `stage.duration_minutes` aditivo; 14 identidades quedan ligadas exactamente a su espejo autónomo. |
| Runtime validaba una ruta distinta de la visible | `stage.route` prevalece, deep links frescos amplían alcance, ruta/minutos/estado/UI/progreso se sincronizan y foco/scroll/clipping fallan cerrado. |
| Teclado y modales filtraban acciones al fondo | Un coordinador único conserva/restaura el `inert` previo, impide dos cajones abiertos, bloquea fondo/shortcuts, respeta scroll nativo y prueba ambos handoffs, foco y modal mobile/estudio. |
| Breakpoint 901–960 heredaba layout flex | Aula restablece explícitamente `display:grid`; la matriz prueba 900, 901, 920, 960 y 961 px. |
| Evidencia desktop podía pasar incompleta | Plan cerrado de 132 registros/661 identidades, 32 hashes, SHA contra `HEAD`, 9 capturas mínimas y validador que recalcula IDs, secuencias, errores y browser. |
| `Market.from_csv` se enseñaba sin contrato | Queda registrada como classmethod REQUIRED de L9, incluida en superficie, objetivo, binding de paquete y reporte derivado. |
| Playwright se instalaba fuera de lockfile | Node 20.19.4, npm 10.8.2 y Playwright 1.62.1 quedan declarados; `npm ci` gobierna los workflows de curso y Pages. |
| JupyterLite podía publicarse sin kernel Python u offline falso | Extensión exacta más Pyodide 314.0.1 empaquetado same-origin con SHA-256; el E2E aborta cualquier request externa. |
| Pages copiaba configuración raíz accidental | Proyección cerrada excluye `.vscode`, `package*.json`, guiones y `CLAUDE.md`; el checker falla si reaparecen. |
| Datos sintéticos descritos como reales | Plan, guiones, docs y HTML dicen “sintéticos/reproducibles”; una regresión impide recuperar el claim falso. |
| Deploy desacoplado de la suite fuente | `pages/package` necesita éxito del workflow reusable `curso` del mismo evento/SHA. |
| Referencias históricas y nombres antiguos | Regeneración y checker de referencias/anchors sobre L1–L15; no quedan referencias obsoletas conocidas. |

## APIs normalizadas

| Origen | Superficie estable |
|---|---|
| L4 | `Side`, `OrderType`, `Order`, `Fill`, constructores y cash-flow/notional. |
| L5 | `Level`, `OrderBook`, properties de precio, `imbalance(levels)`, `PositionTracker`. |
| L7 | `OrderBook.from_snapshot`, `depth`, `microprice`; frontera de datos externos. |
| L8 | `MatchingEngine.process(order, book, timestamp=None) -> list[Fill]`, atomicidad y políticas. |
| L9 | `Market.book`, `step`, `submit`, `reset`, `timestamp`, classmethods `from_csv`/`sample` y property defensiva `snapshots`. |
| L10 | Tipos públicos `Strategy`, `NewOrder`, `Cancel`, `Action`, `Backtest`, `BacktestResult` y lifecycle. |
| L12 | `VWAPStrategy` con tamaño, horizonte y perfil normalizado. |
| L13 | `MarketMaker`, inventario público, `MMSimulation` y `SimResult`. |
| L14 | `AvellanedaStoikov`, `time`, reservation price, optimal spread y quotes. |

Los bindings comprueban clase/tipo/alias, método/property/classmethod, argumentos,
defaults, anotaciones y retorno. No queda un cambio silencioso de API visible
conocido.

## Cambios y carga lesson por lesson

| Lesson | Construcción cerrada | LIVE presentación | Práctica guiada | REQUIRED autónomo | OPTIONAL |
|---|---|---:|---:|---:|---:|
| L1 | dato → cálculo → decisión | 20 | 19 | 78 | 45 |
| L2 | duplicación → funciones → book compartido | 20 | 18 | 80 | 41 |
| L3 | notebook → módulo y errores de dominio | 20 | 18 | 75 | 5 |
| L4 | dict/resultado → `Order` y `Fill` | 20 | 20 | 57 | 20 |
| L5 | composición, `OrderBook` y contabilidad | 20 | 20 | 52 | 15 |
| L6 | herencia, ABC y contrato polimórfico | 20 | 20 | 74 | 10 |
| L7 | snapshot sintético → frontera de dominio | 20 | 19 | 63 | 10 |
| L8 | PLAN → VALIDATE → COMMIT y atomicidad | 20 | 19 | 77 | 15 |
| L9 | estado + dinámica + tiempo en `Market` | 20 | 20 | 44 | 10 |
| L10 | decisión/ejecución y runner intercambiable | 20 | 21 | 38 | 5 |
| L11 | señal, benchmarks, slippage e inventario | 20 | 20 | 33 | 10 |
| L12 | impacto → slicing → TWAP/VWAP | 20 | 20 | 22 | 47 |
| L13 | spread, adverse selection, inventario y skew | 20 | 20 | 27 | 0 |
| L14 | heurística → reservation price/optimal spread | 22 | 21 | 133 | 10 |
| L15 | assessment acumulativo lineal, 40 min | — | — | — | — |

Todos los valores son minutos; la práctica guiada conserva la suma exacta
18–22 de `exercise_routes.yml`, sin redondearla a 20. Las demás cargas suman
documentos, ejercicios, quiz y proyecto.
L14 contiene 35 min de ejercicios REQUIRED, un quiz de 8 min y una única
actividad de capstone de 90 min, representada como documento y proyecto con el
mismo `overlap_id` para no contarla dos veces. La carga extraordinaria es visible
y no se presenta como trabajo doméstico incidental. L12 suma 35 min de ejercicios
OPTIONAL y 12 min de documento OPTIONAL para predicción dinámica de volumen.

## Validación ejecutada en el Work 2 original (sustituida)

| Gate | Resultado final |
|---|---|
| Checker pedagógico | PED-CHECK-01…09, L1–L15: green. |
| Fixtures positivos/negativos | Futuro, ruptura de API, REQUIRED→OPTIONAL, referencia inexistente, assessment OPTIONAL y eliminación de introducción detectados; recall válido y curso real pasan. |
| Reportes generados | `pedagogy_reports.py --check`: diff cero. |
| Ejercicios | 293 ejercicios en 14 lessons autovalidados. |
| Tests Python | 242 passed en la suite integrada. |
| Motor | Smoke end-to-end: green. |
| Scripts consolidados | 16/16, L1–L14: green; el starter termina sin puntuación e indica qué implementar. |
| Regeneración | Curso, reportes y práctica pública de 40 preguntas regenerados sin drift. |
| Contratos Node | 17/17 tests: 7 de Pages y 10 del contrato desktop/evidencia. |
| E2E documental | Harness y runtime parsean; la ejecución Chromium integrada queda pendiente de Actions. |
| Desktop | Plan local validado: 132 IDs únicos, 661 estados, 14 overrides y 32 inputs; ejecución Chromium integrada pendiente de Actions. |
| Pages estático | Build/link/base-path local green: 54 HTML/29 notebooks; configuración raíz excluida. |
| JupyterLite offline | Pyodide 314.0.1 same-origin (13 archivos) con archive SHA-256; matriz WebKit L1–L14 pendiente de Actions. |
| Higiene | `git diff --check`: green. |

El harness vigente espera una señal estable de kernel ready/idle y envía
exactamente un dispatch por contexto. Un timeout o error descarta el contexto
completo y reintenta el notebook en uno nuevo; nunca envía una segunda ejecución
al mismo worker. La evidencia exacta y vigente se describe en la reauditoría.

## Matriz de viewports

| Viewport | Cobertura |
|---|---|
| 1280×720 | L1–L14 LIVE completo; L15 lineal. |
| 1440×900 | LIVE de todas; LIVE+REQUIRED de todas; ALL representativo con OPTIONAL. |
| 1920×1080 | L1–L14 LIVE completo; L15 lineal. |
| 2560×1440 | L1–L14 LIVE completo; L15 lineal. |
| 390×844 | Fallback mobile de L1–L14; L15 lineal; WebKit/Pages. |

La matriz también cubre teclado, foco, Escape, drawers, deep links, persistencia,
reduced motion, opt-in OPTIONAL, retorno al índice, errores JS, body scroll y
overflow horizontal. Una fixture inyecta overflow en una etapa intermedia y
demuestra que el detector falla cuando debe.

## Artefactos visuales

Los diez artefactos versionados del Work 2 original se eliminaron porque no
contenían SHA, versión de navegador ni hashes de inputs y ya no representaban el
código remediado. `desktop_e2e.js` limpia su directorio antes de cada ejecución:
solo crea `desktop-audit.json` con `completed:true` y un campo `passed` explícito
si termina los 132 registros/661 estados exactos; un fallo temprano deja
únicamente `desktop-audit-incomplete.json` con fase, check activo, resultados
parciales, SHA y hashes. Un segundo proceso, independiente de Playwright,
recalcula `HEAD`, cada `check_id`, las 661 identidades ordenadas, errores, browser,
9 capturas y los 32 inputs antes del upload. La
evidencia válida de esta rama será el artefacto inmutable de Actions asociado al
SHA del PR.

## Deuda, riesgos y discrepancias con Work 1

### Deuda técnica

- El repositorio sigue siendo único y público. La fuente privada autoritativa,
  manifest de publicación, allowlist, leakage gate e historial saneado de
  `ARCHITECTURE.md` no pueden implementarse hasta crear/autorizar
  `algo_trading_intro_source` y rotar material de assessment ya divulgado.
- El arranque frío de Pyodide puede ser lento o emitir un error transitorio; el
  gate espera kernel ready/idle, reintenta la lesson completa en contexto nuevo y
  mantiene el fallo si se reproduce.
- La ejecución remota de GitHub Actions y la configuración administrativa de
  checks requeridos/branch protection quedan pendientes del push/PR.

### Deuda pedagógica

- **Bloqueante:** falta dry-run docente humana, cronometrada y con proyector real.
- L1–L9 tienen cargas REQUIRED autónomas apreciables; están explicitadas, pero la
  dry-run debe confirmar ritmo, fatiga y expectativa real del alumnado.
- L14 tiene 133 min REQUIRED por diseño (35 min de ejercicios + capstone de 90 +
  quiz de 8); debe comunicarse como proyecto separado y validarse con alumnos
  reales.

### Discrepancias con Work 1

- Work 1 dejó varias lessons con tiers legacy; Work 2 las sustituye por decisiones
  explícitas sin cambiar la taxonomía ni el runtime aprobado.
- Work 1 auditó cuatro pilotos; Work 2 extiende la geometría y navegación a todas
  las lessons y mantiene L7–L9 como oráculo conceptual.
- La deuda de cronometraje que Work 1 aceptó temporalmente no se ha podido cerrar
  sin participación humana. En lugar de ocultarla, este informe convierte el
  veredicto docente en NO-GO.
- Sí queda una discrepancia arquitectónica externa y bloqueante: la topología
  private→allowlist→public aún no existe y el material históricamente público se
  considera divulgado. Este Work no puede cerrarla sin repositorio/credenciales
  autorizados y bancos nuevos.

## Recomendación final

**GO técnico local / GO para push y PR:** la rama cumple los gates locales
ejecutables. **NO-GO de merge** hasta que los workflows `curso` y `pages`
confirmen la matriz integrada en remoto y el PR exija esos checks.

**NO-GO docente:** no debe etiquetarse todavía como baseline docente V2. Para
cambiar el veredicto a GO, el owner debe ejecutar y registrar el protocolo de
[`work2-teaching-dry-run.md`](work2-teaching-dry-run.md), empezando por L1, L8,
L10 y L14, corregir cualquier desviación y repetir la lesson afectada.

**NO-GO de evaluación oficial/publicación segura:** el examen final obligatorio y
los tests continuos requieren bancos privados nuevos. La práctica pública no puede
reutilizarse como oficial; la migración private→public queda como Work separado.
