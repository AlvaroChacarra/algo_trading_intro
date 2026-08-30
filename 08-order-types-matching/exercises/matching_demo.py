# Clase 8 - Barridos y tipos de orden, en un archivo .py
# Ejecuta desde exercises/:  python matching_demo.py

import csv
import os

from exchange.book import Level, OrderBook
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType


def fresh_book():
    path = os.path.join(os.path.dirname(__file__), "exchange", "_data",
                        "btc_lob_snapshots.csv")
    with open(path, newline="") as f:
        row = {k: float(v) for k, v in next(csv.DictReader(f)).items()}
    raw = OrderBook.from_snapshot("BTCUSDT", row, depth=10)
    binary_sizes = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0)
    return OrderBook(
        raw.symbol,
        [Level(level.price, binary_sizes[i])
         for i, level in enumerate(raw.bids)],
        [Level(level.price, binary_sizes[i])
         for i, level in enumerate(raw.asks)],
    )


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
    print("precios del snapshot + tamanos binarios normalizados")
    print("la ley del dia: mas tamano, peor precio ->")
    for size in (c1 / 2, c1 + book.asks[1].size / 2,
                 sum(level.size for level in book.asks[:3])):
        sweep(size)


if __name__ == "__main__":
    main()
