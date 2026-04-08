# Lesson 03 — Vibe Coding, LLMs, Tools y Agentes

## Purpose
40-minute class bridging Python fundamentals (L1–L2) with AI-assisted coding. The central question: "you wrote ~60 lines of classes by hand — what if an LLM generates them from a description in Spanish?"

Teaches new Python patterns (try/except, type hints, @property, comprehensions, decorators) through the lens of evaluating AI-generated code, not as standalone theory.

## File structure
```
03-vibe-coding-llms-tools-agents/
├── README.md                               # Objectives and quick reference
├── CLAUDE.md                               # This file
├── lesson.ipynb                            # Main teaching notebook (~12 cells)
├── presentation/
│   ├── vibe-coding-interactive.html        # 3-block interactive presentation (GSAP)
│   └── guion.md                            # Instructor script (3 blocks, ~130 lines)
├── exercises/
│   └── vibe_coding_exercises.ipynb         # 10 exercises + tier system
├── assets/                                 # Empty
└── data/                                   # Empty
```

## Lesson flow
1. `presentation/vibe-coding-interactive.html` — 20-min presentation: 3 blocks
2. `lesson.ipynb` — bridge from L2, evaluate AI code, learn new Python patterns
3. `exercises/vibe_coding_exercises.ipynb` — 10 steps + tier system

## Key design decisions

### Presentation (3 blocks, 20 minutes)
| Block | Content | Interaction |
|---|---|---|
| 1. Cómo piensa un LLM (7 min) | Token-by-token generation, temperature, stochastic output | Animated token generation + temperature slider → same prompt, different outputs |
| 2. LLM vs Agente (6 min) | Single-shot vs tool-using loop, when each applies | Animated comparison diagram with tools panel, trading agent example |
| 3. Cuándo confiar, cuándo verificar (5 min) | Trust framework: green/yellow/red confidence levels | Traffic-light semaphore with code examples, interactive bug-finding |

Tech stack: GSAP (animations), vanilla JS. Same dark theme as L1/L2 (#09090b + cyan). Consistent nav, progress bar, keyboard shortcuts. No Pyodide needed.

### lesson.ipynb
Opens with explicit bridge from L2: "You wrote Order, Trade, PositionTracker by hand. Now imagine asking an LLM to generate them."

1. Bridge: show L2's PositionTracker, then show "what an LLM might generate" — similar but with type hints, @property, docstrings
2. `try/except` — what happens when AI code crashes? How to catch errors gracefully
3. Type hints — reading AI-generated signatures: `def apply_trade(self, trade: Trade) -> None`
4. `@property` — AI often uses this; understand `tracker.cash` vs `tracker._cash`
5. List comprehensions — AI loves these; transform a for-loop into a one-liner
6. Decorators — `@property` is one; understand the pattern conceptually
7. Putting it together: evaluate a complete AI-generated `EnhancedTracker` class
8. In-class exercise + guided solution

Each cell follows the pattern: "an LLM generated this → what does it do? → try it → now you understand the pattern."

### exercises/vibe_coding_exercises.ipynb
| Tier | Exercises | Content |
|---|---|---|
| Núcleo | 1–5 | try/except basics, type hints, @property, list comprehension, code evaluation |
| Si vamos bien | 6–7 | decorators, dict comprehension |
| Bonus / casa | 8–10 | predict AI output, refactor L2 code with new patterns, generate TradeLogger |

Experiential callbacks from L1–L2:
- Exercise 5: evaluate an AI-generated Order class against L2's version
- Exercise 9: refactor L2's PositionTracker with type hints + @property
- Exercise 10: describe a TradeLogger in Spanish, then build it

## Continuity

### From Lesson 2
- "Has escrito ~60 líneas de clases a mano" → bridge opens the notebook
- L2's Order/Trade/PositionTracker are the codebase that AI "regenerates"
- L2's `_underscore` convention → @property pattern in L3
- L2's encapsulation concept → AI code often uses it automatically

### To Lesson 4
- "You now know Python + OOP + how to work with AI. Next: real market data."
- Students can use vibe coding to explore BTC microstructure data in L4

## Conventions
- Solutions embedded in exercise notebook — no separate `solutions/` folder
- No external API calls — all "AI-generated" code is pre-written inline to simulate LLM output
- The lesson does NOT teach prompt engineering — it teaches code evaluation
- try/except, type hints, @property, comprehensions, decorators are taught through AI code reading, not as standalone theory blocks
- All examples continue using BTCUSDT/ETHUSDT — consistent with L1–L2 market context
