# Clase 7 - Snapshot sintético a OrderBook, en un archivo .py
# Ejecuta desde exercises/:  python read_book.py

import csv
import os

from exchange.book import OrderBook


def describe(book):
    print(f"  mid={book.mid:.2f}  spread={book.spread:.2f}  "
          f"imb1={book.imbalance(1):+.3f}  imb5={book.imbalance(5):+.3f}  "
          f"micro={book.microprice:.2f}")


def main():
    path = os.path.join(os.path.dirname(__file__), "exchange", "_data",
                        "btc_lob_snapshots.csv")
    with open(path, newline="") as f:
        row = {k: float(v) for k, v in next(csv.DictReader(f)).items()}
    book = OrderBook.from_snapshot("BTCUSDT", row, depth=10)
    print("raw snapshot -> OrderBook:")
    describe(book)
    print(f"  depth bid(5)={book.depth('buy', 5):.3f}  "
          f"depth ask(5)={book.depth('sell', 5):.3f}")


if __name__ == "__main__":
    main()
