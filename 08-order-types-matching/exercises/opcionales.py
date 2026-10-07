"""Experimentos de L8. Las clases y reglas viven en sus módulos."""
import argparse
import csv
from pathlib import Path
from book import SnapshotBook
from exchange.orders import Order, OrderType, Side
from matching import (opposite_levels, take_from_level, crosses, plan_fills,
                      commit_plan, rest_limit, validate_plan, PlannedEngine,
                      effective_price, compare_engine)
from scenarios import fresh_book, book_state


def trace_process(order, book):
    # TODO · Ejercicio 7C: OPTIONAL: devuelve fills, pendiente y aceptación reutilizando las mismas fases; FOK rechazada no confirma.
    raise NotImplementedError('Completa 7C en opcionales.py.')

CHECKPOINTS = ('7A', '7B', '7C', '7D')


def practice(through=None):

    # 7A · Invierte el lado
    # TODO · Ejercicio 7A: OPTIONAL: vende 0.5 a mercado sobre sell_book y guarda sold para observar caja y bid restante.
    raise NotImplementedError('Completa 7A en opcionales.py.')
    print('7A · venta:',[(f.price,f.size) for f in sold])
    print('caja / bid restante:',sum(f.cash_flow() for f in sold),sell_book.bids[0].size)
    if through == '7A': return locals()

    # 7B · Dos tamaños caben en el mismo nivel
    # TODO · Ejercicio 7B: OPTIONAL: compara compras MARKET de 0.1 y 0.2 en libros nuevos y guarda same_prices.
    raise NotImplementedError('Completa 7B en opcionales.py.')
    print('7B · precios dentro del primer nivel:',[round(p,6) for p in same_prices])
    if through == '7B': return locals()

    # 7C · Traza un proceso sin duplicarlo
    # Comprobación 7C: completa trace_process en este archivo.
    for kind in (OrderType.MARKET,OrderType.LIMIT,OrderType.IOC,OrderType.FOK):
        traced_order=Order('BTC','buy',1,price=None if kind is OrderType.MARKET else 101,order_type=kind)
        fs,rem,accepted=trace_process(traced_order,fresh_book())
        print('7C · traza:',kind.value,len(fs),rem,accepted)
    if through == '7C': return locals()

    data_path = Path(__file__).resolve().parent / 'exchange/_data/btc_lob_snapshots.csv'
    with data_path.open(newline='') as stream:
        csv_row = next(csv.DictReader(stream))
    # 7D · Tamaño y precio en el CSV
    # TODO · Ejercicio 7D: OPTIONAL: calcula eff_prices para MARKET 0.1, 1 y 5 sobre copias nuevas de la fila sintética.
    raise NotImplementedError('Completa 7D en opcionales.py.')
    for size,price in zip((.1,1.,5.),eff_prices):
        print('7D · tamaño / precio:',size,round(price,6))
    if through == '7D': return locals()

    return locals()


def main(through=None):
    # Proporcionado: detenerse en el hueco actual no exige resolver los posteriores.
    try:
        return practice(through)
    except NotImplementedError as pending:
        print(pending)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Práctica L8 por apartados.')
    parser.add_argument('--through', choices=CHECKPOINTS)
    main(parser.parse_args().through)
