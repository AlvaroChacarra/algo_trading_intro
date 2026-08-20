# Clase 8 - Barridos y tipos de orden, en un archivo .py
# Ejecuta desde exercises/:  python matching_demo.py

import csv
import os

from exchange.book import OrderBook
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType


def fresh_book():
    path = os.path.join(os.path.dirname(__file__), "exchange", "_data",
                        "btc_lob_snapshots.csv")
    with open(path, newline="") as f:
        row = {k: float(v) for k, v in next(csv.DictReader(f)).items()}
    return OrderBook.from_snapshot("BTCUSDT", row, depth=10)


def sweep(size):
    """Una market buy contra el primer snapshot: fills, efectivo y slippage."""
    book = fresh_book()
    mid = book.mid
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", size, order_type=OrderType.MARKET), book)
    filled = sum(f.size for f in fills)
    eff = sum(f.price * f.size for f in fills) / filled
    print(f"  buy {size:>6}: {len(fills)} fills  eff={eff:.2f}  "
          f"slippage=+{eff - mid:.2f}")


def main():
    book = fresh_book()
    c1 = book.asks[0].size
    print(f"mid={book.mid:.2f}  mejor ask={book.asks[0].price} x {c1:.3f}")
    print("la ley del dia: mas tamano, peor precio ->")
    for size in (round(c1 * 0.5, 3), round(c1 * 2, 3), round(c1 * 5, 3)):
        sweep(size)


if __name__ == "__main__":
    main()
