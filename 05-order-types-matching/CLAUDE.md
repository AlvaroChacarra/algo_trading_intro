# Lesson 05 — Tipos de Ordenes y Matching Behavior

## Purpose
40-minute class teaching how orders interact with the LOB. The central question: "the LOB is the auction. An order is your participation in it. How do you participate?"

Direct continuation from L4: students already understand the LOB as a structure (bids, asks, spread, imbalance). Now they put it in motion.

## File structure
```
05-order-types-matching/
├── README.md                                    # Objectives and quick reference
├── CLAUDE.md                                    # This file
├── lesson.ipynb                                 # Main teaching notebook (~14 cells)
├── presentation/
│   ├── order-types-interactive.html             # 3-block interactive presentation (GSAP + p5.js)
│   └── guion.md                                 # Instructor script (3 blocks, ~130 lines)
├── exercises/
│   └── order_types_exercises.ipynb              # 10 exercises + tier system
├── data/                                        # Empty — reuses L4 CSV
└── assets/                                      # Empty
```

## Lesson flow
1. `presentation/order-types-interactive.html` — 20-min presentation: 3 blocks
2. `lesson.ipynb` — build a MatchingEngine in Python using L4 data, simulate fills
3. `exercises/order_types_exercises.ipynb` — 10 exercises with validators

## Data
No new data. All exercises and the notebook use:
`../04-market-microstructure-btc/data/btc_lob_snapshots.csv`

This is intentional continuity: "the same LOB you analyzed in L4, now you send orders into it."

## Key design decisions

### Presentation (3 blocks, 20 minutes)
| Block | Content | Interaction |
|---|---|---|
| 1. Tipos de ordenes (6 min) | Market vs Limit vs IOC/FOK — the 3 fundamental types | 3-column comparison cards with use-case examples |
| 2. Simulador de matching (8 min) | Interactive LOB with p5.js — place/cancel limit orders, send market/IOC/FOK orders, see fills | Full p5.js canvas with animated fill consumption, fill log |
| 3. Coste y trade-off (5 min) | Market = taker (pays spread), Limit = maker (earns spread) but execution risk | Slider showing cost vs size; execution probability intuition |

Tech stack: GSAP 3.12.5 (scroll/nav) + **p5.js 1.9.4** (simulator canvas) + vanilla JS. Same dark theme as L1-L4 (#09090b + cyan). p5.js is reserved for simulation-heavy classes per PLAN_MAESTRO.

### lesson.ipynb
Opens with bridge from L4: "En L4 calculaste spread, imbalance, weighted mid. Hoy vas a interactuar con ese mismo libro."

Uses `../04-market-microstructure-btc/data/btc_lob_snapshots.csv` — same row = same LOB students analyzed.

1. Extract snapshot 0 as bid/ask lists of dicts [{price, size, id}]
2. `MatchingEngine` class: init from snapshot row, `__repr__`
3. `market_buy(size)` — walk asks, collect fills, compute avg_price + slippage
4. Visualize filled levels (horizontal bars, consumed in red)
5. `market_sell(size)` — walk bids (symmetric)
6. `place_limit(side, price, size)` — insert at correct position, check for crossing
7. `cancel(order_id)` — remove by id
8. IOC: market order + cancel residual if not fully filled
9. FOK: check available liquidity before executing; all or nothing
10. Cost comparison: market vs limit for same trade
11. Student exercise: `simulate_sequence(engine, orders)` processes a list of mixed orders
12. Solution

### exercises/order_types_exercises.ipynb
| Tier | Exercises | Content |
|---|---|---|
| Nucleo | 0–5 | Ex0 motivacional (reflexion), load LOB from L4 CSV, market_buy, slippage, market_sell, place_limit |
| Si vamos bien | 6–7 | IOC implementation, FOK implementation |
| Bonus / casa | 8–10 | Cost comparison, sequence simulation, maker/taker fee model |

Continuity callbacks from L4:
- Ex0: displays LOB snapshot 0 (same data, now as a matching target)
- Ex1–5: use `df.iloc[0]` to extract bids/asks — students recognize the format
- Validators follow exact same pattern: `globals()` check + specific error messages + "Bien:" prefix

## Continuity

### From Lesson 4
- "En L4 visteis el LOB desde fuera. Hoy lo poneis en movimiento."
- Same data: `btc_lob_snapshots.csv`, same `{bid_price_1..10, bid_size_1..10}` format
- Same color palette: bid=#4ade80, ask=#f87171, cyan=#22d3ee
- Same LOB data structure in JS: `[{price, size}]` arrays

### To Lesson 6
- "Ahora que entendeis como se ejecutan las ordenes, en L6 vais a modelizar variables del libro."
- Fill probability (will this limit order execute?) is a natural L6 target variable
- Imbalance as feature input to predict fill probability

## Conventions
- Solutions embedded in exercise notebook — no separate `solutions/` folder
- MatchingEngine uses FIFO price-time priority (no pro-rata, no hidden orders)
- IOC yes, FOK yes, venue logic no (time constraint)
- p5.js canvas in Block 2 uses `noLoop()` + `redraw()` pattern — no continuous animation loop
- All examples use BTCUSDT context (same as L1-L4)
- matplotlib for notebook visualizations (not plotly)
