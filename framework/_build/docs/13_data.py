"""Datos reales para el doc de L13: el market maker naive simulado con y sin
skew de inventario (MMSimulation de referencia, misma semilla)."""
from exchange.simulation import MMSimulation
from exchange.strategies.market_maker import MarketMaker


def sim(skew: float):
    mm = MarketMaker("SIM", quote_size=0.1, half_spread=0.6, inventory_skew=skew)
    res = MMSimulation(mm, s0=100.0, sigma=0.5, steps=500, seed=42).run()
    return {"mid": [round(x, 3) for x in res.mid],
            "inv": [round(x, 3) for x in res.inventory],
            "pnl": [round(x, 3) for x in res.pnl],
            "finalPnl": round(res.final_pnl, 2),
            "maxInv": round(res.max_inventory, 2)}


def build() -> dict:
    return {"skew": sim(2.0), "noskew": sim(0.0)}
