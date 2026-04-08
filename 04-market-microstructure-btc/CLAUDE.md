# Lesson 04 — Microestructura de Mercado (BTC)

## Purpose
40-minute class introducing market microstructure through the Limit Order Book. The central question: "the price you see is not a fact — it's the result of a continuous auction. The LOB is that auction."

First contact with real (synthetic but realistic) market data. Everything after this lesson (order types L5, data science L6-L7, VWAP L8-L9, market making L12-L13) builds on understanding the LOB.

## File structure
```
04-market-microstructure-btc/
├── README.md                               # Objectives and quick reference
├── CLAUDE.md                               # This file
├── lesson.ipynb                            # Main teaching notebook (~16 cells)
├── presentation/
│   ├── lob-interactive.html                # 3-block interactive presentation (GSAP)
│   └── guion.md                            # Instructor script (3 blocks, ~130 lines)
├── exercises/
│   └── lob_exercises.ipynb                 # 10 exercises + tier system
├── data/
│   └── btc_lob_snapshots.csv               # 500 synthetic LOB snapshots (10 levels/side)
└── assets/                                 # Empty
```

## Lesson flow
1. `presentation/lob-interactive.html` — 20-min presentation: 3 blocks
2. `lesson.ipynb` — load LOB data, compute metrics, visualize, analyze imbalance
3. `exercises/lob_exercises.ipynb` — 10 exercises with validators

## Data
`btc_lob_snapshots.csv`: 500 snapshots of BTCUSDT LOB, ~1 per minute, simulating ~8 hours of market.

| Column pattern | Description |
|---|---|
| `timestamp` | Unix timestamp |
| `bid_price_1..10` | Bid prices, level 1 = best bid (highest) |
| `bid_size_1..10` | Bid sizes in BTC |
| `ask_price_1..10` | Ask prices, level 1 = best ask (lowest) |
| `ask_size_1..10` | Ask sizes in BTC |

Properties:
- Prices around ~$100,000 with realistic spread ($5-$50)
- Sizes 0.01–5.0 BTC per level
- Mean-reverting mid price with occasional jumps
- 5% of snapshots have wide spread events
- Deterministic (seed=42) for reproducibility

## Key design decisions

### Presentation (3 blocks, 20 minutes)
| Block | Content | Interaction |
|---|---|---|
| 1. Que es un LOB (6 min) | Bids/asks, best bid/ask, spread, mid price | Interactive LOB with 10 levels, orders arriving/leaving, live metrics |
| 2. Leer el libro (7 min) | Depth chart, cumulative volume, market order impact | Depth visualization, slider for N levels, "market buy" button eating levels |
| 3. Que nos dice el imbalance (5 min) | Imbalance formula, pressure signal, predictive value | Imbalance gauge, historical imbalance vs price move |

Tech stack: GSAP (animations), vanilla JS. Same dark theme as L1-L3 (#09090b + cyan). No external dependencies.

### lesson.ipynb
Opens with bridge from L3: "You learned to evaluate AI code. Now let's apply it to real market data."

1. Load CSV with pandas, explore shape and columns
2. Extract best bid, best ask, spread, mid price for one snapshot
3. Visualize a single LOB snapshot as horizontal bar chart (bids left, asks right)
4. Cumulative depth chart
5. Imbalance formula and calculation for single snapshot
6. Imbalance time series across all 500 snapshots
7. Spread dynamics over time
8. In-class exercise: weighted mid price (VWAP of top-N levels)

Uses matplotlib for all visualizations (not plotly).

### exercises/lob_exercises.ipynb
| Tier | Exercises | Content |
|---|---|---|
| Nucleo | 1–5 | Load CSV, best bid/ask, spread/mid, bid vs ask volume, imbalance |
| Si vamos bien | 6–7 | Visualize snapshot, imbalance time series |
| Bonus / casa | 8–10 | Depth chart, imbalance vs price change correlation, weighted mid price |

## Continuity

### From Lesson 3
- "You learned to evaluate AI code. Now: real market data."
- pandas skills from L2 are essential here (DataFrame, column operations, groupby)
- try/except from L3 used when loading/validating data

### To Lesson 5
- "You understand the LOB. Next: what happens when you send an order into it?"
- LOB structure → order types and matching behavior
- Imbalance → informs order placement strategy

## Conventions
- Solutions embedded in exercise notebook — no separate `solutions/` folder
- All data is local synthetic CSV — no external API calls
- matplotlib for notebook visualizations (simple, standard)
- HTML presentation uses hardcoded realistic BTC data (not the CSV)
- BTCUSDT context consistent with L1-L3
