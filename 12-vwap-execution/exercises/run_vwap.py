# Clase 12 - Vender grande: de golpe vs TWAP vs VWAP. En un .py.
# Ejecuta desde exercises/:  python run_vwap.py

from exchange.backtest import Backtest
from exchange.market import Market
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType
from exchange.strategies.vwap import VWAPStrategy


def u_profile(n):
    """Perfil intradia en U: mas volumen en apertura y cierre."""
    return [0.6 + 1.6 * (2 * (i / (n - 1)) - 1) ** 2 for i in range(n)]


def avg_price(fills):
    total = sum(f.size for f in fills)
    return sum(f.price * f.size for f in fills) / total


def main():
    book = Market.sample(depth=5).step()
    total = round(sum(lv.size for lv in book.bids[:5]) * 0.9, 2)
    mid0 = book.mid
    print(f"vender {total} BTC  (mid inicial {mid0:.2f})")

    fills = MatchingEngine().process(
        Order("BTCUSDT", "sell", total, order_type=OrderType.MARKET), book)
    print(f"  de golpe : precio medio {avg_price(fills):.2f}")

    for name, profile in (("TWAP", None), ("VWAP-U", u_profile(500))):
        strat = VWAPStrategy("BTCUSDT", "sell", total, 500, profile)
        res = Backtest(Market.sample(), strat).run()
        print(f"  {name:<8}: precio medio {avg_price(res.fills):.2f}")


if __name__ == "__main__":
    main()
