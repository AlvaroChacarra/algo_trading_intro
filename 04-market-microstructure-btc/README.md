# Clase 4 — Microestructura de Mercado (BTC)

## Objetivo
Entender como funciona un Limit Order Book (LOB), calcular metricas basicas de microestructura, y usar el imbalance como senal de presion de mercado.

## Pregunta central
"El precio que ves no es un hecho — es el resultado de una subasta continua. El LOB es esa subasta."

## Estructura de la sesion

| Fase | Duracion | Contenido |
|---|---|---|
| Presentacion | 20 min | LOB visual, profundidad, imbalance |
| Notebook | 15 min | Cargar datos, calcular metricas, visualizar |
| Ejercicios | Restante + casa | 10 ejercicios en 3 tiers |

## Conceptos clave
- **Bid / Ask:** precios de compra y venta
- **Spread:** `ask - bid` (coste implicito de operar)
- **Mid price:** `(bid + ask) / 2`
- **Profundidad:** volumen acumulado por nivel de precio
- **Imbalance:** `bid_vol / (bid_vol + ask_vol)` — presion compradora vs vendedora

## Referencia rapida

```python
import pandas as pd

df = pd.read_csv("data/btc_lob_snapshots.csv")

# Metricas basicas
best_bid = df["bid_price_1"]
best_ask = df["ask_price_1"]
spread = best_ask - best_bid
mid = (best_bid + best_ask) / 2

# Imbalance (top 5 niveles)
bid_vol = sum(df[f"bid_size_{i}"] for i in range(1, 6))
ask_vol = sum(df[f"ask_size_{i}"] for i in range(1, 6))
imbalance = bid_vol / (bid_vol + ask_vol)
```

## Datos
`data/btc_lob_snapshots.csv` — 500 snapshots sinteticos de BTCUSDT, 10 niveles por lado, ~8 horas de mercado simulado.

## Continuidad
- **Desde L3:** Python + OOP + IA → ahora datos reales de mercado
- **Hacia L5:** entiendes el LOB → ahora tipos de ordenes y matching
