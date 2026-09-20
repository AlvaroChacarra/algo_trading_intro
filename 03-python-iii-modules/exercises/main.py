"""Clase 3: el mismo ejercicio que el notebook principal.

Guarda una copia como mi_main.py y traslada tu respuesta del notebook.
Desde esta carpeta: python mi_main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

# Usa los módulos y datos proporcionados junto a este notebook/script.
from pathlib import Path
import sys
exercises_folder = Path(__file__).resolve().parent
if exercises_folder.name == "solutions":
    exercises_folder = exercises_folder.parent
sys.path.insert(0, str(exercises_folder))


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
    # Completa las dos fórmulas de L1.
    return {'mid': None, 'spread': None}

def describe(orders):
    # Obtén bid, ask; reutiliza metrics.
    pass

import subprocess

import sys

from pathlib import Path


def main():
    orders = [
        {'side': 'buy', 'price': 98, 'size': 1},
        {'side': 'sell', 'price': 103, 'size': 2},
        {'side': 'buy', 'price': 99, 'size': 4},
        {'side': 'sell', 'price': 101, 'size': 1},
    ]

    print('métricas:', metrics(99,101))


    print('ambos lados:', describe(orders))


    missing = None

    print('solo compras:', missing)
    print('solo ventas:', describe([{'side':'sell','price':101}]))
    print('vacío:', describe([]))


    imported_result = None

    print('módulo proporcionado:', imported_result)
    print('tu función:', describe(orders))


    exercises_folder = Path(description_example.__file__).resolve().parent

    imported = subprocess.run([sys.executable, '-c', ''], cwd=exercises_folder,
                              capture_output=True, text=True, check=True)

    executed = subprocess.run([sys.executable, '-c', ''], cwd=exercises_folder,
                              capture_output=True, text=True, check=True)

    print('importar:', repr(imported.stdout.strip()))
    print('ejecutar:', executed.stdout.strip())
    print('cierre propio:', describe([{'side':'buy','price':98},{'side':'sell','price':102}]))



if __name__ == "__main__":
    main()
