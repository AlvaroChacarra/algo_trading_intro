# Work 2 — Full-Course Desktop Scale-Out + Pedagogical Continuity Closure

## Veredicto ejecutivo

**GO técnico local y GO para PR/revisión; merge condicionado a CI remota green;
NO-GO para declarar esta rama baseline docente V2.**

El curso completo pasa los gates automáticos de continuidad, API, generación,
motor, desktop, mobile/WebKit, Pages y JupyterLite. La única condición que impide
el GO docente es externa al código: no existe una dry-run humana cronometrada con
el equipo real de aula. Las estimaciones contractuales y las pruebas geométricas
no sustituyen esa evidencia. El protocolo y la deuda están registrados en
[`work2-teaching-dry-run.md`](work2-teaching-dry-run.md).

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

El alcance conserva la arquitectura pública actual: no implementa la futura
separación private/public, no cambia JupyterLite ni la publicación, y no añade un
nuevo banco privado de evaluación.

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

La validación final se ejecutó sobre el conjunto completo de estos checkpoints y
la regeneración posterior produjo diff cero.

## Arquitectura final

### Contrato verificable

`pedagogy/` es la fuente machine-readable de continuidad. Sus ficheros `.yml`
siguen siendo JSON compatible, por lo que CI no necesita un parser adicional.

- 93 conceptos estables.
- 74 APIs visibles registradas.
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

L15 conserva su UX lineal de examen. Pages construye HTML estático, notebooks y
un JupyterLite offline con los archivos de cada lesson; no existe una segunda
versión manual de los notebooks.

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
| `tau` y horizonte inconsistentes | El helper privado `_time_left()` calcula `tau = max(0, (horizon - time) / horizon)` en `[0, 1]`; `time` conserva una semántica pública estable y al vencimiento desaparece el skew temporal sin fingir liquidación. |
| Capstone competía con la clase | Se separa como proyecto REQUIRED autónomo de 90 min, usando `mi_estrategia.py`; no ocupa el núcleo presencial. |
| Assessment sin trazabilidad completa | Cada objetivo evaluable apunta a conocimiento LIVE/REQUIRED; OPTIONAL queda excluido. |
| Referencias históricas y nombres antiguos | Regeneración y checker de referencias/anchors sobre L1–L15; no quedan referencias obsoletas conocidas. |

## APIs normalizadas

| Origen | Superficie estable |
|---|---|
| L4 | `Side`, `OrderType`, `Order`, `Fill`, constructores y cash-flow/notional. |
| L5 | `Level`, `OrderBook`, properties de precio, `imbalance(levels)`, `PositionTracker`. |
| L7 | `OrderBook.from_snapshot`, `depth`, `microprice`; frontera de datos externos. |
| L8 | `MatchingEngine.process(order, book, timestamp=None) -> list[Fill]`, atomicidad y políticas. |
| L9 | `Market.book`, `step`, `submit`, `reset`, `timestamp`, `sample` y property defensiva `snapshots`. |
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
| L1 | dato → cálculo → decisión | 20 | 20 | 58 | 44 |
| L2 | duplicación → funciones → book compartido | 20 | 20 | 58 | 41 |
| L3 | notebook → módulo y errores de dominio | 20 | 20 | 52 | 5 |
| L4 | dict/resultado → `Order` y `Fill` | 20 | 20 | 36 | 20 |
| L5 | composición, `OrderBook` y contabilidad | 20 | 20 | 34 | 15 |
| L6 | herencia, ABC y contrato polimórfico | 20 | 20 | 52 | 10 |
| L7 | snapshot real → frontera de dominio | 20 | 20 | 42 | 10 |
| L8 | PLAN → VALIDATE → COMMIT y atomicidad | 20 | 20 | 56 | 15 |
| L9 | estado + dinámica + tiempo en `Market` | 20 | 20 | 34 | 10 |
| L10 | decisión/ejecución y runner intercambiable | 20 | 20 | 12 | 5 |
| L11 | señal, benchmarks, slippage e inventario | 20 | 20 | 14 | 10 |
| L12 | impacto → slicing → TWAP/VWAP | 20 | 20 | 14 | 35 |
| L13 | spread, adverse selection, inventario y skew | 20 | 20 | 19 | 0 |
| L14 | heurística → reservation price/optimal spread | 22 | 20 | 125 | 10 |
| L15 | assessment acumulativo lineal, 40 min | — | — | — | — |

Todos los valores son minutos. L14 contiene 35 min de ejercicios REQUIRED y un
proyecto REQUIRED separado de 90 min. La carga extraordinaria es visible y no se
presenta como trabajo doméstico incidental. L12 reserva sus 35 min OPTIONAL para
predicción dinámica de volumen.

## Validación ejecutada

| Gate | Resultado final |
|---|---|
| Checker pedagógico | PED-CHECK-01…09, L1–L15: green. |
| Fixtures positivos/negativos | Futuro, ruptura de API, REQUIRED→OPTIONAL, referencia inexistente, assessment OPTIONAL y eliminación de introducción detectados; recall válido y curso real pasan. |
| Reportes generados | `pedagogy_reports.py --check`: diff cero. |
| Ejercicios | 293 ejercicios en 14 lessons autovalidados. |
| Tests Python | 117 passed. |
| Motor | Smoke end-to-end: green. |
| Scripts consolidados | 16/16, L1–L14: green; capstone 90.2/100. |
| Regeneración | Curso + examen (40 preguntas) regenerados; `git diff --exit-code`: green. |
| E2E documental | L1–L14 estudio/aula/mobile, simuladores y L15 lineal: green. |
| Desktop | 115 checks, 0 fallos, cada lesson L1–L14 y cada estado LIVE. |
| Pages estático | 54 HTML, 29 notebooks y base path: green. |
| JupyterLite offline | L1–L14 abren y ejecutan un smoke Python específico de la lesson en WebKit. |
| Higiene | `git diff --check`: green. |

El test de Pages usa contextos limpios por notebook y espera la señal accesible
`Python (Pyodide) | Idle` antes de ejecutar. Si aun así una celda no produce el
resultado esperado, la repite de forma acotada; si Pyodide emite un error
asíncrono, repite el notebook completo en otro contexto y solo acepta una segunda
ejecución sin errores. No se filtra ni se ignora el error persistente.

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

El audit completo está en
[`desktop-audit.json`](../artifacts/work2-full-course-scaleout/desktop-audit.json)
y registra los 115 checks con lesson, viewport, modo, escena y etapa.

Muestra visual deliberadamente amplia:

- [Hero L1](../artifacts/work2-full-course-scaleout/visual-hero-l1-l01-challenge.png)
- [Recall L2](../artifacts/work2-full-course-scaleout/visual-recall-l2-l02-recall.png)
- [Code-state L7](../artifacts/work2-full-course-scaleout/visual-code-state-l7-l07-build.png)
- [Simulador L8](../artifacts/work2-full-course-scaleout/visual-simulator-l8-l08-simulator.png)
- [Arquitectura L10](../artifacts/work2-full-course-scaleout/visual-architecture-l10-l10-contract.png)
- [Quiz L11](../artifacts/work2-full-course-scaleout/visual-quiz-l11-l11-quiz.png)
- [Bridge L13](../artifacts/work2-full-course-scaleout/visual-bridge-l13-l13-bridge.png)
- [Escena matemática L14](../artifacts/work2-full-course-scaleout/visual-mathematical-l14-l14-formulas.png)
- [Fixture negativa de overflow](../artifacts/work2-full-course-scaleout/fixture-intermediate-overflow-detected.png)

La revisión cualitativa recorrió la narrativa L1→L15 y revisó las ocho formas
visuales. Además se operaron en navegador el simulador real de L8 y el notebook
JupyterLite de L14. No se observan clipping sistemático, controles perdidos ni un
salto conceptual pendiente conocido.

## Deuda, riesgos y discrepancias con Work 1

### Deuda técnica

- El repositorio sigue siendo único y el generador sigue cubriendo muchos
  artefactos, decisión deliberada para no introducir la topología futura en este
  Work.
- El arranque frío de Pyodide puede ser lento o emitir un error transitorio; el
  gate exige una ejecución limpia y mantiene el fallo si se reproduce.
- La ejecución remota de GitHub Actions queda pendiente de push/PR; su equivalente
  local completo está verde.

### Deuda pedagógica

- **Bloqueante:** falta dry-run docente humana, cronometrada y con proyector real.
- L1–L9 tienen cargas REQUIRED autónomas apreciables; están explicitadas, pero la
  dry-run debe confirmar ritmo, fatiga y expectativa real del alumnado.
- L14 tiene 125 min REQUIRED por diseño (35 min de ejercicios + capstone de 90);
  debe comunicarse como proyecto separado y validarse con alumnos reales.

### Discrepancias con Work 1

- Work 1 dejó varias lessons con tiers legacy; Work 2 las sustituye por decisiones
  explícitas sin cambiar la taxonomía ni el runtime aprobado.
- Work 1 auditó cuatro pilotos; Work 2 extiende la geometría y navegación a todas
  las lessons y mantiene L7–L9 como oráculo conceptual.
- La deuda de cronometraje que Work 1 aceptó temporalmente no se ha podido cerrar
  sin participación humana. En lugar de ocultarla, este informe convierte el
  veredicto docente en NO-GO.
- No hay discrepancia arquitectónica material: se conservan source of truth,
  modos, fallback, progreso, layouts, JupyterLite y Pages.

## Recomendación final

**GO técnico local / GO para PR:** la rama cumple los criterios automatizables de
Work 2 y está lista para revisión y CI remota. **NO-GO de merge** hasta que GitHub
Actions confirme la misma matriz en remoto.

**NO-GO docente:** no debe etiquetarse todavía como baseline docente V2. Para
cambiar el veredicto a GO, el owner debe ejecutar y registrar el protocolo de
[`work2-teaching-dry-run.md`](work2-teaching-dry-run.md), empezando por L1, L8,
L10 y L14, corregir cualquier desviación y repetir la lesson afectada.
