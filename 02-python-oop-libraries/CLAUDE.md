# Lesson 02 — Python OOP + Libraries

## Purpose
40-minute class extending Lesson 1. Introduces libraries (pandas briefly) and OOP (Order, Trade, PositionTracker). The central question: "what happens when your flat script needs to handle ETH and SOL too?"

## File structure
```
02-python-oop-libraries/
├── README.md                               # Objectives and quick reference
├── lesson.ipynb                            # Main teaching notebook (10 cells + solution)
├── presentation/
│   ├── python-oop-libraries-interactive.html  # Visual intro with live state tabs
│   └── guion.md                               # Instructor script (212 lines, 5 blocks)
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
1. `presentation/python-oop-libraries-interactive.html` — tabs: import → table → dict→class→object → live Order playground
2. `lesson.ipynb` — starts with the flat-script problem, then builds Order / Trade / PositionTracker
3. `exercises/oop_trading_system_exercises.ipynb` — 10 steps + bonus (MultiAssetTracker)
4. `portfolio_architecture_demo/` — optional extended demo on modular architecture

## Key design decisions

### lesson.ipynb
Opens with a motivating cell: a flat BTC script where adding ETH would require duplicating 4+ variables and all logic. Then builds:

1. `import pandas as pd` → DataFrame with 3 orders → `.notional` column → `.groupby("side")`
2. `class Order` → `__init__`, `notional()`, `describe()`, `__repr__`
3. `class Trade` → `cash_flow()` (buy = negative, sell = positive)
4. `class PositionTracker` → `_cash`, `_position` (private, underscore prefix), `apply_trade()`, `equity(mark_price)`
5. Mini story: 3 orders + 3 fills → equity calculation

Encapsulation is named explicitly after building PositionTracker, not before.

### exercises/oop_trading_system_exercises.ipynb
Exercise 0 is a "feel the problem" cell — not a coding exercise, but a motivating anti-pattern with questions (how many variables for ETH? for SOL? how many places change if equity formula changes?).

| Tier | Exercises | Content |
|---|---|---|
| Núcleo | 1–5 | pandas import, DataFrame, notional column, Order class structure |
| Si vamos bien | 6–7 | Order methods (notional, describe), Trade class |
| Bonus / casa | 8–10b | PositionTracker with private state, apply_trade, equity, MultiAssetTracker |

Exercise 10b (MultiAssetTracker) teaches composition: a dict of `{symbol: PositionTracker}`, showing that N assets = N entries, not N duplicated code blocks.

Each exercise follows the same cell pattern as Lesson 1: problem → validation → guided solution.

### portfolio_architecture_demo/ (optional extended demo)
Self-contained Python package. No external dependencies. No internet. Used to teach debugging by ownership — the idea that every error has a natural home in the codebase.

Run with: `python run_demo.py --scenario <name>`

| Scenario | What fails | Owner |
|---|---|---|
| `happy` | Nothing | — |
| `data_fail` | NVDA causes DataRetrievalError (simulated timeout) | `data_provider.py` |
| `bad_selection` | FAKE ticker causes SelectionError | `selector.py` |
| `model_fail` | Negative returns → ModelComputationError | `model.py` |
| `interactive` | User picks tickers | — |

The app catches each exception type separately and prints: error title, owner file, and reasoning ("the data layer failed — no point looking at the model yet").

Teaching message: "when code grows, the question stops being 'does it work?' and becomes 'which piece owns this?'"

### presentation HTML
Interactive tabs: Before/After import, dict→class→object flow, live Order playground (change price/size/mark, click Crear orden / Compra demo / Venta parcial, watch cash/position/equity update in real time).

## Conventions
- Solutions embedded in exercise notebook — no separate `solutions/` folder
- Private state uses `_underscore` prefix (not `__dunder`); convention explained in notebook
- pandas is introduced briefly (one cell for table, one for notional + groupby) — not the focus
- portfolio_architecture_demo is entirely optional; it does not replace the main exercise path
- All examples use BTCUSDT or ETHUSDT — consistent with Lesson 1's market context
