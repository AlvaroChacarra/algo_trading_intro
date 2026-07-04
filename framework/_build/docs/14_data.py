"""Datos reales para el doc de L14: Avellaneda-Stoikov contra el naive y el
barrido de gamma, con la MMSimulation de referencia (misma semilla)."""
from exchange.simulation import MMSimulation
from exchange.strategies.market_maker import AvellanedaStoikov, MarketMaker

SIGMA = 0.5
KAPPA = 1.5
HORIZON = 500


def paths(strategy):
    res = MMSimulation(strategy, s0=100.0, sigma=SIGMA, steps=HORIZON,
                       kappa=KAPPA, seed=42).run()
    return {"inv": [round(x, 3) for x in res.inventory],
            "pnl": [round(x, 3) for x in res.pnl],
            "finalPnl": round(res.final_pnl, 2),
            "maxInv": round(res.max_inventory, 2)}


def build() -> dict:
    naive = paths(MarketMaker("SIM", quote_size=0.1, half_spread=0.6,
                              inventory_skew=2.0))
    a_s = paths(AvellanedaStoikov("SIM", quote_size=0.1, gamma=0.5,
                                  sigma=SIGMA, kappa=KAPPA, horizon=HORIZON))
    sweep = []
    for g in (0.05, 0.2, 0.5, 1.0, 2.0):
        r = paths(AvellanedaStoikov("SIM", quote_size=0.1, gamma=g,
                                    sigma=SIGMA, kappa=KAPPA, horizon=HORIZON))
        sweep.append({"gamma": g, "pnl": r["finalPnl"], "maxInv": r["maxInv"]})
    return {"naive": naive, "as": a_s, "sweep": sweep,
            "sigma": SIGMA, "kappa": KAPPA, "horizon": HORIZON}
