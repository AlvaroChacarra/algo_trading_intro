"""Clase 1: el mismo ejercicio que el notebook principal.

Guarda una copia como mi_main.py y traslada tu respuesta del notebook.
Desde esta carpeta: python mi_main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

bid = 99
ask = 101
quotes = [
    {"bid": 99, "ask": 101},
    {"bid": 99, "ask": 103},
]

spread = None  # pendiente
mid = None  # pendiente

results = []
for quote in quotes:
    quote_spread = None  # pendiente
    quote_mid = None  # pendiente
    if quote["ask"] - quote["bid"] <= 2:
        state = None  # etiqueta pendiente
    else:
        state = None  # etiqueta pendiente
    results.append({"spread": quote_spread, "mid": quote_mid, "state": state})


def main():
    print('spread:', spread)
    print('mid:', mid)
    print('resúmenes:', results)


if __name__ == "__main__":
    main()
