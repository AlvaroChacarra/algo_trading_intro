# Clase 14 - Avellaneda-Stoikov: el barrido de gamma. En un .py.
# Ejecuta desde exercises/:  python mm_sweep.py

from exchange.simulation import MMSimulation
from exchange.strategies import AvellanedaStoikov, MarketMaker


def run(strategy):
    return MMSimulation(strategy, s0=100.0, sigma=0.5, steps=500,
                        kappa=1.5, seed=42).run()


def main():
    naive = run(MarketMaker("SIM", quote_size=0.1, half_spread=0.6,
                            inventory_skew=2.0))
    print(f"naive (L13)  : PnL={naive.final_pnl:>6.2f}  "
          f"max|inv|={naive.max_inventory:.2f}")

    print("gamma  PnL     max|inv|   <- la frontera riesgo/retorno")
    for gamma in (0.05, 0.2, 0.5, 1.0, 2.0):
        mm = AvellanedaStoikov("SIM", quote_size=0.1, gamma=gamma,
                               sigma=0.5, kappa=1.5, horizon=500)
        res = run(mm)
        print(f"{gamma:<5}  {res.final_pnl:>6.2f}   {res.max_inventory:.2f}")


if __name__ == "__main__":
    main()
