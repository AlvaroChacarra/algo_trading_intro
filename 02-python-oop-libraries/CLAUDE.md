# Lesson 02 — Python OOP + Libraries

## Purpose
40-minute class extending Lesson 1. Introduces libraries (pandas briefly) and OOP (Order, Trade, PositionTracker). The central question: "what happens when your flat script needs to handle ETH and SOL too?"

## File structure
```
02-python-oop-libraries/
├── README.md                               # Objectives and quick reference
├── lesson.ipynb                            # Main teaching notebook (10 cells + solution)
├── presentation/
│   ├── python-oop-libraries-interactive.html  # 3-block interactive presentation (GSAP)
│   └── guion.md                               # Instructor script (3 blocks, ~130 lines)
├── exercises/
│   ├── oop_trading_system_exercises.ipynb     # 10 exercises + bonus (Exercise 10b)
│   └── portfolio_architecture_demo/           # Standalone Python package (optional demo)
│       ├── run_demo.py                        # CLI entrypoint
│       ├── README.md                          # Architecture doc + ownership table
│       ├── teaching_notes.md                  # Instructor guide (debugging by ownership)
│       ├── portfolio-architecture-interactive.html
│       └── portfolio_app/
│           ├── __init__.py
│           ├── app.py                         # PortfolioOptimizerApp (orchestrator)
│           ├── universe.py                    # AssetUniverse (17 tickers, 4 categories)
│           ├── selector.py                    # UnderlyingSelector (validates user input)
│           ├── data_provider.py               # YahooFinanceDataProvider (mock, no internet)
│           ├── model.py                       # PortfolioOptimizerModel (score = return/vol)
│           └── exceptions.py                  # SelectionError, DataRetrievalError, ModelComputationError
└── assets/                                    # Empty
```

## Lesson flow
1. `presentation/python-oop-libraries-interactive.html` — 20-min presentation: 3 blocks
2. `lesson.ipynb` — starts with the flat-script problem, then builds Order / Trade / PositionTracker
3. `exercises/oop_trading_system_exercises.ipynb` — 10 steps + bonus (MultiAssetTracker)
4. `portfolio_architecture_demo/` — optional extended demo on modular architecture

## Key design decisions

### Presentation (3 blocks, 20 minutes)
| Block | Content | Interaction |
|---|---|---|
| 1. El problema de escalar (5 min) | Script plano vs OOP: 1→2→3 activos | Interactive comparison with metrics (vars, objects, duplication) |
| 2. Dict → Class → Object (5 min) | Transformation from L1 dict to class to instance | Tabbed code view + SVG diagram with highlights |
| 3. Playground (7 min) | Order/Trade/PositionTracker in action | Form inputs → buy/sell/sequence → live cash/position/equity |

Tech stack: GSAP (animations), vanilla JS. Same dark theme as L1 (#09090b + cyan). Consistent nav, progress bar, keyboard shortcuts.

### lesson.ipynb
Opens with a motivating cell: explicitly references L1 Exercise 9 (flat cash/position tracking) and shows the same code with prefixed variables for ETH. Then builds:

1. `import pandas as pd` → DataFrame with 3 orders → `.notional` column → `.groupby("side")`
2. `class Order` → `__init__`, `notional()`, `describe()`, `__repr__`
3. `class Trade` → `cash_flow()` (buy = negative, sell = positive)
4. `class PositionTracker` → `_cash`, `_position` (private, underscore prefix), `apply_trade()`, `equity(mark_price)`
5. Mini story: 3 orders + 3 fills → equity calculation

Encapsulation is named explicitly after building PositionTracker, not before.
Closing references vibe coding as bridge to Lesson 3.

### exercises/oop_trading_system_exercises.ipynb
Exercise 0 is an **active** exercise: student uncomments ETH code and tries to scale the flat script. Not just reading — doing.

| Tier | Exercises | Content |
|---|---|---|
| Núcleo | 1–5 | pandas import, DataFrame, notional column, Order class structure |
| Si vamos bien | 6–7 | Order methods (notional, describe), Trade class |
| Bonus / casa | 8–10b | PositionTracker with private state, apply_trade, equity, MultiAssetTracker |

Experiential callbacks from L1 (not just textual):
- Exercise 4: shows the L1 dict inline, then asks "convert keys to attributes"
- Exercise 6: references `compute_notional()` from L1 Ex6 → now `Order.notional()`
- Exercise 8: references flat cash/position from L1 Ex9 → now `PositionTracker`

Exercise 10b (MultiAssetTracker) teaches composition: `{symbol: PositionTracker}`.

Closing plants concrete vibe coding seed: "you wrote ~60 lines of classes. What if you could describe what you want in Spanish and an LLM generates them?"

### portfolio_architecture_demo/ (optional extended demo)
Self-contained Python package. No external dependencies. No internet. Teaches debugging by ownership.

Run with: `python run_demo.py --scenario <name>`

| Scenario | What fails | Owner |
|---|---|---|
| `happy` | Nothing | — |
| `data_fail` | NVDA causes DataRetrievalError (simulated timeout) | `data_provider.py` |
| `bad_selection` | FAKE ticker causes SelectionError | `selector.py` |
| `model_fail` | Negative returns → ModelComputationError | `model.py` |
| `interactive` | User picks tickers | — |

## Continuity

### From Lesson 1
- `symbol` in all dicts → `Order.__init__` first parameter
- `compute_notional(price, size)` → `Order.notional()` method
- Exercise 9 flat tracking → `PositionTracker.apply_trade()`
- Mixed-asset buy_volume problem → motivates OOP

### To Lesson 3
- "You wrote ~60 lines by hand. What if an LLM generates them?"
- Bridge plants vibe coding concept concretely

## Conventions
- Solutions embedded in exercise notebook — no separate `solutions/` folder
- Private state uses `_underscore` prefix (not `__dunder`); convention explained in notebook
- pandas is introduced briefly (one cell for table, one for notional + groupby) — not the focus
- portfolio_architecture_demo is entirely optional; it does not replace the main exercise path
- All examples use BTCUSDT or ETHUSDT — consistent with Lesson 1's market context
