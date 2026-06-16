# Clase 5 — Microestructura — Leer el libro (guía de implementación)

Pieza del framework: **métricas de mercado sobre snapshots reales de BTC**.

## Teoría que cubre

Microestructura: cómo se forma el precio en el detalle del libro.
- **Spread**: coste implícito de cruzar de un lado a otro.
- **Mid** vs **microprice**: el microprice pondera el mid por el tamaño del lado *contrario*,
  porque el lado con menos tamaño es el que probablemente se mueva — mejor predictor a corto.
- **Imbalance**: presión compradora/vendedora; un imbalance positivo suele preceder subidas.
- **Depth**: cuánto aguanta el libro un golpe (resiliencia).

Distinción importante: la **liquidez visible** del libro es intención, no negociación; puede
cancelarse antes de ejecutarse.

## Implementación técnica

`book.py` gana las métricas de lectura (`microprice`, `imbalance(levels)`,
`depth(side, levels)`). `market.py` aporta `Market.sample()` — carga 500 snapshots reales de
BTCUSDT empaquetados (`exchange/_data/`) sin configurar rutas — y `OrderBook.from_snapshot`.

A partir de aquí los ejercicios trabajan sobre datos reales con `Market.sample().step()`. El
paquete acumulado ya incluye el motor de datos completo.

## Presentación (3 bloques)

1. **El libro como lente** — Cargas un snapshot y el OrderBook te da spread y mid en una línea. Pero lo interesante está más adentro: cuánta liquidez hay, y de qué lado.
2. **Imbalance: presión del libro** — Más tamaño en bids que en asks (imbalance > 0) suele preceder subidas de mid. Es una de las señales más usadas en microestructura.
3. **Microprice y profundidad** — El microprice pondera el mid por el tamaño contrario: mejor predictor a corto que el mid simple. La profundidad mide cuánto aguanta el libro un golpe.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `05_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
