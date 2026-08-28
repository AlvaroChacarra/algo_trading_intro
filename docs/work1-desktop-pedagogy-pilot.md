# Work 1 — Desktop Learning Runtime + Pedagogical Contract Pilot

## Estado y alcance

Rama: `v2/desktop-learning-runtime-pilot`

Baseline auditado y HEAD de `main` al iniciar: `947a82b4906fe91b2d187ef4b864e8570abde457`.

`main` no había avanzado respecto del baseline. No hubo que reconciliar commits ni
se realizó ningún reset. El piloto migra L1, L8, L10 y L14; usa L7 como fixture de
comparación y mantiene L15 como assessment lineal. No migra la topología
private/public ni reordena las lessons.

Las fuentes rectoras son, por este orden y dominio, `AGENTS.md`,
`CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md` y `ARCHITECTURE.md`.

## Decisiones

### Un contenido, dos recorridos

El HTML generado sigue teniendo una sola fuente. `docgen.py` embebe el contrato de
la lesson y `learning_runtime.js` interpreta sus escenas:

- `?mode=aula`: solo LIVE por defecto, una escena activa, etapas y navegación por
  teclado; el `body` no hace scroll en desktop.
- `?mode=estudio`: recorrido vertical con navegación lateral, REQUIRED incluido y
  OPTIONAL visible e identificado.
- `?mode=aula&profe=1`: añade una guía docente de escena —y el guion detallado
  cuando existe— y permite alternar LIVE,
  LIVE+REQUIRED y todo el contenido.
- En pantallas de hasta 900 px, incluso si se solicita aula, se usa el renderer
  vertical de estudio. No se fuerza el layout multicolumna.

La posición se persiste en `localStorage` como `scene` + `stage` + alcance de ruta.
El progreso de aula no se calcula a partir del porcentaje de scroll.

### Escenas semánticas

El conjunto de tipos es pequeño y cerrado en `pedagogy/course_graph.yml`:
`hero-challenge`, `recall`, `concept-simulator`, `code-state`,
`architecture-map`, `guided-exercise`, `recap`, `bridge` y
`diagnostic-quiz`.

Una escena enlaza metadatos pedagógicos con un nodo existente del body mediante
`dom_id`. Una etapa puede enlazar un paso de scrollytelling mediante `dom_stage`.
Esto permite reutilizar el contenido existente sin duplicar una versión para aula.

### Rutas inequívocas

- **LIVE**: núcleo que se imparte en clase.
- **REQUIRED**: consolidación autónoma obligatoria y potencialmente evaluable.
- **OPTIONAL**: profundización no obligatoria; ningún assessment oficial puede
  depender exclusivamente de ella.

Las rutas de ejercicios piloto viven en `pedagogy/exercise_routes.yml`. Son
decisiones explícitas por título, con tiempo; el generador falla si falta o sobra un
ejercicio. El checker suma todos los ejercicios LIVE y exige 18–22 minutos de
práctica guiada, con una desviación máxima de dos minutos respecto a
`guided_minutes`. La selección queda en 19 minutos para L1, L7 y L8; 20 para L5;
y 21 para L10 y L14. L2, L3, L4, L6, L9 y L11–L13 conservan temporalmente sus
tiers legacy y deben recibir una decisión explícita en Work 2.

### Continuidad de APIs

La API de lectura de `OrderBook` queda estabilizada desde L5:

- `best_bid`, `best_ask`, `spread` y `mid` son propiedades sin argumentos;
- `imbalance(levels=1)` sigue siendo método porque acepta una decisión del alumno;
- presentación, ejercicios, demo, paquete acumulativo y tests usan la misma forma.

L10 contiene un puente visible desde la Strategy pedagógica de L6:
`decide(imbalance) -> str` se transforma en
`on_book_update(book) -> list[Action]`. El puente declara qué se conserva, cómo
cambian input/output y por qué la decisión deja de ejecutar efectos.

L14 concentra LIVE en reservation price, optimal spread, los parámetros
`q`, `γ`, `σ`, `τ`, `κ` y el laboratorio. El capstone es REQUIRED autónomo y
está separado del examen final de L15.

## Contrato machine-readable

Los `.yml` son deliberadamente JSON compatible. Así CI los valida con la librería
estándar de Python, sin incorporar un parser adicional.

```text
pedagogy/
├── course_graph.yml
├── exercise_routes.yml
├── assessment_blueprint.yml
└── lessons/01.yml … 15.yml
```

Cada lesson declara `requires`, `introduces`, `recalls`, `api_surface`, `routes`,
`objectives`, `load`, `scenes` y, cuando procede, `api_transitions` y
`package_checks`. Estos últimos vinculan una API material con el archivo y clase
reales del starter, además de su tipo (`method`, `property` o `classmethod`),
argumentos, anotaciones, defaults y retorno. La cobertura estricta incluye
`MatchingEngine.process`, `Strategy.on_book_update`, `Strategy.on_fill` y
`Backtest.run`, junto con sus prerrequisitos acumulativos.

Ejemplo de dependencia y recuperación:

```json
{
  "requires": {"concepts": ["oop.polymorphism"], "apis": ["toy_strategy.decide"]},
  "recalls": [{
    "concept": "oop.polymorphism",
    "introduced_in": 6,
    "mapping": {
      "before": "decide(imbalance) -> str",
      "now": "on_book_update(book) -> list[Action]"
    }
  }]
}
```

`assessment_blueprint.yml` solo demuestra metadatos. Los enunciados y respuestas
oficiales permanecen fuera de este contrato público. Cada item piloto mapea lesson,
objetivo, concepto, nivel cognitivo y dificultad.

## Cómo añadir una escena

1. Crear o reutilizar una sección con `id` estable en
   `framework/_build/docs/NN_body.html`.
2. Añadir la escena a `pedagogy/lessons/NN.yml`, con `id`, `dom_id`, `type`,
   `route`, `layout`, `concepts`, `duration_minutes` y `stages`.
3. Incluir el `id` exactamente una vez en `routes.LIVE`, `routes.REQUIRED` o
   `routes.OPTIONAL`.
4. Si enlaza un scrollytelling, declarar cada `dom_stage` que ya existe en el body.
5. Regenerar y ejecutar el checker y la matriz desktop.

Ejemplo:

```json
{
  "id": "l08-plan-validate-commit",
  "dom_id": "s1",
  "type": "code-state",
  "route": "LIVE",
  "layout": "split-42-58",
  "concepts": ["matching.plan_validate_commit", "matching.atomicity"],
  "duration_minutes": 11,
  "stages": [
    {"id": "plan", "dom_stage": 5, "route": "LIVE"},
    {"id": "validate", "dom_stage": 6, "route": "LIVE"},
    {"id": "commit", "dom_stage": 7, "route": "LIVE"}
  ]
}
```

## Cómo migrar una lesson

1. Auditar lo que realmente exigen sus cuerpos, ejercicios, paquete acumulativo y
   assessments.
2. Completar conceptos y APIs requeridos/introducidos sin alterar el orden L1–L15.
3. Declarar recuperaciones distantes y transiciones de API; nunca encubrir una
   ruptura cambiando solo el código final.
4. Diseñar LIVE para 18–22 minutos por densidad cognitiva, no por número de
   pantallas, y declarar por separado carga guiada, requerida y opcional. La suma
   de todos los ejercicios LIVE debe caber también en 18–22 minutos; lo que no
   quepa se decide como REQUIRED u OPTIONAL, nunca como desbordamiento implícito.
5. Clasificar cada escena y cada ejercicio. No derivar la ruta de la posición.
6. Regenerar los outputs; nunca editar a mano notebooks o HTML generados.
7. Ejecutar `python pedagogy_check.py`, pytest, smoke, build check, E2E general,
   matriz desktop y WebKit/Pages.

## Checker y acceptance

`pedagogy_check.py` implementa PED-CHECK-01…09: uso antes de introducción,
superficies de API, referencias/anchors vigentes, recalls distantes, clasificación,
restricciones de assessment, metadata de preguntas, carga y consistencia del
starter acumulativo. Los tests introducen regresiones sintéticas de sobrecarga,
tiempo ausente, doble clasificación, property → method y divergencias de
argumentos, tipos, defaults o retornos en los starters de L8/L10.

`desktop_e2e.js` valida L1, L8, L10 y L14 en 1280×720, 1440×900, 1920×1080 y
2560×1440. Después de cada transición registra lesson, viewport, alcance, escena
y etapa; comprueba geometría, controles, contenido esencial, ausencia de scroll
del body, overflow, foco, Escape, persistencia y errores JS. Una fixture inyecta
overflow únicamente en una etapa intermedia de L8 y exige que el detector la
rechace. La matriz recorre también LIVE+REQUIRED a 1440×900, y repite estudio,
reduced motion y fallback 390×844 en los cuatro pilotos. El estado exacto que
falle conserva screenshot; el JSON completo queda en el artefacto
`work1-desktop-pedagogy-pilot`. L15 sigue validándose como assessment lineal.

El workflow de Pages también valida cada push `v2/**`: construye el site con
JupyterLite, comprueba enlaces/base path y ejecuta el fallback móvil en WebKit.
Solo `main` puede llegar al job de despliegue.

## Limitaciones conocidas

- El contrato de L2, L3, L4, L6, L9 y L11–L13 es un esqueleto de continuidad, no
  una migración editorial completa.
- Solo las lessons piloto, L5 y el fixture L7 tienen rutas explícitas de ejercicios.
- Los layouts reutilizan la semántica y componentes del documento actual. Work 2
  puede añadir uno o dos layouts si una lesson demuestra una necesidad real; no
  debe crear un framework genérico por anticipado.
- El modo aula permite overflow interno en paneles de detalle, pero no scroll del
  body. La información esencial y los controles permanecen dentro del viewport.
- El estado actual sigue siendo un repositorio único, tal como exige el alcance.
- La dry-run humana todavía no puede deducirse de CI. Su protocolo y registro
  versionado viven en [`work1-teaching-dry-run.md`](work1-teaching-dry-run.md) y
  permanecen pendientes hasta que el docente mida las cuatro lessons.

## Gate para Work 2

Escalar solo si CI mantiene verdes el checker, generación, motor, Pages/WebKit y
la matriz desktop; si las cuatro formas piloto y L15 resultan utilizables; y si una
prueba de impartición confirma que las rutas LIVE caben en 18–22 minutos sin ocultar
prerrequisitos. La dry-run debe registrar también una práctica guiada próxima a
20 minutos y una decisión `PASS` por lesson. Después se requiere reauditar el PR,
mergear Work 1 y registrar el SHA de merge antes de crear la rama de Work 2.
Work 2 debe migrar las lessons legacy de forma incremental y conservar L7–L9
como oráculo conceptual.
