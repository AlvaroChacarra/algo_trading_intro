# Clase 11 — Primera estrategia + métricas (guía de implementación)

Pieza del framework: **medir una estrategia contra un benchmark**.

## Teoría que cubre

Una estrategia de verdad necesita una **señal** y una **métrica honesta**. La señal aquí es
el imbalance: largo cuando el libro empuja arriba, corto cuando empuja abajo.

Medir bien exige separar dos benchmarks. El **parent arrival** es el mid del primer snapshot y
evalúa la decisión completa de empezar a operar. El **decision mid** de cada orden hija evalúa
solo su ejecución: comprar por encima o vender por debajo de ese mid produce slippage adverso.
No se mezclan ambas preguntas. Y cuidado con el **riesgo escondido**: un equity positivo con un
inventario enorme no es una buena estrategia, sino una apuesta direccional disfrazada.

## Implementación técnica

Subclase de `Strategy` parametrizada por umbral, usando `book.imbalance(3)`. La ruta
LIVE lee `final_equity`, `final_position` y `n_fills` de `BacktestResult`; el juez de slippage
usa el decision mid vigente cuando nace cada orden hija. La ruta REQUIRED consolida cálculos e
interpretación; dibujar `equity_curve` con matplotlib queda **OPTIONAL** y no se evalúa.
Comparar umbrales (más bajo = más operaciones = más inventario) cierra el bloque L1–L10: L10
aportó el contrato y el runner que aquí se someten a métricas honestas.

## Presentación (3 bloques)

1. **Una estrategia con criterio** — Compra cuando el libro empuja arriba (imbalance positivo), vende cuando empuja abajo. Simple, pero ya es una decisión basada en microestructura.
2. **Dos llegadas, dos preguntas** — El parent arrival es el primer mid y evalúa la decisión completa. Cada orden hija tiene su propio decision mid y mide solo su ejecución. No se mezclan.
3. **Leer el resultado con honestidad** — final_equity, posición final, número de fills. Un equity positivo con inventario enorme no es una buena estrategia: es riesgo escondido.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `11_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El snapshot de `exchange/` declara exactamente la superficie disponible en L11. La lección construye su pieza sobre esa superficie; el snapshot siguiente conserva el estado acumulado sin presuponer que cada clase añada un módulo nuevo.
