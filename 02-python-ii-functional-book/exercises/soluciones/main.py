"""Clase 2: el mismo ejercicio que el notebook principal.

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


def main():
    print('ambos lados:', best_prices(orders))
    print('solo compras:', best_prices([{'side': 'buy', 'price': 99}]))
    print('solo ventas:', best_prices([{'side': 'sell', 'price': 101}]))
    print('vacío:', best_prices([]))
    print('libro después:', orders)


if __name__ == "__main__":
    main()
