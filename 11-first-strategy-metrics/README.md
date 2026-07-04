# Clase 11 — Primera estrategia + métricas

> Cerrar el motor: una estrategia con señal real, y métricas honestas — PnL, posición y slippage contra el mid de llegada. Checkpoint integrador de todo L1-L9.

## Contexto teórico

Una estrategia de verdad necesita una **señal** y una **métrica honesta**. La señal aquí es
el imbalance: largo cuando el libro empuja arriba, corto cuando empuja abajo.

Medir bien exige un **benchmark**: el **mid de llegada** (arrival mid). Tu ejecución es buena
si compraste por debajo (o vendiste por encima) de él — eso es el **slippage**. Y cuidado con
el **riesgo escondido**: un equity positivo acompañado de un inventario enorme no es una buena
estrategia, es una apuesta direccional disfrazada. Por eso se miran a la vez equity, posición
final y número de fills.

## Qué construyes hoy

**medir una estrategia contra un benchmark**

Subclase de `Strategy` parametrizada por umbral, usando `book.imbalance(3)`. Lectura
completa de `BacktestResult`: `final_equity`, `final_position`, `n_fills`, `equity_curve`.
Comparación de umbrales (más bajo = más operaciones = más inventario). Cierra el bloque
L1–L9: el motor está completo y se puede medir. Checkpoint integrador.

## Ejercicios de construcción

- **1. Estrategia de imbalance** — señal larga/corta
- **2. Mídela** — leer BacktestResult
- **3. Benchmark de llegada** — mid inicial
- **4. Riesgo escondido** — interpretar inventario

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/11_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/11_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Sin benchmark no hay estrategia: medir contra el mid de llegada separa la suerte del valor.
