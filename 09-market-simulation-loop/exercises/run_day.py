# Clase 9 - El loop de simulacion, en un archivo .py
# Ejecuta desde exercises/:  python run_day.py

from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.portfolio import PositionTracker


def main():
    market = Market.sample()
    tracker = PositionTracker()
    equity_curve = []
    step = 0

    while market.step() is not None:
        step += 1
        if step == 50:  # la decision: comprar en el paso 50
            for fill in market.submit(Order("BTCUSDT", "buy", 0.5,
                                            order_type=OrderType.MARKET)):
                tracker.apply_fill(fill)
                print(f"paso {step}: {fill}")
        equity_curve.append(tracker.equity(market.book.mid))

    print(f"dia completo: {step} pasos  posicion={tracker.position:.4f}  "
          f"equity final={equity_curve[-1]:.2f}")


if __name__ == "__main__":
    main()
