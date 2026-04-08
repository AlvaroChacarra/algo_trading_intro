# Clase 5 — Tipos de Ordenes y Matching Behavior

## Objetivo
Entender como se envian y se cruzan ordenes en un mercado electronico, y por que la eleccion del tipo de orden cambia el coste, la probabilidad de ejecucion y el riesgo.

## Pregunta central
"El LOB es la subasta. Una orden es tu participacion en ella. ¿Como participas?"

## Estructura de la sesion

| Fase | Duracion | Contenido |
|---|---|---|
| Presentacion | 20 min | Tipos de ordenes, simulador de matching, trade-off coste/probabilidad |
| Notebook | 15 min | MatchingEngine en Python, fills, slippage, IOC, FOK |
| Ejercicios | Restante + casa | 10 ejercicios en 3 tiers |

## Conceptos clave
- **Market order:** ejecucion garantizada, precio incierto (taker — paga el spread)
- **Limit order:** precio garantizado, ejecucion incierta (maker — cobra el spread)
- **IOC (Immediate or Cancel):** ejecuta lo que pueda, cancela el residuo
- **FOK (Fill or Kill):** ejecuta todo o no ejecuta nada
- **Slippage:** diferencia entre el precio esperado y el precio medio de ejecucion
- **FIFO:** las ordenes al mismo precio se ejecutan por orden de llegada

## Referencia rapida

```python
import pandas as pd

df = pd.read_csv("../04-market-microstructure-btc/data/btc_lob_snapshots.csv")
row = df.iloc[0]

# Construir el motor de matching
engine = MatchingEngine(row)

# Market buy de 0.5 BTC
result = engine.market_buy(0.5)
print(f"fills: {result['fills']}")
print(f"avg_price: {result['avg_price']:.2f}")
print(f"slippage: {result['slippage']:.4f}")
```

## Datos
Reutiliza `../04-market-microstructure-btc/data/btc_lob_snapshots.csv` — los mismos 500 snapshots de L4. No se generan datos nuevos.

## Continuidad
- **Desde L4:** conoces el LOB como estructura (bids, asks, spread, imbalance) → ahora lo pones en movimiento
- **Hacia L6:** entiendes como se ejecutan las ordenes → ahora puedes modelizar variables del libro con ciencia de datos
