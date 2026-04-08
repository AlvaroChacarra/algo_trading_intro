# Lesson 12 — RFQ & Close Probability

## Purpose
40-minute class on RFQ market structure in fixed income. Core question: given that you quote a spread, what's the probability the client accepts? Use logistic regression to model P(close|spread) and find the revenue-maximizing spread.

## File structure
```
12-rfq-close-probability/
├── README.md
├── CLAUDE.md                                (this file)
├── presentation/
│   └── rfq-close-probability-interactive.html  # 28-min HTML presentation
├── exercises/
│   └── rfq_close_probability_exercises.ipynb   # 10 exercises with validators
└── data/
    ├── generate_rfq_dataset.py             # Dataset generator (run once)
    ├── rfq_dataset.csv                     # 800 RFQs × 19 columns
    └── scatter_data.json                   # 80 sample pts/tier for HTML
```

## Lesson flow
1. `presentation/rfq-close-probability-interactive.html` — 28-min HTML (Hero + 3 blocks + cierre)
2. `exercises/rfq_close_probability_exercises.ipynb` — E1–E5 in-class, E6–E10 bonus

## Dataset facts
- 800 RFQs × 19 columns, 10 trading days, 6 Tesoro bonds (2Y/5Y/10Y/15Y/30Y)
- Tier distribution: T1=156, T2=321, T3=323
- After filtering (E3): df_model = 557 rows (65 won + 492 closed_away + 0 ambiguous)
- 243 ambiguous RFQs removed (won=0, closed_away=0)

## Logistic model parameters (1 feature: spread_bp)
Pre-computed with `sklearn.linear_model.LogisticRegression(random_state=42)`:

| Tier | b0         | b1         | s*      | p*    | n   |
|------|------------|------------|---------|-------|-----|
| T1   | -1.153594  | -1.164688  | 0.9484  | 9.47% | 102 |
| T2   | -1.895052  | -0.336315  | 3.1294  | 4.99% | 233 |
| T3   | -3.082927  | +0.677225  | ∞ (none)|  —    | 222 |

T3 has b1 > 0 (wins concentrated at high spreads, 15/222). No interior s*.

## 2-feature model parameters (spread_bp + num_dealers)
| Tier | b0      | b_spread | b_dealers |
|------|---------|----------|-----------|
| T2   | 1.3188  | -0.2098  | -1.0489   |
| T3   | 2.3720  | -0.0415  | -1.8606   |

## Validator constants for exercises
```
E1:  df.shape == (800, 19)
E2:  spread_bp means: T1=0.0761, T2=0.4136, T3=0.6600  (tolerance 0.005)
E3:  df_model.shape[0] == 557,  df_model['won'].sum() == 65
E4:  b0/b1 per tier — see table above  (tolerance 0.001)
E5:  predict_close_probability(1, 0.5) = 0.14983
     predict_close_probability(1, 0.0) = 0.23983
     predict_close_probability(2, 0.4) = 0.11613
     predict_close_probability(3, 1.0) = 0.08274
E6:  expected_revenue(1, 0.5, 1.0) = 0.074915
     expected_revenue(1, 0.948361, 1.0) = 0.089762  (≈ max for T1)
     expected_revenue(2, 0.4, 2.0) = 0.092906
E7:  optimal_spread(1) ≈ 0.9484,  optimal_spread(2) ≈ 3.1294
     Q invariance: optimal_spread(t, Q=1) == optimal_spread(t, Q=10)  (tol 0.01)
E9:  T2 2feat: b0=1.3188, b_spread=-0.2098, b_dealers=-1.0489  (tol 0.01)
     T3 2feat: b0=2.3720, b_spread=-0.0415, b_dealers=-1.8606  (tol 0.01)
```

## Key pedagogical design decisions

### The closed_away trap (B1)
The 243 RFQs with `won=0, closed_away=0` look identical to genuine losses. Only by filtering to `(won=1 | closed_away=1)` do we get a clean binary target. Reveal this in B1 — let students hypothesize first.

### T3 b1 > 0 (B2)
With only 15 wins in 222 RFQs, all concentrated at high spreads, the logistic fit yields a positive slope. This is NOT causal — it reflects T3 clients being opportunistic (they only accept when they really want liquidity). Use this as a "model can fit spuriously" lesson.

### Q cancels (B3)
s* = -1/(b1 × (1-p*)) is independent of Q. The Q slider in B3 scales the revenue chart vertically but does NOT move the s* line. This is the main insight students should leave with.

### spread_bp normalization (E2)
`spread_price / dv01` normalizes the quoted price away from mid into basis points. This makes T1 and T3 spreads comparable despite very different DV01s (2Y vs 30Y).

## HTML presentation structure
- **Hero (5 min):** RFQ terminal with 30s countdown. Three outcome cards reveal: won / closed_away / price discovery. Trap badge on discovery card.
- **B1 (7 min):** 800→557 path diagram, filter explanation, win rate bars (raw vs corrected by tier).
- **B2 (8 min):** Scatter + logistic curve (Chart.js). Tier toggle. Spread slider with live P(close) readout.
- **B3 (8 min):** Dual synchronized charts — P(s) and E[Rev]. Tier selector. Q slider scales revenue curve but s* doesn't move.
- **Cierre (3 min):** 3 takeaways + bridge to L13 (Avellaneda-Stoikov).

## Continuity
- `spread_bp` normalization (this lesson) → reused as a feature in L13 market-making model
- `RFQModel.optimal_spread()` → motivates A-S model: s* is static, but inventory should shift it dynamically
- T3 model failure → motivates richer features (volume, volatility, time of day) in future work
