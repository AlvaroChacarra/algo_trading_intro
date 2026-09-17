"""Clase 1: el mismo ejercicio que el notebook principal.

Solución de referencia. Desde esta carpeta: python main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

bid = 99
ask = 101

spread = ask - bid
mid = (bid + ask) / 2


def main():
    print('spread:', spread)
    print('mid:', mid)


if __name__ == "__main__":
    main()
