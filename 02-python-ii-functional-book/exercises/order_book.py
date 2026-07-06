# Clase 2 - El libro funcional, en un archivo .py
# Las funciones que construiste en el notebook, mas un main que arma y lee un libro.
# Ejecuta desde la terminal:  python order_book.py


def make_order(symbol, side, price, size):   # ej. 1
    return {"symbol": symbol, "side": side, "price": price, "size": size}


def add_order(book, order):                  # ej. 2
    book.append(order)
    return book


def cancel_order(book, order_id):            # ej. 3
    return [o for o in book if o.get("id") != order_id]


def best_bid(book):                          # ej. 4
    return max(o["price"] for o in book if o["side"] == "buy")


def best_ask(book):                          # ej. 4
    return min(o["price"] for o in book if o["side"] == "sell")


def spread(book):                            # ej. 6
    return best_ask(book) - best_bid(book)


def mid(book):                               # ej. 6
    return (best_bid(book) + best_ask(book)) / 2


def imbalance(book):                         # ej. 5
    buy = sum(o["size"] for o in book if o["side"] == "buy")
    sell = sum(o["size"] for o in book if o["side"] == "sell")
    return (buy - sell) / (buy + sell)


def main():                                  # ej. 7: construir y leer el libro
    book = []
    book = add_order(book, make_order("BTCUSDT", "buy", 99980, 0.10))
    book = add_order(book, make_order("BTCUSDT", "buy", 99990, 0.20))
    book = add_order(book, make_order("BTCUSDT", "sell", 100010, 0.15))

    print("ordenes:", len(book))
    print("best_bid:", best_bid(book))
    print("best_ask:", best_ask(book))
    print("spread:", spread(book))
    print("mid:", mid(book))
    print("imbalance:", round(imbalance(book), 4))
    # Fijate: TODAS estas funciones reciben book. En la clase 3, book sera un objeto.


if __name__ == "__main__":
    main()
