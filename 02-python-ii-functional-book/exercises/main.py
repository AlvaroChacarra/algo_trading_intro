"""Clase 2: el mismo ejercicio que el notebook principal.

Guarda una copia como mi_main.py y traslada tu respuesta del notebook.
Desde esta carpeta: python mi_main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

def buy_prices(orders):
    prices = []
    # Recorre orders y añade solo los precios buy.
    return prices

def best_bid(orders):
    prices = buy_prices(orders)
    if not prices:
        return None

def sell_prices(orders):
    prices = []
    # Recorre solo las ventas.
    return prices

def best_ask(orders):
    prices = sell_prices(orders)
    if not prices:
        return None

def best_prices(orders):
    # Reutiliza best_bid y best_ask.
    pass


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

    print('sin ventas:', best_prices(only_buys))
    print('sin órdenes:', best_prices([]))



if __name__ == "__main__":
    main()
