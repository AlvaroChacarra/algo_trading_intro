# Clase 1 - Tu primer programa en un archivo .py
# Lo mismo que construiste en el notebook (ej. 1 a 7), ordenado en funciones.
# Ejecuta desde la terminal:  python trading_snapshot.py


def compute_spread(bid, ask):          # ej. 2
    return ask - bid


def compute_mid(bid, ask):             # ej. 2
    return (bid + ask) / 2


def average(values):                   # ej. 3 y 4: lista + for
    total = 0
    for v in values:
        total = total + v
    return total / len(values)


def order_notional(order):             # ej. 5: acceder a un dict
    return order["price"] * order["size"]


def classify_market(spread):           # ej. 6: if / elif / else
    if spread <= 20:
        return "tight"
    elif spread <= 60:
        return "normal"
    return "wide"


def decide(mid):                       # ej. 7: la decisión sobre el mid
    if mid <= 100000:
        return "buy"
    return "hold"


def main():                            # ej. 7: dato -> calculo -> decision
    symbol = "BTCUSDT"
    bid, ask = 99950, 100000

    spread = compute_spread(bid, ask)
    mid = compute_mid(bid, ask)

    mids = [99975, 99980, 99970, 99990, 100005]
    order = {"symbol": symbol, "side": "buy", "price": 99950, "size": 0.10}

    print("symbol:", symbol)
    print("spread:", spread)
    print("mid:", mid)
    print("media de mids:", average(mids))
    print("nocional de la orden:", order_notional(order))
    print("estado:", classify_market(spread))
    print("decision:", decide(mid))


if __name__ == "__main__":
    main()
