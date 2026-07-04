# Clase 7 — Microestructura — Leer el libro

> Cargar 500 snapshots reales de BTCUSDT y leer el mercado: spread, mid, imbalance, microprice y profundidad. El OrderBook deja de ser una foto y se vuelve una lente.

## Contexto teórico

Microestructura: cómo se forma el precio en el detalle del libro.
- **Spread**: coste implícito de cruzar de un lado a otro.
- **Mid** vs **microprice**: el microprice pondera el mid por el tamaño del lado *contrario*,
  porque el lado con menos tamaño es el que probablemente se mueva — mejor predictor a corto.
- **Imbalance**: presión compradora/vendedora; un imbalance positivo suele preceder subidas.
- **Depth**: cuánto aguanta el libro un golpe (resiliencia).

Distinción importante: la **liquidez visible** del libro es intención, no negociación; puede
cancelarse antes de ejecutarse.

## Qué construyes hoy

**métricas de mercado sobre snapshots reales de BTC**

`book.py` gana las métricas de lectura (`microprice`, `imbalance(levels)`,
`depth(side, levels)`). `market.py` aporta `Market.sample()` — carga 500 snapshots reales de
BTCUSDT empaquetados (`exchange/_data/`) sin configurar rutas — y `OrderBook.from_snapshot`.

A partir de aquí los ejercicios trabajan sobre datos reales con `Market.sample().step()`. El
paquete acumulado ya incluye el motor de datos completo.

## Ejercicios de construcción

- **1. Carga el mercado** — Market.sample y step
- **2. Spread y mid del primer snapshot** — propiedades del libro
- **3. Imbalance a 1 y 5 niveles** — imbalance(levels)
- **4. Microprice** — microprice
- **5. Profundidad por lado** — depth(side, levels)

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/07_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/07_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> El imbalance y el microprice te dicen hacia dónde empuja el libro antes de que se mueva el mid.
