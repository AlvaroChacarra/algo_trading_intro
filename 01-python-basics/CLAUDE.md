# Lesson 01 — Python Basics for Traders

## Purpose
40-minute intro class for absolute beginners. Core idea: Python is executable text, not magic. Zero theory before running code.

## File structure
```
01-python-basics/
├── README.md                          # Objectives and quick reference
├── lesson.ipynb                       # Main teaching notebook (10 cells + in-class exercise)
├── presentation/
│   ├── python-intro-interactive.html  # 3-block interactive presentation (Pyodide + GSAP)
│   └── guion.md                       # Instructor script (3 blocks, ~130 lines)
├── exercises/
│   └── trading_system_exercises.ipynb # 10 exercises with automated validators
├── assets/                            # Empty — no visuals needed
└── data/                              # Empty — all data is inline
```

## Lesson flow
1. `presentation/python-intro-interactive.html` — 20-min presentation: 3 blocks
2. `lesson.ipynb` — builds from variables to a mini trading system live in class
3. `exercises/trading_system_exercises.ipynb` — guided practice with 10 exercises

## Key design decisions

### Presentation (3 blocks, 20 minutes)
| Block | Content | Interaction |
|---|---|---|
| 1. Tu código es texto (5 min) | Python reads text, produces results | Pyodide REPL: write Python live in browser, snippet buttons |
| 2. Errores como pistas (5 min) | SyntaxError vs runtime errors | 4 interactive break-and-fix challenges with auto-progression |
| 3. Del dato a la decisión (7 min) | Variables → operations → if → decision | Market snapshot + rule builder + code editor |

Tech stack: Pyodide (live Python), GSAP (animations), vanilla JS. Dark theme (#09090b + cyan #22d3ee). No p5.js, no CPython pipeline sections.

### lesson.ipynb
- All examples use BTCUSDT (bid=99950, ask=100000) — market context from cell 1
- Linear progression: variables → types → lists → dicts → `for` → `if` → functions → mini system
- **Mixed-asset moment (cell 7):** orders list includes one ETHUSDT order — `buy_volume` mixes BTC and ETH, surfacing the multi-asset problem. A reflection cell after the solution highlights why this doesn't make sense financially.
- All order dicts carry `symbol` field — this is deliberate for L2 continuity (dict keys → class attributes)
- Last two cells: in-class exercise + guided solution (buy_share, average_size)
- No imports — pure stdlib, zero setup friction

### exercises/trading_system_exercises.ipynb
Three tiers, stated at the top of the notebook:

| Tier | Exercises | When |
|---|---|---|
| Núcleo | 1–5 | Must complete in class |
| Si vamos bien | 6–7 | If pace allows |
| Bonus / casa | 8–10 | Homework or fast finishers |

Each exercise follows this exact cell pattern:
1. Problem statement + starter code with `pass` or `None`
2. Validation cell (auto-checks with descriptive errors, tolerance for floats)
3. Guided solution cell

Exercise 3 requires `symbol` in the order dict — validated by the checker.

Exercise 9 (fill tracking with cash/position/equity) is explicitly referenced in L2 as the starting point for PositionTracker.

Exercise 10 closes with a concrete bridge to L2: references the mixed-asset problem from the lesson notebook and previews `PositionTracker`.

## Continuity with Lesson 2
- `symbol` field in all dicts → becomes first parameter of `Order.__init__`
- `compute_notional(price, size)` function → becomes `Order.notional()` method
- Exercise 9 flat cash/position tracking → becomes `PositionTracker.apply_trade()`
- Mixed-asset observation → motivates OOP composition (MultiAssetTracker)

## Conventions
- Solutions embedded in exercise notebook — no separate `solutions/` folder
- All trading data is inline synthetic — no CSV files, no external APIs
- Every concept is anchored to market terms: variables → bid/ask, dicts → orders, loops → trade processing
- Validation cells use `abs(x - expected) < 1e-9` for float comparisons
