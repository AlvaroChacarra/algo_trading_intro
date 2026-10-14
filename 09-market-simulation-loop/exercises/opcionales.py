"""Variantes OPTIONAL. Se usan tus módulos ya completados del principal."""
import csv
from pathlib import Path
from market import ReplayMarket
from main import trade_at
from exchange.orders import Order, OrderType, Side
from scenarios import rows


def optional():
    # TODO · Ejercicio 5A: OPTIONAL · crea empty=ReplayMarket([]) y guarda dos step consecutivos en outputs.
    raise NotImplementedError('Completa 5A en opcionales.py.')
    print('5A · vacío:', outputs, empty.book)

    # TODO · Ejercicio 5B: OPTIONAL · ejecuta trade_at(rows, 0) dos veces y conserva sus carteras en first_run y second_run.
    raise NotImplementedError('Completa 5B en opcionales.py.')
    print('5B · limpio:', first_run.cash, first_run.position, second_run.cash, second_run.position)

    # TODO · Ejercicio 5C: OPTIONAL · recorre el CSV y pide BUY 0.1 cada 50 fotos hasta confirmar 1; acumula solo fills en executed y cuenta fotos en i.
    raise NotImplementedError('Completa 5C en opcionales.py.')
    print('5C · fotos / ejecutado:', i, round(executed, 6))

    # Proporcionado: energía consumida por hora, en kWh.
    lecturas = [0.4, 0.6, 1.2, 0.9, 0.3, 0.5]
    # TODO · Ejercicio 5D: OPTIONAL · recorre lecturas, suma kWh en consumido y guarda el total de cada paso en curva.
    raise NotImplementedError('Completa 5D en opcionales.py.')
    print('5D · acumulado:', [round(x,2) for x in curva])

    return locals()


if __name__ == '__main__':
    try:
        optional()
    except NotImplementedError as pending:
        print(pending)
