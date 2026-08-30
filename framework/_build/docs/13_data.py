"""Datos sintéticos para el doc de L13: el market maker naive simulado con y sin
skew de inventario (MMSimulation de referencia, misma semilla)."""
from exchange.simulation import MMSimulation
from exchange.strategies.market_maker import MarketMaker

SIGMA_HORIZON = 0.5
HORIZON = 500
# Intensidad por horizonte del escenario didáctico común a L13/L14. Con A=1
# apenas se espera una llegada antes de aplicar la distancia de la quote;
# A=520 produce una muestra informativa sin cambiar semilla ni discretización.
ARRIVAL_INTENSITY = 520.0


def sim(skew: float):
    mm = MarketMaker("SIM", quote_size=0.1, half_spread=0.6, inventory_skew=skew)
    res = MMSimulation(mm, s0=100.0, sigma=SIGMA_HORIZON,
                       steps=HORIZON, A=ARRIVAL_INTENSITY, seed=42).run()
    return {"mid": [round(x, 3) for x in res.mid],
            "inv": [round(x, 3) for x in res.inventory],
            "pnl": [round(x, 3) for x in res.pnl],
            "nFills": res.n_fills,
            "finalPnl": round(res.final_pnl, 2),
            "maxInv": round(res.max_inventory, 2)}


def build() -> dict:
    return {"skew": sim(2.0), "noskew": sim(0.0),
            "arrivalIntensity": ARRIVAL_INTENSITY}
