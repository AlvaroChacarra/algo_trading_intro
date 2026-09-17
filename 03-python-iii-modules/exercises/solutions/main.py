"""Clase 3: el mismo ejercicio que el notebook principal.

Solución de referencia. Desde esta carpeta: python main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

orders = [
    {'side': 'buy', 'price': 98, 'size': 1},
    {'side': 'sell', 'price': 103, 'size': 2},
    {'side': 'buy', 'price': 99, 'size': 4},
    {'side': 'sell', 'price': 101, 'size': 1},
]

def best_prices(orders):
    buys = [order['price'] for order in orders if order['side'] == 'buy']
    sells = [order['price'] for order in orders if order['side'] == 'sell']
    bid = max(buys) if buys else None
    ask = min(sells) if sells else None
    return bid, ask

def describe(orders):
    bid, ask = best_prices(orders)
    if bid is None or ask is None:
        return {'mid': None, 'spread': None}
    return {'mid': (bid + ask) / 2, 'spread': ask - bid}


def main():
    print('ambos lados:', describe(orders))
    print('solo compras:', describe([{'side': 'buy', 'price': 99}]))
    print('solo ventas:', describe([{'side': 'sell', 'price': 101}]))
    print('vacío:', describe([]))


if __name__ == "__main__":
    main()
