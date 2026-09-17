"""Clase 2: el mismo ejercicio que el notebook principal.

Guarda una copia como mi_main.py y traslada tu respuesta del notebook.
Desde esta carpeta: python mi_main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

orders = [
    {'side': 'buy', 'price': 98, 'size': 1},
    {'side': 'sell', 'price': 103, 'size': 2},
    {'side': 'buy', 'price': 99, 'size': 4},
    {'side': 'sell', 'price': 101, 'size': 1},
]

def best_prices(orders):
    # Selecciona un precio por lado y devuelve el par.
    pass


def main():
    print('ambos lados:', best_prices(orders))
    print('solo compras:', best_prices([{'side': 'buy', 'price': 99}]))
    print('solo ventas:', best_prices([{'side': 'sell', 'price': 101}]))
    print('vacío:', best_prices([]))
    print('libro después:', orders)


if __name__ == "__main__":
    main()
