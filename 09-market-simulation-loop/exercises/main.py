"""Experimentos de L9: observar tiempo, liquidez y cartera por separado."""
import argparse
import csv
from pathlib import Path
from market import ReplayMarket
from portfolio import PositionTracker
from book import SnapshotBook
from exchange.orders import Order, OrderType
from scenarios import rows


def mids_of(market):
    # TODO · Ejercicio 2B: reinicia market, visita cada foto hasta None y devuelve sus mids en una lista.
    raise NotImplementedError('Completa 2B en main.py.')


def endpoints(market):
    # TODO · Ejercicio 3A: usa mids_of para devolver el primer y último mid; si no hay fotos devuelve (None, None).
    raise NotImplementedError('Completa 3A en main.py.')


def trade_at(rows, at, symbol="BTC"):
    # TODO · Ejercicio 3B: recorre todas las filas, compra una unidad solo en el índice at y devuelve fills, tracker y marks.
    raise NotImplementedError('Completa 3B en main.py.')


CHECKPOINTS = ('1A', '1B', '1C', '1D', '2A', '2B', '3A', '3B', '4A', '4B')


def practice(through=None):
    # Proporcionado: primer resultado sin resolver los huecos.
    print('Dos fotos · mids: 100 → 102 · caja inicial: 1000 USD · compra: 1 BTC')
    # Comprobación 1A: completa ReplayMarket.__init__ en market.py.
    market = ReplayMarket(rows)
    print('1A · inicio:', market._i, market.book)
    if through == '1A': return locals()

    # Comprobación 1B: completa ReplayMarket.step en market.py.
    first = market.step()
    print('1B · primera foto:', market._i, first.mid, market.timestamp)
    if through == '1B': return locals()

    # Comprobación 1C: completa ReplayMarket.submit en market.py.
    tracker = PositionTracker(1000)
    fills = market.submit(Order('BTC', 'buy', 1, order_type=OrderType.MARKET))
    for fill in fills:
        tracker.apply_fill(fill)
    print('1C · tras compra:', market._i, tracker.cash, tracker.position)
    print('ask restante:', first.asks[0].size, '| equity:', tracker.equity(100))
    if through == '1C': return locals()

    second = market.step()
    print('segunda foto:', market._i, second.mid, tracker.equity(second.mid))
    print('libro nuevo:', second is not first, '| ask:', second.asks[0].size)
    print('fin:', market.step(), market.book, market.timestamp)
    # Comprobación 1D: completa ReplayMarket.reset en market.py.
    market.reset()
    print('1D · reset:', market._i, market.book, tracker.cash, tracker.position)
    if through == '1D': return locals()

    # TODO · Ejercicio 2A: intenta enviar antes del primer step, captura solo RuntimeError y guarda rejected=True.
    raise NotImplementedError('Completa 2A en main.py.')
    print('2A · sin foto:', rejected)
    if through == '2A': return locals()

    # Comprobación 2B: completa mids_of en main.py.
    replay = ReplayMarket(rows)
    print('2B · recorrido:', mids_of(replay))
    print('repetición:', mids_of(replay))
    print('vacío:', mids_of(ReplayMarket([])))
    if through == '2B': return locals()

    # Comprobación 3A: completa endpoints en main.py.
    print('3A · apertura/cierre:', endpoints(ReplayMarket(rows)))
    print('sesión vacía:', endpoints(ReplayMarket([])))
    if through == '3A': return locals()

    # Comprobación 3B: completa trade_at en main.py.
    for at in (0, 1, 9):
        trades, portfolio, marks = trade_at(rows, at)
        print('3B · momento:', at, len(trades), portfolio.cash, portfolio.position, portfolio.equity(marks[-1]))
    if through == '3B': return locals()

    # Proporcionado: ruta relativa al archivo; funciona desde cualquier carpeta.
    csv_path = Path(__file__).resolve().parent / 'exchange/_data/btc_lob_snapshots.csv'
    # TODO · Ejercicio 4A: lee csv_path con DictReader y usa trade_at en el índice 9 con symbol="BTCUSDT"; guarda los resultados de la sesión.
    raise NotImplementedError('Completa 4A en main.py.')
    print('4A · cierre CSV:', len(session_marks), session_marks[0], session_marks[-1])
    print('fills/posición:', len(session_fills), round(session_tracker.position, 9))
    print('equity final:', round(session_tracker.equity(session_marks[-1]), 6))
    if through == '4A': return locals()

    # TODO · Ejercicio 4B: envía LIMIT BUY 0.5 a 98 en la primera foto, aplica solo sus fills y observa bid98, cursor y cartera antes y después de step.
    raise NotImplementedError('Completa 4B en main.py.')
    print('4B · LIMIT: fills / bid98:', len(limit_fills), pending_before, pending_after)
    print('antes / después:', before, after)
    return locals()


def main(through=None):
    # Proporcionado: una pausa útil en el apartado pendiente.
    try:
        return practice(through)
    except NotImplementedError as pending:
        print(pending)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Práctica L9 por apartados.')
    parser.add_argument('--through', choices=CHECKPOINTS)
    main(parser.parse_args().through)
