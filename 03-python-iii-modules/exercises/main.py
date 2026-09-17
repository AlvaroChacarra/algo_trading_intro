"""Clase 3: el mismo ejercicio que el notebook principal.

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

# Sustituye esta función por TU best_prices del notebook de L2.
def best_prices(orders):
    pass

def describe(orders):
    # Usa best_prices y devuelve las dos métricas.
    pass


def main():
    print('ambos lados:', describe(orders))
    print('solo compras:', describe([{'side': 'buy', 'price': 99}]))
    print('solo ventas:', describe([{'side': 'sell', 'price': 101}]))
    print('vacío:', describe([]))


if __name__ == "__main__":
    main()
