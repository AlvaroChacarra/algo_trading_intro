# main.py - importa el modulo order_book y arma + lee un libro.
# Ejecuta desde la terminal:  python main.py
import order_book


def main():
    book = []
    order_book.add_order(book, order_book.make_order("BTCUSDT", "buy", 99980, 0.10))
    order_book.add_order(book, order_book.make_order("BTCUSDT", "buy", 99990, 0.20))
    order_book.add_order(book, order_book.make_order("BTCUSDT", "sell", 100010, 0.15))

    print("best_bid:", order_book.best_bid(book))
    print("spread:", order_book.spread(book))
    print("imbalance:", round(order_book.imbalance(book), 4))


if __name__ == "__main__":
    main()
