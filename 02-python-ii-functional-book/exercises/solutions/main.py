"""Clase 2: el mismo ejercicio que el notebook principal.

Solución de referencia. Desde esta carpeta: python main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

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


def main():
    orders = [
        {'side': 'buy', 'price': 98, 'size': 1},
        {'side': 'sell', 'price': 103, 'size': 2},
        {'side': 'buy', 'price': 99, 'size': 4},
        {'side': 'sell', 'price': 101, 'size': 1},
    ]

    print('compras:', buy_prices(orders))


    print('bid:', best_bid(orders))


    print('ventas:', sell_prices(orders))
    print('ask:', best_ask(orders))


    print('bid, ask:', best_prices(orders))
    print('órdenes:', orders)


    only_buys = []

    for order in orders:
        if order['side'] == 'buy':
            only_buys.append(order)

    print('sin ventas:', best_prices(only_buys))
    print('sin órdenes:', best_prices([]))



if __name__ == "__main__":
    main()
