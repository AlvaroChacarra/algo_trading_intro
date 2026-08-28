# Clase 10 — El framework: Strategy + Backtest (guía de implementación)

Pieza del framework: **interfaz Strategy (ABC) y el runner Backtest**.

## Teoría que cubre

El principio de diseño más importante del curso: **separar la decisión de la ejecución**.
Una estrategia no ejecuta órdenes — las *pide*. Reacciona al libro y devuelve acciones; el
motor decide qué hacer con ellas.

Eso se modela con una **clase base abstracta** (interfaz) y **polimorfismo**: cualquier
subclase de `Strategy` encaja en el mismo runner. Esta ignorancia mutua (la estrategia no sabe
del motor, el motor no sabe de la estrategia concreta) es lo que hace el sistema modular y
permite que el alumno enchufe la suya.

## Implementación técnica

`exchange/strategy.py`: `Strategy(ABC)` con `on_book_update(book) -> list[Action]`
(abstracto), `on_fill`, `on_start/on_end`; acciones `NewOrder` y `Cancel`.
`exchange/backtest.py`: `Backtest(market, strategy)` recorre el mercado, pasa cada libro a la
estrategia, ejecuta sus acciones contra el matching, actualiza el `PositionTracker` y registra
`BacktestResult` (fills, equity_curve, final_equity/position). El **mismo** `run()` sirve para
toda estrategia — el pico arquitectónico del curso.

## Presentación (3 bloques)

1. **La interfaz Strategy** — Una estrategia implementa on_book_update(book) y devuelve una lista de acciones (NewOrder/Cancel). No sabe nada del motor. Esa ignorancia es lo que la hace enchufable.
2. **Acciones, no efectos** — La estrategia no ejecuta órdenes: las pide. Devuelve NewOrder(order). El Backtest decide qué hacer con ellas. Separar decisión de ejecución es la clave del diseño.
3. **El Backtest lo cablea todo** — Recorre el mercado, pasa cada libro a la estrategia, ejecuta sus acciones contra el matching, actualiza el portfolio y mide. El mismo run() para cualquier estrategia.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `10_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
