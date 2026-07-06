# Clase 11 — Primera estrategia + métricas (guía de implementación)

Pieza del framework: **medir una estrategia contra un benchmark**.

## Teoría que cubre

Una estrategia de verdad necesita una **señal** y una **métrica honesta**. La señal aquí es
el imbalance: largo cuando el libro empuja arriba, corto cuando empuja abajo.

Medir bien exige un **benchmark**: el **mid de llegada** (arrival mid). Tu ejecución es buena
si compraste por debajo (o vendiste por encima) de él — eso es el **slippage**. Y cuidado con
el **riesgo escondido**: un equity positivo acompañado de un inventario enorme no es una buena
estrategia, es una apuesta direccional disfrazada. Por eso se miran a la vez equity, posición
final y número de fills.

## Implementación técnica

Subclase de `Strategy` parametrizada por umbral, usando `book.imbalance(3)`. Lectura
completa de `BacktestResult`: `final_equity`, `final_position`, `n_fills`, `equity_curve`.
Comparación de umbrales (más bajo = más operaciones = más inventario). Cierra el bloque
L1–L9: el motor está completo y se puede medir. Checkpoint integrador.

## Presentación (3 bloques)

1. **Una estrategia con criterio** — Compra cuando el libro empuja arriba (imbalance positivo), vende cuando empuja abajo. Simple, pero ya es una decisión basada en microestructura.
2. **El benchmark: mid de llegada** — El precio justo de referencia es el mid cuando empezaste. Tu ejecución es buena si compraste por debajo (o vendiste por encima) de él.
3. **Leer el resultado con honestidad** — final_equity, posición final, número de fills. Un equity positivo con inventario enorme no es una buena estrategia: es riesgo escondido.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `11_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
