"""Conecta las piezas y observa; no define clases de mercado."""
from adapters import level_from_values, levels_from_snapshot, snapshot_to_row
from base_book import OrderBook
from book import SnapshotBook
from lob_data import read_snapshots
import argparse


CHECKPOINTS = ('1A', '1B', '2A', '2B', '3A', '4A', '4B', '4C',
               '4D', '4E', '4F', '5A', '5B', '5C')


def main(through=None):
    # Proporcionado: leer no adapta ni construye libros.
    raw_snapshots = read_snapshots()
    print('Archivo real:', len(raw_snapshots), 'snapshots · 24/01/2022')
    row = {'bid_price_1':'98','bid_size_1':'2',
           'ask_price_1':'103','ask_size_1':'0',
           'bid_price_2':'99','bid_size_2':'3',
           'ask_price_2':'101','ask_size_2':'1'}

    # Comprobación 1A: completa la función en adapters.py.
    level = level_from_values('98', '2')
    if level is None:
        print('Completa 1A en adapters.py para construir el primer Level.'); return
    print('1A · Level:', level.price, level.size,
          '| cero:', level_from_values('103', '0'))
    if through == '1A': return

    # Comprobación 1B: completa la función en adapters.py.
    result = levels_from_snapshot(row, 2)
    if result is None:
        print('Completa 1B en adapters.py.'); return
    bids, asks = result
    print('1B · Listas:', [(x.price, x.size) for x in bids],
          [(x.price, x.size) for x in asks])
    if through == '1B': return

    # TODO · Ejercicio 2A: construye preview = OrderBook(bids, asks); el constructor ordena las parejas.
    preview = None
    # Comprobación 2A
    if preview is None: return
    print('2A · Ordenados:', [(x.price, x.size) for x in preview.bids],
          [(x.price, x.size) for x in preview.asks])
    if through == '2A': return

    # TODO · Ejercicio 2B: guarda mid0 y spread0 desde preview; no vuelvas al diccionario.
    mid0 = spread0 = None
    # Comprobación 2B
    if mid0 is None or spread0 is None: return
    print('2B · Mid/spread:', mid0, spread0)
    if through == '2B': return

    # Comprobación 3A: completa la factory en book.py.
    book = SnapshotBook.from_snapshot('BTCUSDT', row, 2)
    if book is None: return
    print('3A · Factory:', type(book).__name__, book.symbol, book.mid)
    if through == '3A': return

    # Comprobación 4A–4C: completa estos métodos en book.py, uno a uno.
    buy, sell = book.depth('buy', 2), book.depth('sell', 2)
    if buy is None or sell is None: return
    print('4A · Depth:', buy, sell)
    if through == '4A': return
    if book.imbalance(1) is None: return
    print('4B · Imbalance:', book.imbalance(1))
    if through == '4B': return
    if book.microprice is None: return
    print('4C · Microprice:', book.microprice)
    if through == '4C': return

    # TODO · Ejercicio 4D: consulta imbalance a 1 y 2 niveles; comprueba si cambia de signo.
    im1 = im2 = direction_changed = None
    # Comprobación 4D
    if im1 is None or im2 is None: return
    print('4D · Profundidades:', round(im1, 4), round(im2, 4), direction_changed)
    if through == '4D': return

    # TODO · Ejercicio 4E: guarda tilt = microprice - mid y explica su signo.
    tilt = None
    # Comprobación 4E
    if tilt is None: return
    print('4E · Inclinación:', tilt, 'USDT/BTC')
    if through == '4E': return

    # TODO · Ejercicio 4F: suma los dos tamaños bid de forma independiente y compara con depth.
    manual = d2 = None
    # Comprobación 4F
    if manual is None or d2 is None: return
    print('4F · Control independiente:', manual, d2)
    if through == '4F': return

    # TODO · Ejercicio 5A: adapta price/volume a price/size sin mutar raw; construye los 24 libros en main.
    rows = session_books = first_mid = None
    # Comprobación 5A
    if session_books is None: return
    print('5A · Día real:', len(session_books), 'libros | primer mid:', first_mid)
    if through == '5A': return

    # TODO · Ejercicio 5B: recorre session_books y conserva el mayor mid en high.
    high = None
    # Comprobación 5B
    if high is None: return
    print('5B · Mayor mid:', high)
    if through == '5B': return

    # Lectura 5C: predice antes de ejecutar; el contraste está proporcionado.
    # Todos los niveles conservan precio y duplican cantidad en otra fila.
    doubled = {key: (float(value) * 2 if '_size_' in key else value)
               for key, value in row.items()}
    double_book = SnapshotBook.from_snapshot('BTCUSDT', doubled, 2)
    print('5C · Tamaños x2:', double_book.depth('buy', 2),
          double_book.imbalance(1), double_book.mid, double_book.microprice)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Práctica L7 por apartados.')
    parser.add_argument('--through', choices=CHECKPOINTS,
                        help='terminar después de la comprobación indicada')
    main(parser.parse_args().through)
