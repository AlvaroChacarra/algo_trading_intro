# Lesson 14 — Avellaneda-Stoikov

## Purpose
40-minute class delivering the analytical solution to L13's open question: the
mathematically optimal market making policy. 100% HTML presentation + exercises notebook.
No main lesson notebook — the HTML is the lesson. L13 and L14 are quasi-continuous.

## File structure
```
14-avellaneda-stoikov/
├── README.md
├── CLAUDE.md                                       (this file)
├── presentation/
│   └── avellaneda-stoikov-interactive.html         (~1800 lines)
└── exercises/
    └── avellaneda_stoikov_exercises.ipynb          (10 exercises, 46 cells)
```

## HTML presentation structure
- **Hero (3 min):** Two A-S formulas animate in with colored variable annotations and legends.
  Each variable labeled with its meaning (r, s, q, γ, σ², T−t, δ*, κ).
- **B1 (7 min):** Three ingredient cards:
  - BM: p5.js live random walk
  - Poisson: Chart.js λ = A·e^{−κδ} decay curve
  - CARA: Chart.js utility curves for γ=0.1 vs γ=0.3
- **B2 (8 min):** HJB equation display + 4-step derivation walkthrough (btn-triggered GSAP).
  Two result boxes: reservation price and half-spread with component breakdown.
- **B3 (8 min):** Five sliders (q, γ, σ, T−t, κ) → live reservation price + half-spread breakdown.
  Mini-LOB showing A-S quotes vs naive quotes.
- **B4 (10 min):** Real-time simulation Naive vs A-S.
  γ slider adjusts A-S behavior IMMEDIATELY without restart.
  Shock button: σ×3 for 300 steps.
  Three Chart.js charts: inventory, P&L, price + A-S quotes.
  Live δ* decomposition display.
- **Cierre (3 min):** 3 takeaways + bridge to L15 (Exam-Quiz II).

## A-S formulas (exact)
```
r(s, t) = s − q·γ·σ²·(T−t)

δ*(τ) = γ·σ²·(T−t)/2  +  (1/γ)·ln(1 + γ/κ)
         ─────────────     ───────────────────
         cobertura inv.     liquidez permanente
```

## Simulation constants (HTML and notebook must match)
```python
SIGMA    = 0.05     # price vol per step
SIGMA_SQ = 0.0025   # SIGMA**2
SPREAD   = 0.10     # naive spread (reference only)
KAPPA    = 5.0      # fill prob decay
ARR      = 1.0      # base arrival rate
DT       = 1.0
T_TOTAL  = 3600     # session steps
MID0     = 100.0
```

## Validator constants for exercises
```
E1:  as_reservation_price(100, 5, 0.1, 0.0025, 3600)  = 95.5
     as_reservation_price(100, -3, 0.1, 0.0025, 3600) = 102.7
     as_reservation_price(100, 0, 0.1, 0.0025, 0)     = 100.0
     as_reservation_price(100, 10, 0.2, 0.0025, 3600) = 82.0
     Property: at τ=0, r = mid regardless of q

E2:  as_optimal_halfspread(0.1, 0.0025, 5.0, 3600)
       inv=0.45000, liq=0.19803, total=0.64803
     as_optimal_halfspread(0.1, 0.0025, 5.0, 0)
       inv=0.00000, liq=0.19803, total=0.19803
     Property: liq component is constant across τ

E4:  ASMarketMaker(T=3600, gamma=0.1, seed=42).run(price_path(T=3600, seed=42))
       fills=1414, inventory=0, pnl≈301.31 (tolerance 1.0)
       inv_std≈0.5918 (tolerance 0.05), max_abs_inv=4

E5:  Comparison (N=20): inv_std_AS < inv_std_Skewed < inv_std_Naive
     A-S reduces inventory std by >90% vs Naive

E6:  Gamma sensitivity (path_3600, seed=42):
       γ=0.01: fills=2475, inv_std=1.5353, max_abs=7
       γ=0.10: fills=1414, inv_std=0.5918, max_abs=4
       γ=0.50: fills=341,  inv_std=0.2723, max_abs=2
     Properties: fills and inv_std both strictly decreasing with γ
```

## Key implementation detail: ASMarketMaker
- RNG: `np.random.default_rng(seed)` — same as L13 classes
- At step t (0-indexed): τ = T − t (so first step τ = T = 3600)
- Fill distances: `d_ask = max(ask − mid, 0)`, `d_bid = max(mid − bid, 0)`
- Fill probabilities: `p_ask = exp(−κ·d_ask)·ARR·DT`, `p_bid = exp(−κ·d_bid)·ARR·DT`
- **Ask fill ALWAYS before bid fill** (inventory -= 1 before inventory += 1)
- This order matches the seeded RNG and produces the validated constants above

## Real-time γ slider (B4)
The HTML γ slider does NOT restart the simulation. `getGamma()` reads the slider value
on every step. Changing γ mid-simulation is intentional — students see immediate effect
on inventory accumulation vs fill rate.

## Continuity
- `as_reservation_price(mid, q, gamma, sigma_sq, tau)` generalizes L13's
  `reservation_price(mid, q, gamma, sigma_sq)` which had an implicit τ=1.
- `MarketMakingBacktest` from L13 E10 accepts `ASMarketMaker` directly — stable run() signature.
- `price_path` and `price_path_with_shock` (E7) reused from L13.
- Notebook imports all L13 classes directly (no separate file dependency).
