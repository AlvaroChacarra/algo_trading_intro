# Referencia resuelta generada desde el principal; no sustituye tus funciones.
orders = [
    {'side': 'buy', 'price': 98, 'size': 1},
    {'side': 'sell', 'price': 103, 'size': 2},
    {'side': 'buy', 'price': 99, 'size': 4},
    {'side': 'sell', 'price': 101, 'size': 1},
]
def buy_prices(orders):
    prices = []
    for order in orders:
        if order['side'] == 'buy':
            prices.append(order['price'])
    return prices


def best_bid(orders):
    prices = buy_prices(orders)
    if not prices:
        return None
    return max(prices)


def sell_prices(orders):
    prices = []
    for order in orders:
        if order['side'] == 'sell':
            prices.append(order['price'])
    return prices

def best_ask(orders):
    prices = sell_prices(orders)
    if not prices:
        return None
    return min(prices)


def best_prices(orders):
    return best_bid(orders), best_ask(orders)


def metrics(bid, ask):
    if bid is None or ask is None:
        return {'mid': None, 'spread': None}
    return {'mid': (bid + ask) / 2, 'spread': ask - bid}


def describe(orders):
    bid, ask = best_prices(orders)
    return metrics(bid, ask)

def main():
    print(describe(orders))

if __name__ == "__main__":
    main()
