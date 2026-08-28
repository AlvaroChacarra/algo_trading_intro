# Clase 11 — Primera estrategia + métricas

> Someter el motor completo de L1–L10 a una estrategia con señal real y métricas honestas — PnL, posición, parent arrival para la decisión y decision mid para la ejecución de cada orden hija. Checkpoint integrador que depende directamente del contrato y el runner de L10.

## Contexto teórico

Una estrategia de verdad necesita una **señal** y una **métrica honesta**. La señal aquí es
el imbalance: largo cuando el libro empuja arriba, corto cuando empuja abajo.

Medir bien exige separar dos benchmarks. El **parent arrival** es el mid del primer snapshot y
evalúa la decisión completa de empezar a operar. El **decision mid** de cada orden hija evalúa
solo su ejecución: comprar por encima o vender por debajo de ese mid produce slippage adverso.
No se mezclan ambas preguntas. Y cuidado con el **riesgo escondido**: un equity positivo con un
inventario enorme no es una buena estrategia, sino una apuesta direccional disfrazada.

## Qué construyes hoy

**medir una estrategia contra un benchmark**

Subclase de `Strategy` parametrizada por umbral, usando `book.imbalance(3)`. La ruta
LIVE lee `final_equity`, `final_position` y `n_fills` de `BacktestResult`; el juez de slippage
usa el decision mid vigente cuando nace cada orden hija. La ruta REQUIRED consolida cálculos e
interpretación; dibujar `equity_curve` con matplotlib queda **OPTIONAL** y no se evalúa.
Comparar umbrales (más bajo = más operaciones = más inventario) cierra el bloque L1–L10: L10
aportó el contrato y el runner que aquí se someten a métricas honestas.

## Ejercicios de construcción

- **1. Estrategia de imbalance** — señal larga/corta
- **2. Mídela** — leer BacktestResult
- **3. Parent arrival** — primer mid de la decisión completa
- **4. Riesgo escondido** — interpretar inventario

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/11_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/11_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Sin benchmark no hay estrategia: parent arrival juzga la decisión; cada decision mid juzga su ejecución.
