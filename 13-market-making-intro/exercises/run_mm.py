# Clase 13 - El market maker, con y sin correa. En un .py.
# Ejecuta desde exercises/:  python run_mm.py

from exchange.simulation import MMSimulation
from exchange.strategies import MarketMaker

SIGMA_HORIZON = 0.5
HORIZON = 500
ARRIVAL_INTENSITY = 520.0


def run(skew):
    mm = MarketMaker("SIM", quote_size=0.1, half_spread=0.6, inventory_skew=skew)
    res = MMSimulation(mm, s0=100.0, sigma=SIGMA_HORIZON,
                       steps=HORIZON, A=ARRIVAL_INTENSITY, seed=42).run()
    print(f"  skew={skew:>3}: PnL={res.final_pnl:>6.2f}  "
          f"max|inventario|={res.max_inventory:.2f}")


def main():
    print("misma semilla, mismo mercado; solo cambia la correa:")
    run(0.0)
    run(2.0)
    print("la correa domestica el inventario... y cuesta PnL. Trade-off.")


if __name__ == "__main__":
    main()
