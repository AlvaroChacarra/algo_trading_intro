# Clase 1 - Tu primer programa en un archivo .py
# Lo mismo que montaste en el notebook, pero en un .py de verdad.
# Ejecuta desde la terminal:  python trading_snapshot.py


def compute_spread(bid, ask):
    return ask - bid


def compute_mid(bid, ask):
    return (bid + ask) / 2


def classify_market(spread):
    if spread <= 20:
        return "tight"
    elif spread <= 60:
        return "normal"
    return "wide"


def book_pressure(book):
    buy = sum(o["size"] for o in book if o["side"] == "buy")
    sell = sum(o["size"] for o in book if o["side"] == "sell")
    return buy, sell


def main():
    bid, ask = 99950, 100000
    spread = compute_spread(bid, ask)
    mid = compute_mid(bid, ask)

    book = [
        {"side": "buy",  "price": 99980,  "size": 0.10},
        {"side": "sell", "price": 100010, "size": 0.15},
        {"side": "buy",  "price": 99970,  "size": 0.20},
    ]
    buy_vol, sell_vol = book_pressure(book)

    print("spread:", spread)
    print("mid:", mid)
    print("estado:", classify_market(spread))
    print("buy/sell:", round(buy_vol, 4), "/", round(sell_vol, 4))
    print("decision:", "buy" if mid <= 100000 else "hold")


if __name__ == "__main__":
    main()
