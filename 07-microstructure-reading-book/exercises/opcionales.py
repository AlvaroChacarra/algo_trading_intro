"""Variantes OPTIONAL: escenarios nuevos con tus mismos módulos."""
from book import SnapshotBook
from adapters import snapshot_to_row
from lob_data import read_snapshots


def main():
    row = {'bid_price_1':'98','bid_size_1':'2',
           'ask_price_1':'103','ask_size_1':'0',
           'bid_price_2':'99','bid_size_2':'3',
           'ask_price_2':'101','ask_size_2':'1'}

    # TODO · Ejercicio 6A: OPTIONAL: omite bid_size_2 en una copia y construye changed.
    changed = None
    # Comprobación 6A
    if changed is None: return
    print('6A · Ausente:', changed.best_bid, '| original conserva tamaño:', 'bid_size_2' in row)

    # TODO · Ejercicio 6B: OPTIONAL: asigna tamaño cero al segundo bid en una copia y construye zero_book.
    zero_book = None
    # Comprobación 6B
    if zero_book is None: return
    print('6B · Cero:', zero_book.best_bid, '| bids:', len(zero_book.bids))

    raw_snapshots = read_snapshots()
    rows = [snapshot_to_row(raw) for raw in raw_snapshots]
    # TODO · Ejercicio 6C: OPTIONAL: consulta todos los spreads y calcula su media.
    spreads = avg_spread = None
    # Comprobación 6C
    if avg_spread is None: return
    control = sum(raw['ask'][0]['price'] - raw['bid'][0]['price'] for raw in raw_snapshots) / len(raw_snapshots)
    print('6C · avg_spread=%.4f | control=%.4f' % (avg_spread, control))

    books = [SnapshotBook.from_snapshot('BTCUSDT', item) for item in rows]
    # TODO · Ejercicio 6D: OPTIONAL: cuenta subidas tras imbalance positivo y compara con la tasa base.
    n_pairs = positive_cases = up_total = up_after_positive = None
    hit_rate = base_rate = None
    # Comprobación 6D
    if hit_rate is None or base_rate is None: return
    print(f'6D · {up_after_positive}/{positive_cases} = {hit_rate:.3f}; base {up_total}/{n_pairs} = {base_rate:.3f}')
    print('Comparación descriptiva de un día real horario; no prueba predictividad ni rentabilidad.')


if __name__ == '__main__':
    main()
