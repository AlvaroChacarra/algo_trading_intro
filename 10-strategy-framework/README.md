# Clase 10 — El framework: Strategy + Backtest

> El corazón del curso: una estrategia solo reacciona al libro y devuelve acciones. El Backtest la cablea con el mercado y el portfolio. Cualquier estrategia se enchufa igual.

## Contexto teórico

El principio de diseño más importante del curso: **separar la decisión de la ejecución**.
Una estrategia no ejecuta órdenes — las *pide*. Reacciona al libro y devuelve acciones; el
motor decide qué hacer con ellas.

Eso se modela con una **clase base abstracta** (interfaz) y **polimorfismo**: cualquier
subclase de `Strategy` encaja en el mismo runner. Esta ignorancia mutua (la estrategia no sabe
del motor, el motor no sabe de la estrategia concreta) es lo que hace el sistema modular y
permite que el alumno enchufe la suya.

## Qué construyes hoy

**interfaz Strategy (ABC) y el runner Backtest**

`exchange/strategy.py`: `Strategy(ABC)` con `on_book_update(book) -> list[Action]`
(abstracto), `on_fill`, `on_start/on_end`; acciones `NewOrder` y `Cancel`.
`exchange/backtest.py`: `Backtest(market, strategy)` recorre el mercado, pasa cada libro a la
estrategia, ejecuta sus acciones contra el matching, actualiza el `PositionTracker` y registra
`BacktestResult` (fills, equity_curve, final_equity/position). El **mismo** `run()` sirve para
toda estrategia — el pico arquitectónico del curso.

## Ejercicios de construcción

- **1. Tu primera estrategia** — heredar de Strategy
- **2. Corre el Backtest** — Backtest.run
- **3. Reacciona a tus fills** — el hook on_fill
- **4. Polimorfismo: cambia la estrategia, no el runner** — intercambiar subclases

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/10_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/10_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Escribe una subclase de Strategy y enchúfala al mismo Backtest. Eso es polimorfismo, y es lo que hace todo modular.
