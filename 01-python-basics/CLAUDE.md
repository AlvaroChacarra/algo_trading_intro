# Lesson 01 — Python Basics for Traders

## Purpose
40-minute intro class for absolute beginners. Core idea: Python is executable text, not magic. Zero theory before running code.

## File structure
```
01-python-basics/
├── README.md                          # Objectives and quick reference
├── lesson.ipynb                       # Main teaching notebook (9 cells + in-class exercise)
├── presentation/
│   ├── python-intro-interactive.html  # Visual intro (scroll-snap, dark theme)
│   └── guion.md                       # Instructor script (464 lines, 7 slides)
├── exercises/
│   └── trading_system_exercises.ipynb # 10 exercises with automated validators
├── assets/                            # Empty — no visuals needed
└── data/                              # Empty — all data is inline
```

## Lesson flow
1. `presentation/python-intro-interactive.html` — sets mental model (what is Python, what is CPython, tokenization → AST → bytecode → VM)
2. `lesson.ipynb` — builds from variables to a mini trading system live in class
3. `exercises/trading_system_exercises.ipynb` — guided practice with 10 exercises

## Key design decisions

### lesson.ipynb
- All examples use BTCUSDT (bid=99950, ask=100000) — market context from cell 1
- Linear progression: variables → types → lists → dicts → `for` → `if` → functions → mini system
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

Exercise 10 ends with a motivating question: "if you wanted to add ETH, how many places would you need to change?" — natural bridge to Lesson 2 (classes).

### presentation/python-intro-interactive.html
- Dark theme: background `#09090b`, accent `#22d3ee` (cyan)
- Scroll-snap navigation, fullscreen button, progress bar
- Fonts: Inter (body) + JetBrains Mono (code)
- Pure HTML/CSS/JS — no p5.js (p5.js is for simulation-heavy classes later)

## Conventions
- Solutions embedded in exercise notebook — no separate `solutions/` folder
- All trading data is inline synthetic — no CSV files, no external APIs
- Every concept is anchored to market terms: variables → bid/ask, dicts → orders, loops → trade processing
- Validation cells use `abs(x - expected) < 1e-9` for float comparisons
