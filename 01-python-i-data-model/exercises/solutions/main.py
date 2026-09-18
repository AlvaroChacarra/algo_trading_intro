"""Clase 1: el mismo ejercicio que el notebook principal.

Solución de referencia. Desde esta carpeta: python main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

bid = 99
ask = 101
quotes = [
    {"bid": 99, "ask": 101},
    {"bid": 99, "ask": 103},
]

spread = ask - bid
mid = (bid + ask) / 2

results = []
for quote in quotes:
    quote_spread = quote["ask"] - quote["bid"]
    quote_mid = (quote["bid"] + quote["ask"]) / 2
    if quote_spread <= 2:
        state = "estrecho"
    else:
        state = "amplio"
    results.append({"spread": quote_spread, "mid": quote_mid, "state": state})


def main():
    print('spread:', spread)
    print('mid:', mid)
    print('resúmenes:', results)


if __name__ == "__main__":
    main()
