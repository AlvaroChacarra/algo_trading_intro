"""
Generate synthetic RFQ dataset for L12 — RFQ Close Probability.
800 RFQs across 10 trading days (80/day), 6 Tesoro bonds.

Run: python generate_rfq_dataset.py
Output: rfq_dataset.csv
"""
import numpy as np
import pandas as pd
from scipy.special import expit  # sigmoid

RNG = np.random.default_rng(42)

# ── BOND UNIVERSE ────────────────────────────────────────────────────────────
# YTM curve: 2Y→3.00%, 5Y→3.40%, 10Y→3.60%, 15Y→3.80%, 30Y→3.90%
# Coupons chosen so bonds trade slightly below par (realistic Tesoro)

BONDS = {
    "ESP 2Y":  {"tenor": 2,  "coupon": 2.75, "ytm_base": 3.00},
    "ESP 5Y":  {"tenor": 5,  "coupon": 3.25, "ytm_base": 3.40},
    "ESP 10Y": {"tenor": 10, "coupon": 3.50, "ytm_base": 3.60},
    "ESP 15Y": {"tenor": 15, "coupon": 3.75, "ytm_base": 3.80},
    "ESP 30Y": {"tenor": 30, "coupon": 4.00, "ytm_base": 3.90},
}

# Bond weights (5Y and 10Y most traded)
BOND_NAMES   = list(BONDS.keys())
BOND_WEIGHTS = np.array([0.10, 0.25, 0.30, 0.20, 0.15])

# Daily price volatility by tenor (annualised σ ≈ tenor * 0.004, rough)
DAILY_SIGMA = {2: 0.020, 5: 0.040, 10: 0.065, 15: 0.085, 30: 0.110}

# ── BOND MATH ────────────────────────────────────────────────────────────────

def bond_price(coupon_pct, tenor, ytm):
    """Dirty price per 100 nominal, annual coupons.
    coupon_pct: coupon in % (e.g. 3.25 → pays 3.25 per year per 100 nominal)
    ytm:        yield in % (e.g. 3.40)
    """
    c = coupon_pct          # cash coupon per 100 nominal (already in price terms)
    y = ytm / 100           # yield as decimal
    p = sum(c / (1 + y) ** t for t in range(1, tenor + 1))
    p += 100 / (1 + y) ** tenor
    return p

def bond_ytm(price, coupon_pct, tenor, guess=0.035):
    """Newton-Raphson YTM from price. Returns YTM in %."""
    c = coupon_pct          # same convention as bond_price
    y = guess
    for _ in range(60):
        pv   = sum(c / (1+y)**t for t in range(1, tenor+1)) + 100/(1+y)**tenor
        dpv  = sum(-t*c / (1+y)**(t+1) for t in range(1, tenor+1)) - tenor*100/(1+y)**(tenor+1)
        dy   = (pv - price) / dpv
        y   -= dy
        if abs(dy) < 1e-10:
            break
    return round(y * 100, 4)

def bond_dv01(coupon_pct, tenor, ytm):
    """DV01 per 100 nominal (price change for +1bp in yield)."""
    p0 = bond_price(coupon_pct, tenor, ytm)
    p1 = bond_price(coupon_pct, tenor, ytm + 0.01)
    return round(abs(p1 - p0), 5)

# Pre-compute base prices and DV01 for each bond
for name, b in BONDS.items():
    b["price_base"] = round(bond_price(b["coupon"], b["tenor"], b["ytm_base"]), 4)
    b["dv01_base"]  = bond_dv01(b["coupon"], b["tenor"], b["ytm_base"])

# ── SIMULATION PARAMETERS ────────────────────────────────────────────────────

N_DAYS  = 10
N_DAILY = 80
N_TOTAL = N_DAYS * N_DAILY

# Tier distribution: 20% T1, 40% T2, 40% T3
TIER_PROBS = [0.20, 0.40, 0.40]

# Quoted spread distribution (in bp): N(mean, sigma)
TIER_SPREAD_BP = {
    1: (0.10, 0.15),   # ~25% chance negative spread (inside mid)
    2: (0.40, 0.20),
    3: (0.70, 0.25),
}

# Won rate targets (calibrated via intercept tuning)
TARGET_WON = {1: 0.15, 2: 0.09, 3: 0.05}

# Dealer count groups and weights
DEALER_DIST = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
DEALER_WEIGHTS = np.array([0.05, 0.12, 0.10, 0.10, 0.08, 0.10, 0.10, 0.10, 0.08, 0.09, 0.08])

# Volume (in M€) log-normal parameters by tier [mu_log, sigma_log]
VOL_PARAMS = {1: (3.0, 0.9), 2: (2.0, 0.8), 3: (1.1, 0.7)}   # exp gives M€ 5-100 / 2-30 / 1-10

# ── DAILY PRICE PATHS ────────────────────────────────────────────────────────

# Generate mid CBBT base path per bond per day (Brownian walk, cumulative)
daily_price_offsets = {}
for name, b in BONDS.items():
    sigma_d = DAILY_SIGMA[b["tenor"]]
    shocks   = RNG.normal(0, sigma_d, N_DAYS)
    cum      = np.concatenate([[0], np.cumsum(shocks)])[:N_DAYS]  # day 0 = base
    daily_price_offsets[name] = cum

# ── GENERATE RFQs ─────────────────────────────────────────────────────────────

start_date = pd.Timestamp("2025-11-03 09:00")   # Monday
trading_days = pd.bdate_range(start_date, periods=N_DAYS)

rows = []
rfq_counter = 1

for day_idx, day in enumerate(trading_days):
    # Daily side bias (some days slightly more buy or sell)
    side_bias = RNG.uniform(0.44, 0.56)

    for _ in range(N_DAILY):
        # ── Sample bond ──
        bond_name = RNG.choice(BOND_NAMES, p=BOND_WEIGHTS)
        b         = BONDS[bond_name]
        tenor     = b["tenor"]
        coupon    = b["coupon"]
        dv01      = b["dv01_base"]

        # ── Mid CBBT: daily path + intraday noise ──
        intraday_noise = RNG.normal(0, dv01 * 0.3)
        mid_cbbt       = round(b["price_base"] + daily_price_offsets[bond_name][day_idx]
                               + intraday_noise, 4)

        # ── CBBT spread (in price terms): 1.0–2.5 DV01 range ──
        spread_cbbt_factor = RNG.uniform(1.0, 2.5)
        spread_price_cbbt  = round(spread_cbbt_factor * dv01, 5)
        bid_cbbt = round(mid_cbbt - spread_price_cbbt / 2, 4)
        ask_cbbt = round(mid_cbbt + spread_price_cbbt / 2, 4)

        # ── MTS: spread = exactly 2 DV01 (fixed rule) ──
        mts_noise   = RNG.normal(0, dv01 * 0.15)   # small basis vs CBBT
        mid_mts     = round(mid_cbbt + mts_noise, 4)
        best_bid_mts = round(mid_mts - dv01, 4)
        best_ask_mts = round(mid_mts + dv01, 4)

        # ── Tier / Side / Dealers / Volume ──
        tier         = RNG.choice([1, 2, 3], p=TIER_PROBS)
        side         = 1 if RNG.random() < side_bias else 2
        num_dealers  = RNG.choice(DEALER_DIST, p=DEALER_WEIGHTS)
        vol_mu, vol_sigma = VOL_PARAMS[tier]
        volume_meur  = round(float(np.exp(RNG.normal(vol_mu, vol_sigma))), 2)

        # ── Quoted price (bp normal → price, normalized by DV01) ──
        mu_bp, sigma_bp = TIER_SPREAD_BP[tier]

        # Special case: tier1 small volume → allow more negative spread
        if tier == 1 and volume_meur < 2.0:
            mu_bp_adj = mu_bp - 0.05
        else:
            mu_bp_adj = mu_bp

        # Outlier flag: 6% of rows ignore tier logic
        is_outlier = RNG.random() < 0.06
        if is_outlier:
            spread_bp = RNG.uniform(-0.2, 1.5)
        else:
            spread_bp = RNG.normal(mu_bp_adj, sigma_bp)

        spread_price = spread_bp * dv01

        if side == 1:   # BUY: client buys, we sell → we quote above mid
            quoted_price = mid_cbbt + spread_price
            # Hard constraint: quoted ≤ best_ask_mts
            quoted_price = min(quoted_price, best_ask_mts - 0.0001)
        else:            # SELL: client sells, we buy → we quote below mid
            quoted_price = mid_cbbt - spread_price
            # Hard constraint: quoted ≥ best_bid_mts
            quoted_price = max(quoted_price, best_bid_mts + 0.0001)

        quoted_price = round(quoted_price, 4)

        # ── YTM from mid CBBT (Newton-Raphson) ──
        ytm = bond_ytm(mid_cbbt, coupon, tenor, guess=b["ytm_base"]/100)

        # ── Proximity signal: how close is CBBT mid to the relevant MTS side ──
        # If side=1 (BUY), market leaning buy → cbbt near ask_mts → easier to sell
        # Signal: negative = cbbt leans toward bid (market selling), positive = toward ask
        mts_range = best_ask_mts - best_bid_mts  # = 2*dv01
        cbbt_position = (mid_cbbt - best_bid_mts) / mts_range  # 0=at bid, 1=at ask
        if side == 1:
            proximity_signal = cbbt_position - 0.5        # positive = market leans buy
        else:
            proximity_signal = 0.5 - cbbt_position        # positive = market leans sell

        # ── Win probability (logistic) ──
        # Spread_bp: smaller = more competitive = higher win prob
        dist_bp   = abs(spread_bp)   # distance from mid in bp

        # Dealer group penalty
        if num_dealers == 1:
            dealer_penalty = 0.0   # handled separately
        elif num_dealers <= 4:
            dealer_penalty = -0.2
        elif num_dealers <= 9:
            dealer_penalty = -0.9
        else:
            dealer_penalty = -1.6

        # CBBT spread: wider = fewer dealers checking → easier
        cbbt_spread_signal = (spread_price_cbbt / dv01 - 1.5) * 0.4  # centered at 1.5 DV01

        # Tier intercepts (tuned to hit target win rates)
        tier_intercept = {1: -1.05, 2: -2.10, 3: -2.95}[tier]

        logit = (tier_intercept
                 - 1.8 * dist_bp                  # competitiveness
                 + 0.7 * cbbt_spread_signal        # wide cbbt spread = easier
                 + 0.5 * proximity_signal          # market momentum
                 + dealer_penalty
                 + RNG.normal(0, 0.45))            # irreducible noise

        p_win = float(expit(logit))

        # Force num_dealers=1 → always win
        if num_dealers == 1:
            won = 1
        else:
            won = int(RNG.random() < p_win)

        # ── Closed away ──
        if won == 1:
            closed_away = 0
            cover_price = np.nan
        else:
            # 68% chance someone else closed
            if RNG.random() < 0.68:
                closed_away = 1
                # Cover is better than our quote
                delta_bp   = abs(RNG.normal(0.15, 0.10))   # cover is ~0.15 bp better
                delta_price = max(delta_bp * dv01, 0.0001)
                if side == 1:
                    cover_price = round(quoted_price - delta_price, 4)  # they sold cheaper
                else:
                    cover_price = round(quoted_price + delta_price, 4)  # they paid more
                # Cover must also respect MTS constraints
                if side == 1:
                    cover_price = max(cover_price, best_bid_mts + 0.0001)
                else:
                    cover_price = min(cover_price, best_ask_mts - 0.0001)
                cover_price = round(cover_price, 4)
            else:
                closed_away = 0   # price discovery
                cover_price = np.nan

        # ── Timestamp: uniformly within trading hours ──
        seconds_in_day = RNG.integers(0, 8 * 3600)   # 09:00 to 17:00
        ts = day + pd.Timedelta(seconds=int(seconds_in_day))

        rows.append({
            "rfq_id":           f"RFQ_{rfq_counter:04d}",
            "timestamp":         ts,
            "bond_name":         bond_name,
            "tenor":             tenor,
            "coupon":            coupon,
            "mid_price_cbbt":    mid_cbbt,
            "spread_price_cbbt": spread_price_cbbt,
            "best_bid_mts":      best_bid_mts,
            "best_ask_mts":      best_ask_mts,
            "ytm":               ytm,
            "dv01":              dv01,
            "tier":              tier,
            "side":              side,
            "volume_meur":       volume_meur,
            "num_dealers":       num_dealers,
            "quoted_price":      quoted_price,
            "won":               won,
            "closed_away":       closed_away,
            "cover_price":       cover_price,
        })

        rfq_counter += 1

df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
df["rfq_id"] = [f"RFQ_{i+1:04d}" for i in range(len(df))]

# ── VALIDATION STATS ─────────────────────────────────────────────────────────
print("=== Dataset validation ===")
print(f"Total rows: {len(df)}")
print(f"\nWon rate by tier:")
for t in [1, 2, 3]:
    mask = df["tier"] == t
    wr   = df.loc[mask, "won"].mean()
    print(f"  Tier {t}: {wr:.3f}  (target {TARGET_WON[t]:.2f}, n={mask.sum()})")

print(f"\nClosed away breakdown:")
print(f"  won=1, closed_away=0:  {((df['won']==1)&(df['closed_away']==0)).sum()}")
print(f"  won=0, closed_away=1:  {((df['won']==0)&(df['closed_away']==1)).sum()}  (competitor won)")
print(f"  won=0, closed_away=0:  {((df['won']==0)&(df['closed_away']==0)).sum()}  (price discovery)")

print(f"\nMTS spread == 2×DV01 check (mean diff): "
      f"{((df['best_ask_mts']-df['best_bid_mts']) - 2*df['dv01']).abs().mean():.6f}")

print(f"\nQuoted price constraints violations:")
buy_viol  = ((df['side']==1) & (df['quoted_price'] > df['best_ask_mts'])).sum()
sell_viol = ((df['side']==2) & (df['quoted_price'] < df['best_bid_mts'])).sum()
print(f"  BUY quoted > best_ask_mts:  {buy_viol}")
print(f"  SELL quoted < best_bid_mts: {sell_viol}")

print(f"\nBond distribution:")
print(df["bond_name"].value_counts().to_string())

print(f"\nNegative spread (quoted inside mid) by tier:")
df["spread_to_mid"] = np.where(df["side"]==1,
                               df["quoted_price"] - df["mid_price_cbbt"],
                               df["mid_price_cbbt"] - df["quoted_price"])
for t in [1, 2, 3]:
    mask = df["tier"] == t
    neg  = (df.loc[mask, "spread_to_mid"] < 0).mean()
    print(f"  Tier {t}: {neg:.1%} negative spread")

print(f"\nSample rows:")
print(df[["rfq_id","bond_name","tier","side","quoted_price","mid_price_cbbt",
          "won","closed_away","cover_price"]].head(8).to_string(index=False))

# ── SAVE ─────────────────────────────────────────────────────────────────────
out_path = "rfq_dataset.csv"
df.drop(columns=["spread_to_mid"]).to_csv(out_path, index=False)
print(f"\nSaved → {out_path}  ({len(df)} rows × {len(df.columns)} cols)")
