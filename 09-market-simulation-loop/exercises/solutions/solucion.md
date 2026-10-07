# Solución · Lesson 9

Consulta el apartado después de intentarlo. Cada archivo aparece **una sola vez completo**: copia su bloque, incluidos imports y guard de ejecución. El comentario `# Ejercicio 1A: …` repite el encargo y la implementación está inmediatamente debajo. Mantén tus intentos guardados; las bases incluidas no son nuevos ejercicios.

## Respuestas y decisiones por apartado

**1A** · Guarda rows como lista, symbol, depth y PlannedEngine; deja _i=-1 y book=None. -1 None; cada instancia conserva su propio cursor y motor.

**1B** · Avanza _i una vez; devuelve un SnapshotBook nuevo o limpia book y devuelve None al agotarse. 0 100.0 0; repetir step con datos agotados mantiene book=None.

**1C** · Exige un libro activo y devuelve engine.process(order, book, timestamp), sin avanzar _i. cursor 0; cash 899; position 1; ask restante 2 y equity 999.

**1D** · Restaura _i=-1 y book=None, conservando las filas y el motor. segunda foto: cursor 1, mid 102, equity 1001 y ask 3. Fin: None. Reset: -1/None; cartera 899/1.

**2A** · Intenta enviar antes del primer step, captura solo RuntimeError y guarda rejected=True. sin foto: True; una foto activa es la precondición de submit.

**2B** · Reinicia market, visita cada foto hasta None y devuelve sus mids en una lista. [100.0, 102.0] en ambos recorridos; vacío []. Al terminar ya no hay market.book.

**3A** · Usa mids_of para devolver el primer y último mid; si no hay fotos devuelve (None, None). (100.0, 102.0) y (None, None). No son libros persistentes.

**3B** · Recorre todas las filas, compra una unidad solo en el índice at y devuelve fills, tracker y marks. En índice 0: caja899 y equity final1001; en 1: caja897 y equity999; en9: posición0 y equity1000. Cambia el precio de ejecución, no el reloj.

**4A** · Lee csv_path con DictReader y usa trade_at en el índice 9 con symbol="BTCUSDT"; guarda los resultados de la sesión. 500 marks. Position coincide con la cantidad ejecutada. Todos los fills pertenecen a BTCUSDT. El mismo reloj sirve para filas textuales.

**4B** · Envía LIMIT BUY 0.5 a 98 en la primera foto, aplica solo sus fills y observa bid98, cursor y cartera antes y después de step. Cero fills; bid98 True→False; (0,1000,0)→(1,1000,0). Se reemplaza la foto; no hay una cola de órdenes que sobreviva ni datos de eventos entre fotos.

**5A** · Crea empty=ReplayMarket([]) y guarda dos step consecutivos en outputs. [None, None]; book=None.

**5B** · Ejecuta trade_at(rows, 0) dos veces y conserva sus carteras en first_run y second_run. 899/1 y899/1. Reiniciar solo el mercado conserva una cartera externa; no debe duplicarse la compra al comparar experimentos nuevos.

**5C** · Recorre el CSV y pide BUY 0.1 cada 50 fotos hasta confirmar 1; acumula solo fills en executed y cuenta fotos en i. 500 fotos y executed1.0. El calendario cuenta tiempo; los fills cuentan unidades.

**5D** · Recorre lecturas, suma kWh en consumido y guarda el total de cada paso en curva. [0.4,1.0,2.2,3.1,3.4,3.9]. Total3.9kWh; equity=cash+position×mid en cada foto, no acumulación de precios.

## `market.py`

```python
"""El reloj del replay. El matching y la cartera tienen responsabilidades propias."""
from book import SnapshotBook
from matching import PlannedEngine


class ReplayMarket:
    def __init__(self, rows, symbol='BTC', depth=10):
        # Ejercicio 1A: guarda rows como lista, symbol, depth y PlannedEngine; deja _i=-1 y book=None.
        self.rows = list(rows)
        self.symbol = symbol
        self.depth = depth
        self.engine = PlannedEngine()
        self._i = -1
        self.book = None

    @property
    def timestamp(self):
        if self.book is None:
            return None
        return int(float(self.rows[self._i].get('timestamp', self._i)))

    def step(self):
        # Ejercicio 1B: avanza _i una vez; devuelve un SnapshotBook nuevo o limpia book y devuelve None al agotarse.
        self._i += 1
        if self._i >= len(self.rows):
            self.book = None
            return None
        self.book = SnapshotBook.from_snapshot(self.symbol, self.rows[self._i], self.depth)
        return self.book

    def submit(self, order):
        # Ejercicio 1C: exige un libro activo y devuelve engine.process(order, book, timestamp), sin avanzar _i.
        if self.book is None:
            raise RuntimeError('llama a step antes de enviar una orden')
        return self.engine.process(order, self.book, self.timestamp)

    def reset(self):
        # Ejercicio 1D: restaura _i=-1 y book=None, conservando las filas y el motor.
        self._i = -1
        self.book = None
```

## `main.py`

```python
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
    # Ejercicio 2B: reinicia market, visita cada foto hasta None y devuelve sus mids en una lista.
    market.reset()
    mids = []
    while True:
        book = market.step()
        if book is None:
            break
        mids.append(book.mid)
    return mids


def endpoints(market):
    # Ejercicio 3A: usa mids_of para devolver el primer y último mid; si no hay fotos devuelve (None, None).
    mids = mids_of(market)
    return (mids[0], mids[-1]) if mids else (None, None)


def trade_at(rows, at, symbol="BTC"):
    # Ejercicio 3B: recorre todas las filas, compra una unidad solo en el índice at y devuelve fills, tracker y marks.
    market = ReplayMarket(rows, symbol=symbol)
    tracker = PositionTracker(1000)
    fills, marks = [], []
    while True:
        book = market.step()
        if book is None:
            break
        marks.append(book.mid)
        if market._i == at:
            for fill in market.submit(Order(symbol, 'buy', 1, order_type=OrderType.MARKET)):
                tracker.apply_fill(fill)
                fills.append(fill)
    return fills, tracker, marks


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

    # Ejercicio 2A: intenta enviar antes del primer step, captura solo RuntimeError y guarda rejected=True.
    rejected = False
    try:
        ReplayMarket(rows).submit(Order('BTC', 'buy', 1, order_type=OrderType.MARKET))
    except RuntimeError:
        rejected = True
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
    # Ejercicio 4A: lee csv_path con DictReader y usa trade_at en el índice 9 con symbol="BTCUSDT"; guarda los resultados de la sesión.
    with csv_path.open() as handle:
        session_rows = list(csv.DictReader(handle))
    session_fills, session_tracker, session_marks = trade_at(session_rows, 9, symbol="BTCUSDT")
    print('4A · cierre CSV:', len(session_marks), session_marks[0], session_marks[-1])
    print('fills/posición:', len(session_fills), round(session_tracker.position, 9))
    print('equity final:', round(session_tracker.equity(session_marks[-1]), 6))
    if through == '4A': return locals()

    # Ejercicio 4B: envía LIMIT BUY 0.5 a 98 en la primera foto, aplica solo sus fills y observa bid98, cursor y cartera antes y después de step.
    limit_market = ReplayMarket(rows)
    limit_tracker = PositionTracker(1000)
    limit_market.step()
    limit_fills = limit_market.submit(Order('BTC', 'buy', .5, price=98, order_type=OrderType.LIMIT))
    for fill in limit_fills:
        limit_tracker.apply_fill(fill)
    pending_before = any(level.price == 98 for level in limit_market.book.bids)
    before = (limit_market._i, limit_tracker.cash, limit_tracker.position)
    limit_market.step()
    pending_after = any(level.price == 98 for level in limit_market.book.bids)
    after = (limit_market._i, limit_tracker.cash, limit_tracker.position)
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
```

## `opcionales.py`

```python
"""Variantes OPTIONAL. Se usan tus módulos ya completados del principal."""
import csv
from pathlib import Path
from market import ReplayMarket
from main import trade_at
from exchange.orders import Order, OrderType, Side
from scenarios import rows


def optional():
    # Ejercicio 5A: OPTIONAL · crea empty=ReplayMarket([]) y guarda dos step consecutivos en outputs.
    empty = ReplayMarket([])
    outputs = [empty.step(), empty.step()]
    print('5A · vacío:', outputs, empty.book)

    # Ejercicio 5B: OPTIONAL · ejecuta trade_at(rows, 0) dos veces y conserva sus carteras en first_run y second_run.
    first_run = trade_at(rows,0)[1]
    second_run = trade_at(rows,0)[1]
    print('5B · limpio:', first_run.cash, first_run.position, second_run.cash, second_run.position)

    # Ejercicio 5C: OPTIONAL · recorre el CSV y pide BUY 0.1 cada 50 fotos hasta confirmar 1; acumula solo fills en executed y cuenta fotos en i.
    with (Path(__file__).resolve().parent / 'exchange/_data/btc_lob_snapshots.csv').open(newline='') as handle:
        schedule_rows = list(csv.DictReader(handle))
    m = ReplayMarket(schedule_rows, symbol="BTCUSDT"); i = 0; executed = 0.0
    while True:
        book = m.step()
        if book is None: break
        if i % 50 == 0 and executed < 1.0 - 1e-9:
            for f in m.submit(Order('BTCUSDT', Side.BUY, 0.1, order_type=OrderType.MARKET)):
                executed += f.size
        i += 1
    print('5C · fotos / ejecutado:', i, round(executed, 6))

    # Proporcionado: energía consumida por hora, en kWh.
    lecturas = [0.4, 0.6, 1.2, 0.9, 0.3, 0.5]
    # Ejercicio 5D: OPTIONAL · recorre lecturas, suma kWh en consumido y guarda el total de cada paso en curva.
    consumido = 0.0
    curva = []
    for x in lecturas:
        consumido += x
        curva.append(consumido)
    print('5D · acumulado:', [round(x,2) for x in curva])

    return locals()


if __name__ == '__main__':
    try:
        optional()
    except NotImplementedError as pending:
        print(pending)
```

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

## `matching.py`

```python
"""Tu matching engine: funciones pequeñas y una clase que las conecta."""
from base_book import Level
from exchange.orders import Order, OrderType, Side
from exchange.trades import Fill as ExecutionFill
from scenarios import fresh_book, book_state, fill_signature

# Proporcionado: solo compare_engine usa este oráculo independiente.
from exchange.book import OrderBook as ReferenceBook, Level as ReferenceLevel
from exchange.matching import MatchingEngine as ReferenceEngine

EPS = 1e-12


def opposite_levels(order, book):
    # Ejercicio 1A: devuelve los asks para BUY y los bids para SELL, conservando la lista del libro.
    return book.asks if order.side is Side.BUY else book.bids


def take_from_level(remaining, level):
    # Ejercicio 1B: devuelve take = min(remaining, level.size) y el nuevo pendiente, sin modificar el nivel.
    take = min(remaining, level.size)
    return take, max(0.0, remaining - take)


def crosses(order, level_price):
    # Ejercicio 1C: acepta cualquier precio en MARKET; en las demás políticas compara el límite según BUY o SELL.
    if order.order_type is OrderType.MARKET:
        return True
    if order.side is Side.BUY:
        return level_price <= order.price
    return level_price >= order.price


def plan_fills(order, levels):
    # Ejercicio 2A: construye pares (level, take) con crosses y take_from_level; devuelve plan y pendiente sin mutar.
    remaining = order.size
    plan = []
    for level in levels:
        if remaining <= EPS or not crosses(order, level.price):
            break
        take, remaining = take_from_level(remaining, level)
        if take > EPS:
            plan.append((level, take))
    return plan, max(0.0, remaining)


def commit_plan(order, book, plan, timestamp=None):
    # Ejercicio 2B: consume cada par del plan, crea ExecutionFill con timestamp y retira niveles agotados.
    fills = []
    for level, take in plan:
        level.size -= take
        fills.append(ExecutionFill(order.id, order.symbol, order.side,
                                   level.price, take, timestamp))
    book.bids[:] = [lv for lv in book.bids if lv.size > EPS]
    book.asks[:] = [lv for lv in book.asks if lv.size > EPS]
    return fills


def rest_limit(order, book, remaining):
    # Ejercicio 3D: añade el remanente LIMIT al lado propio, agrega cantidades al mismo precio y conserva el orden.
    if remaining <= EPS:
        return
    own = book.bids if order.side is Side.BUY else book.asks
    for level in own:
        if level.price == order.price:
            level.size += remaining
            break
    else:
        own.append(Level(order.price, remaining))
    own.sort(key=lambda lv: -lv.price if order.side is Side.BUY else lv.price)


def validate_plan(order, remaining):
    # Ejercicio 3F: acepta FOK solo si el pendiente es cero dentro de EPS; las demás políticas admiten parciales.
    return order.order_type is not OrderType.FOK or remaining <= EPS


class PlannedEngine:
    def process(self, order, book, timestamp=None):
        # Ejercicio 4A: conecta selección, plan, validación, commit y remanente LIMIT en process; transmite timestamp.
        if order.symbol != book.symbol:
            raise ValueError("orden y libro deben tener el mismo símbolo")
        levels = opposite_levels(order, book)
        plan, remaining = plan_fills(order, levels)
        if not validate_plan(order, remaining):
            return []
        fills = commit_plan(order, book, plan, timestamp)
        if order.order_type is OrderType.LIMIT and remaining > EPS:
            rest_limit(order, book, remaining)
        return fills


def effective_price(fills):
    # Ejercicio 5A: devuelve el precio ponderado por tamaño de los fills, o None cuando no hay ejecución.
    quantity = sum(fill.size for fill in fills)
    if quantity == 0:
        return None
    return sum(fill.price * fill.size for fill in fills) / quantity


def compare_engine(engine_class, side, size, kind, price=None):
    # Ejercicio 6B: compara los fills y ambos lados finales de tu motor con la referencia sobre libros nuevos.
    student_book = fresh_book()
    reference_book = ReferenceBook('BTC',[ReferenceLevel(99,1)],
                                    [ReferenceLevel(101,.4),ReferenceLevel(102,1.6)])
    first = Order('BTC',side,size,price=price,order_type=kind)
    second = Order('BTC',side,size,price=price,order_type=kind)
    student_fills = engine_class().process(first,student_book)
    reference_fills = ReferenceEngine().process(second,reference_book)
    return (fill_signature(student_fills)==fill_signature(reference_fills)
            and book_state(student_book)==book_state(reference_book))
```

## `portfolio.py`

```python
"""La cartera conserva estado; Fill proporciona el flujo de cada ejecución."""


class PositionTracker:
    def __init__(self, cash=0.0):
        # Ejercicio 1.a
        self.cash = cash
        self.position = 0.0

    def apply_fill(self, fill):
        # Ejercicio 2.a: usar el comportamiento del Fill de L4.
        self.cash += fill.cash_flow()
        if fill.side == 'buy':
            self.position += fill.size
        else:
            self.position -= fill.size

    def equity(self, mark):
        # Ejercicio 3.a: consultar, sin cambiar atributos.
        return self.cash + self.position * mark
```
