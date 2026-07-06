# order_book.py — el libro funcional de la clase 2, ahora como modulo reutilizable.


def make_order(symbol, side, price, size):
    if side not in ("buy", "sell"):
        raise ValueError("side debe ser buy o sell")
    return {"symbol": symbol, "side": side, "price": price, "size": size}


def add_order(book, order):
    book.append(order)
    return book


def cancel_order(book, order_id):
    return [o for o in book if o.get("id") != order_id]


def best_bid(book):
    return max(o["price"] for o in book if o["side"] == "buy")


def best_ask(book):
    return min(o["price"] for o in book if o["side"] == "sell")


def spread(book):
    return best_ask(book) - best_bid(book)


def imbalance(book):
    buy = sum(o["size"] for o in book if o["side"] == "buy")
    sell = sum(o["size"] for o in book if o["side"] == "sell")
    return (buy - sell) / (buy + sell)
