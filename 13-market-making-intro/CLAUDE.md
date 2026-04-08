# Lesson 13 — Market Making

## Purpose
40-minute class introducing market making: mechanics, three risks, and practical heuristics.
Ends with the open question that L14 (Avellaneda-Stoikov) answers. 100% HTML presentation
+ exercises notebook. No main lesson notebook — the HTML is the lesson.

## File structure
```
13-market-making-intro/
├── README.md
├── CLAUDE.md                                   (this file)
├── presentation/
│   └── market-making-interactive.html          (~1900 lines)
└── exercises/
    └── market_making_exercises.ipynb           (10 exercises, 45 cells)
```

## HTML presentation structure
- **Hero (5 min):** p5.js LOB animation — MM quotes bid/ask, market orders arrive and execute.
  Live P&L / inventory / fills counters update in real time.
- **B1 (7 min):** GSAP-animated 5-step trade sequence. Formula card: `P&L = fills×s/2 − |q|×|ΔS|`.
  Key insight: the inventory cost term can exceed the spread income.
- **B2 (8 min):** Three risk cards — inventory risk (Chart.js), adverse selection (GSAP timeline),
  volatility/stale quote (Chart.js). Each has its own mini-visualization.
- **B3 (10 min):** Three tabs — Imbalance, Nivel 2, Skew de inventario.
  Tabs share a live p5-less simulation driven by `setInterval` + Chart.js.
  Skew tab introduces `reservation_price = mid - q·γ·σ²` explicitly as preview of A&S.
- **Cierre (3 min):** 3 takeaways + bridge to L14 (HJB + A&S).

## Simulation constants (HTML and notebook must match)
```javascript
SIGMA    = 0.05     // price vol per step
SPREAD   = 0.10     // total spread in price units
KAPPA    = 5.0      // fill prob decay: p = exp(-kappa * delta_from_mid)
ARR      = 1.0      // base arrival rate per step
SIGMA_SQ = 0.0025   // SIGMA^2
DT       = 1.0
```

Fill probability model: `p_fill = exp(-KAPPA * distance_from_mid) * ARR * DT`
This is the same exponential model as A&S — intentional continuity.

## Validator constants for exercises
```
E1:  price_path(T=100, dt=1, sigma=0.05, seed=42)
       [0]=100.0, [50]=100.22802758, [100]=99.74865194, len=101

E2:  NaiveMarketMaker(seed=42).run(price_path(T=500,seed=42))
       fills=774, inventory=-10, pnl≈43.9333  (tolerance 0.1)

E3:  reservation_price(100.0, q=5,  gamma=0.1, sigma_sq=0.0025) = 99.998750
     reservation_price(100.0, q=-3, gamma=0.1, sigma_sq=0.0025) = 100.000750
     reservation_price(100.0, q=10, gamma=0.2, sigma_sq=0.0025) = 99.995000

E4:  SkewedMarketMaker(seed=42).run(price_path(T=3600,seed=42))
       fills=5643, inventory=-3, pnl≈291.6679  (tolerance 1.0)

E5:  std(naive_inv) ≈ 9.91 vs std(skewed_inv) ≈ 5.43
     max_abs(naive) = 26, max_abs(skewed) = 15
     Assert: std_skewed < std_naive AND max_skewed <= max_naive
```

## Key pedagogical design decisions

### Fill probability model in the simulation
Uses `exp(-kappa * distance_from_mid)` — intentionally the same exponential model
as in Avellaneda-Stoikov. Students see it first as a "black box probability", then
in L14 it appears as the Poisson order arrival rate `λ = A·e^(-κ·δ)`.

### Reservation price in B3 tab 3
The formula `r = mid - q·γ·σ²` is introduced heuristically in the HTML, without
justification. The A&S preview code block explicitly says "L14 justifies this
mathematically." This seeds curiosity before L14.

### Skewed vs Naive inventory comparison
With SIGMA=0.05, KAPPA=5, GAMMA=0.1, the skew effect is clearly visible:
- Naive inventory std ≈ 9.9, max_abs ≈ 26
- Skewed inventory std ≈ 5.4, max_abs ≈ 15
If parameters change, revalidate E4/E5 and update this file.

### The three risks are instances of one problem
B2 intentionally presents adverse selection, volatility/stale, and inventory risk
as three separate risks, then the B1 formula shows they're all the `|q|×|ΔS|` term.
The cierre makes this explicit.

## Continuity with L14
- `MarketMakingBacktest` (E10) is designed to accept any MMClass including the A&S
  implementation built in L14. The `run()` signature is stable.
- `reservation_price()` function (E3) is used directly in L14's A-S model.
- `SkewedMarketMaker` (E4) uses the static reservation price (no T-t factor).
  L14's `ASMarketMaker` adds the `(T-t)` time decay and the optimal spread formula.
- `price_path()` and `price_path_with_shock()` are reused in L14 simulations.
