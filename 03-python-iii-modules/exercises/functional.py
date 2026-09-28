"""Lesson 2 — funciones reutilizables que Lesson 3 importa como módulo."""


def make_order(side, price, size):
    if side not in ("buy", "sell"):
        raise ValueError("side debe ser 'buy' o 'sell'")
    if price <= 0:
        raise ValueError("price debe ser positivo")
    if size <= 0:
        raise ValueError("size debe ser positivo")
    return {"side": side, "price": price, "size": size}


def best_prices(orders):
    buys = [order["price"] for order in orders if order["side"] == "buy"]
    sells = [order["price"] for order in orders if order["side"] == "sell"]

    bid = max(buys) if buys else None
    ask = min(sells) if sells else None

    return bid, ask
