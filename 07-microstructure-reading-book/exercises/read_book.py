# Clase 7 - Leer el libro real, en un archivo .py
# Ejecuta desde exercises/:  python read_book.py

from exchange.market import Market
from exchange.orders import Side


def describe(book):
    print(f"  mid={book.mid:.2f}  spread={book.spread:.2f}  "
          f"imb1={book.imbalance(1):+.3f}  imb5={book.imbalance(5):+.3f}  "
          f"micro={book.microprice:.2f}")


def main():
    market = Market.sample()
    book = market.step()
    print("primer snapshot:")
    describe(book)

    high = low = book.mid
    while market.step() is not None:
        high = max(high, market.book.mid)
        low = min(low, market.book.mid)
    print(f"el dia entero: low={low:.2f}  high={high:.2f}  rango={high - low:.2f}")


if __name__ == "__main__":
    main()
