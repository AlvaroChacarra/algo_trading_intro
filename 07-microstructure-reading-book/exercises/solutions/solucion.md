# Solución · Lesson 7

Guarda tu intento y compara apartado a apartado. Cada bloque es el archivo completo
que puedes copiar en `exercises`. Conserva los mismos nombres; no copies piezas de
otras carpetas. Los comentarios repiten el encargo del main y de sus módulos;
inmediatamente debajo aparece la respuesta. Las comprobaciones proporcionadas
quedan junto a ella. `base_book.py` ya está incluido y no requiere cambios.

## `base_book.py`

```python
"""Level y OrderBook resueltos: niveles ordenados, mid e imbalance."""


class Level:
    def __init__(self, price, size):
        self.price = price
        self.size = size


class OrderBook:
    def __init__(self, bids, asks):
        self.bids = sorted(bids, key=lambda level: -level.price)
        self.asks = sorted(asks, key=lambda level: level.price)

    @property
    def mid(self):
        # Ejercicio 5.b: calcular desde los objetos actuales.
        if not self.bids or not self.asks:
            return None
        bid = self.bids[0].price
        ask = self.asks[0].price
        return (bid + ask) / 2

    def imbalance(self, levels=1):
        """Proporcionado: compara tamaños de los primeros levels de cada lado."""
        bid = sum(level.size for level in self.bids[:levels])
        ask = sum(level.size for level in self.asks[:levels])
        return (bid - ask) / (bid + ask) if bid + ask else None
```

## `adapters.py`

```python
"""La frontera de datos: vocabulario externo → niveles internos."""
from base_book import Level


def level_from_values(price, size):
    # Ejercicio 1A: convierte precio y tamaño a float; devuelve Level o None si faltan o size <= 0.
    if price is None or size is None:
        return None
    size = float(size)
    if not size > 0:
        return None
    return Level(float(price), size)


def levels_from_snapshot(row, depth):
    # Ejercicio 1B: reúne bids y asks usando level_from_values para cada sufijo de 1 a depth.
    bids, asks = [], []
    for number in range(1, depth + 1):
        for side, destination in [('bid', bids), ('ask', asks)]:
            level = level_from_values(row.get(f'{side}_price_{number}'),
                                      row.get(f'{side}_size_{number}'))
            if level is not None:
                destination.append(level)
    return bids, asks


def snapshot_to_row(raw):
    # Ejercicio 5A: adapta price/volume a price/size sin mutar raw; construye los 24 libros en main.
    row = {'timestamp': raw['timestamp']}
    for side in ('bid', 'ask'):
        for number, level in enumerate(raw[side], start=1):
            row[f'{side}_price_{number}'] = level['price']
            row[f'{side}_size_{number}'] = level['volume']
    return row

```

## `book.py`

```python
"""Un libro consultable. Level y OrderBook están incluidos en base_book.py."""
from base_book import OrderBook
from adapters import levels_from_snapshot


class SnapshotBook(OrderBook):
    def __init__(self, symbol, bids, asks):
        self.symbol = symbol
        super().__init__(bids, asks)

    @classmethod
    def from_snapshot(cls, symbol, row, depth=10):
        # Ejercicio 3A: fabrica el libro con levels_from_snapshot y devuelve cls(symbol, bids, asks).
        bids, asks = levels_from_snapshot(row, depth)
        return cls(symbol, bids, asks)

    @property
    def best_bid(self):
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self):
        return self.asks[0].price if self.asks else None

    @property
    def spread(self):
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid

    def depth(self, side, levels=10):
        # Ejercicio 4A: suma size en los primeros levels del lado buy/sell; rechaza otros lados.
        if side not in ('buy', 'sell'):
            raise ValueError('lado desconocido')
        selected = self.bids if side == 'buy' else self.asks
        return sum(level.size for level in selected[:levels])

    def imbalance(self, levels=1):
        # Ejercicio 4B: compón depth para calcular (bid - ask) / (bid + ask); total cero devuelve None.
        bid = self.depth('buy', levels)
        ask = self.depth('sell', levels)
        return (bid - ask) / (bid + ask) if bid + ask else None

    @property
    def microprice(self):
        # Ejercicio 4C: calcula microprice con pesos cruzados; un lado vacío devuelve None.
        if not self.bids or not self.asks:
            return None
        bid, ask = self.bids[0], self.asks[0]
        total = bid.size + ask.size
        if total == 0:
            return None
        return (bid.price * ask.size + ask.price * bid.size) / total
```

## `main.py`

```python
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

    # Ejercicio 2A: construye preview = OrderBook(bids, asks); el constructor ordena las parejas.
    preview = OrderBook(bids, asks)
    # Comprobación 2A
    if preview is None: return
    print('2A · Ordenados:', [(x.price, x.size) for x in preview.bids],
          [(x.price, x.size) for x in preview.asks])
    if through == '2A': return

    # Ejercicio 2B: guarda mid0 y spread0 desde preview; no vuelvas al diccionario.
    mid0 = preview.mid
    spread0 = preview.asks[0].price - preview.bids[0].price
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

    # Ejercicio 4D: consulta imbalance a 1 y 2 niveles; comprueba si cambia de signo.
    im1 = book.imbalance(1)
    im2 = book.imbalance(2)
    direction_changed = im1 * im2 < 0
    # Comprobación 4D
    if im1 is None or im2 is None: return
    print('4D · Profundidades:', round(im1, 4), round(im2, 4), direction_changed)
    if through == '4D': return

    # Ejercicio 4E: guarda tilt = microprice - mid y explica su signo.
    tilt = book.microprice - book.mid
    # Comprobación 4E
    if tilt is None: return
    print('4E · Inclinación:', tilt, 'USDT/BTC')
    if through == '4E': return

    # Ejercicio 4F: suma los dos tamaños bid de forma independiente y compara con depth.
    manual = book.bids[0].size + book.bids[1].size
    d2 = book.depth('buy',2)
    # Comprobación 4F
    if manual is None or d2 is None: return
    print('4F · Control independiente:', manual, d2)
    if through == '4F': return

    # Ejercicio 5A: adapta price/volume a price/size sin mutar raw; construye los 24 libros en main.
    rows = [snapshot_to_row(snapshot) for snapshot in raw_snapshots]
    session_books = [SnapshotBook.from_snapshot('BTCUSDT', item, 10) for item in rows]
    first_mid = session_books[0].mid
    # Comprobación 5A
    if session_books is None: return
    print('5A · Día real:', len(session_books), 'libros | primer mid:', first_mid)
    if through == '5A': return

    # Ejercicio 5B: recorre session_books y conserva el mayor mid en high.
    high = None
    for current_book in session_books:
        if current_book.mid is not None and (high is None or current_book.mid > high):
            high = current_book.mid
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
```

## `opcionales.py`

```python
"""Variantes OPTIONAL: escenarios nuevos con tus mismos módulos."""
from book import SnapshotBook
from adapters import snapshot_to_row
from lob_data import read_snapshots


def main():
    row = {'bid_price_1':'98','bid_size_1':'2',
           'ask_price_1':'103','ask_size_1':'0',
           'bid_price_2':'99','bid_size_2':'3',
           'ask_price_2':'101','ask_size_2':'1'}

    # Ejercicio 6A: OPTIONAL: omite bid_size_2 en una copia y construye changed.
    missing_column = dict(row)
    del missing_column['bid_size_2']
    changed = SnapshotBook.from_snapshot('BTCUSDT',missing_column,2)
    # Comprobación 6A
    if changed is None: return
    print('6A · Ausente:', changed.best_bid, '| original conserva tamaño:', 'bid_size_2' in row)

    # Ejercicio 6B: OPTIONAL: asigna tamaño cero al segundo bid en una copia y construye zero_book.
    zero_row = dict(row)
    zero_row['bid_size_2']='0'
    zero_book = SnapshotBook.from_snapshot('BTCUSDT',zero_row,2)
    # Comprobación 6B
    if zero_book is None: return
    print('6B · Cero:', zero_book.best_bid, '| bids:', len(zero_book.bids))

    raw_snapshots = read_snapshots()
    rows = [snapshot_to_row(raw) for raw in raw_snapshots]
    # Ejercicio 6C: OPTIONAL: consulta todos los spreads y calcula su media.
    spreads = [SnapshotBook.from_snapshot('BTCUSDT', r).spread for r in rows]
    avg_spread = sum(spreads) / len(spreads)
    # Comprobación 6C
    if avg_spread is None: return
    control = sum(raw['ask'][0]['price'] - raw['bid'][0]['price'] for raw in raw_snapshots) / len(raw_snapshots)
    print('6C · avg_spread=%.4f | control=%.4f' % (avg_spread, control))

    books = [SnapshotBook.from_snapshot('BTCUSDT', item) for item in rows]
    # Ejercicio 6D: OPTIONAL: cuenta subidas tras imbalance positivo y compara con la tasa base.
    n_pairs = len(books) - 1
    positive_cases = 0
    up_total = 0
    up_after_positive = 0
    for prev, cur in zip(books, books[1:]):
        rises = cur.mid > prev.mid
        if rises:
            up_total += 1
        signal = prev.imbalance(1)
        if signal is not None and signal > 0:
            positive_cases += 1
            if rises:
                up_after_positive += 1
    hit_rate = up_after_positive / positive_cases
    base_rate = up_total / n_pairs
    # Comprobación 6D
    if hit_rate is None or base_rate is None: return
    print(f'6D · {up_after_positive}/{positive_cases} = {hit_rate:.3f}; base {up_total}/{n_pairs} = {base_rate:.3f}')
    print('Comparación descriptiva de un día real horario; no prueba predictividad ni rentabilidad.')


if __name__ == '__main__':
    main()
```

## Respuestas y decisiones por apartado

**1A** · Los floats permiten operar. None y cantidades no positivas no fabrican liquidez. Un texto inválido conserva ValueError; no estamos saneando cualquier feed posible.

**1B** · price y size viajan juntos en un Level. El ask 103×0 se excluye; la extracción no ordena ni muta row.

**2A** · El mayor bid y el menor ask quedan en índice 0. Ordenar objetos conserva su pareja precio/cantidad.

**2B** · (99+101)/2 = 100; 101−99 = 2. Son cotizaciones, no un fill.

**3A** · @classmethod recibe la clase en cls y cls(...) ejecuta su constructor. Una hija que invoque la factory recibe una instancia de la hija. self designaría un objeto ya existente.

**4A** · buy suma 3+2 = 5 BTC; sell suma 1 BTC. Una lista vacía suma cero. Consultar conserva el estado.

**4B** · (3−1)/(3+1) = 0.5. La misma depth determina ambos totales. Total cero no admite dividir, por eso None.

**4C** · (99×1+101×3)/4 = 100.5. El peso bid favorece el precio ask por los pesos cruzados; no demuestra predicción.

**4D** · A dos niveles, (5−1)/(5+1) = 2/3. Ambos positivos: cambia la intensidad, no la dirección.

**4E** · 100.5−100 = +0.5 USDT/BTC. Se inclina hacia ask por mayor peso bid.

**4F** · La suma independiente y depth dan 5 BTC. La comprobación no vuelve a llamar dos veces al mismo método.

**5A** · volume pasa a size y se conserva el valor. Son 24 libros, primer mid 36246.474609375. El raw permanece intacto. El consumidor trabaja con objetos, no nombres del proveedor.

**5B** · El mayor mid es 37222.98046875 USDT/BTC, máximo de los 24 objetos consultados. high evita comparar con None. Ese bucle solo conoce mid.

**5C** · Depth buy se duplica a 10 BTC. Imbalance sigue en 0.5, mid en 100 y microprice en 100.5: proporciones y precios no cambian. qty en vez de volume requiere cambiar snapshot_to_row. Otras unidades requieren convertirlas allí a USDT/BTC y BTC; un cambio de significado exige revisar el contrato. La separación funciona porque mantenemos significado e interfaz internos.

**6A** · Falta el tamaño: no se construye el segundo bid. Mejor bid 98; original intacto.

**6B** · Tamaño cero: también se omite. Queda un bid a 98; la fila original no se toca.

**6C** · Media = suma de los 24 spreads / 24 = 0.4736328125 USDT/BTC. La resta directa de los raw sirve como control independiente. No es coste realizado de ejecución.

**6D** · 8 aciertos entre 13 casos positivos; la tasa base es 12/23. Cuenta también los positivos que no suben. Última foto excluida; no se conoce el siguiente mid. No se deduce rentabilidad de estas tasas.
