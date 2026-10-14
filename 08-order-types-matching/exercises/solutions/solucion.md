# Solución · Lesson 8

Busca el apartado y el comentario con el mismo encargo dentro del archivo.
Cada bloque es el archivo completo para copiar junto a los recursos de esta lesson.
Las anotaciones heredadas de L5/L7 identifican su procedencia; no son tareas de L8.
Los módulos `exchange/` y `scenarios.py` están proporcionados: no se reconstruyen.

| Apartados | Archivo y símbolo |
| --- | --- |
| 1A–1C | matching.py: opposite_levels, take_from_level, crosses |
| 2A–2B | matching.py: plan_fills, commit_plan |
| 3A–3C | main.py: libro nuevo, profundidad y planes limitados |
| 3D / 3F | matching.py: rest_limit / validate_plan |
| 3E | main.py: observación IOC |
| 4A / 4B | matching.py: PlannedEngine.process / main.py: orden pequeña |
| 5A / 5B–5C | matching.py: effective_price / main.py: coste y tamaños |
| 6A / 6B | main.py: CSV / matching.py: compare_engine |
| 6C | Predicción y respuesta textual; contraste proporcionado en main.py |
| 7A–7D | opcionales.py: variantes OPTIONAL |

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

## `main.py`

```python
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


CHECKPOINTS = ('1A', '1B', '1C', '2A', '2B', '3A', '3B', '3C', '3D', '3E', '3F', '4A', '4B', '5A', '5B', '5C', '6A', '6B', '6C')


def practice(through=None):
    # Proporcionado: primer resultado, incluso con todos los TODO pendientes.
    book = fresh_book()
    print('Libro inicial · bids:', book_state(book)[0], '| asks:', book_state(book)[1])
    order = Order('BTC', 'buy', 1, order_type=OrderType.MARKET)

    # 1A · Selecciona el lado contrario
    # Comprobación 1A: completa opposite_levels en matching.py.
    levels = opposite_levels(order, book)
    print('1A · niveles contrarios:', [(lv.price,lv.size) for lv in levels])
    print('misma lista del libro:', levels is book.asks)
    if through == '1A': return locals()

    # 1B · Calcula take y remaining
    # Comprobación 1B: completa take_from_level en matching.py.
    take, pending = take_from_level(order.size, levels[0])
    print('1B · take / remaining:', take, pending)
    print('nivel intacto:', levels[0].size)
    if through == '1B': return locals()

    # 1C · Decide si el precio cruza
    # Comprobación 1C: completa crosses en matching.py.
    limited = Order('BTC','buy',1,price=101,order_type=OrderType.LIMIT)
    print('1C · compra limitada:', [crosses(limited, lv.price) for lv in levels])
    if through == '1C': return locals()

    # 2A · Construye un único plan
    # Comprobación 2A: completa plan_fills en matching.py.
    plan, remaining = plan_fills(order, levels)
    print('2A · plan MARKET:', [(lv.price, qty) for lv,qty in plan])
    print('remanente:', remaining)
    print('tamaños tras plan:', [lv.size for lv in levels])
    if through == '2A': return locals()

    # 2B · Aplica el plan y crea fills
    # Comprobación 2B: completa commit_plan en matching.py.
    # Cada observación reconstruye el estado y recalcula el plan con tus funciones.
    book = fresh_book()
    order = Order('BTC', 'buy', 1, order_type=OrderType.MARKET)
    levels = opposite_levels(order, book)
    plan, remaining = plan_fills(order, levels)
    fills = commit_plan(order, book, plan, timestamp=7)
    print('2B · fills MARKET:', [(f.price,f.size) for f in fills])
    print('asks finales:', [(lv.price,lv.size) for lv in book.asks])
    print('timestamp / caja:', fills[0].timestamp, sum(f.cash_flow() for f in fills))
    if through == '2B': return locals()

    # 3A · Recupera una foto limpia
    # Ejercicio 3A: crea clean con fresh_book y consulta su mid y spread antes de comparar políticas.
    clean = fresh_book()
    mid0 = clean.mid
    spread0 = clean.spread
    print('3A · foto limpia, mid / spread:', mid0, spread0)
    if through == '3A': return locals()

    # 3B · Recupera la liquidez
    # Ejercicio 3B: guarda available como la profundidad ask de clean en dos niveles.
    available = clean.depth('sell',2)
    print('3B · liquidez sell:', available)
    if through == '3B': return locals()

    # 3C · Un límite detiene el plan
    # Ejercicio 3C: planifica BUY 1 a 101 y SELL 1.5 a 99 sobre clean; conserva sus planes y pendientes.
    limit_order = Order('BTC','buy',1,price=101,order_type=OrderType.LIMIT)
    limit_plan, limit_remaining = plan_fills(limit_order, opposite_levels(limit_order,clean))
    sell_order = Order('BTC','sell',1.5,price=99,order_type=OrderType.LIMIT)
    sell_plan, sell_remaining = plan_fills(sell_order, opposite_levels(sell_order,clean))
    print('3C · LIMIT compra:', [(lv.price,q) for lv,q in limit_plan], limit_remaining)
    print('LIMIT venta:', [(lv.price,q) for lv,q in sell_plan], sell_remaining)
    if through == '3C': return locals()

    # 3D · Un remanente LIMIT descansa
    # Comprobación 3D: completa rest_limit en matching.py.
    resting = fresh_book()
    pending_plan, pending_size = plan_fills(limit_order, opposite_levels(limit_order,resting))
    limit_fills = commit_plan(limit_order,resting,pending_plan)
    rest_limit(limit_order,resting,pending_size)
    print('3D · LIMIT fills:', [(f.price,f.size) for f in limit_fills])
    print('LIMIT bids:', [(lv.price,lv.size) for lv in resting.bids])
    if through == '3D': return locals()

    # 3E · IOC cancela el resto
    # Ejercicio 3E: ejecuta el plan IOC BUY 1 a 101 sobre un libro nuevo y cancela el pendiente.
    ioc_book = fresh_book()
    ioc_order = Order('BTC','buy',1,price=101,order_type=OrderType.IOC)
    ioc_plan,ioc_remaining = plan_fills(ioc_order,opposite_levels(ioc_order,ioc_book))
    ioc_fills = commit_plan(ioc_order,ioc_book,ioc_plan)
    print('3E · IOC ejecutado / cancelado:', sum(f.size for f in ioc_fills), ioc_remaining)
    print('IOC bids:', [(lv.price,lv.size) for lv in ioc_book.bids])
    if through == '3E': return locals()

    # 3F · Valida FOK antes de mutar
    # Comprobación 3F: completa validate_plan en matching.py.
    fok_book = fresh_book()
    fok_order = Order('BTC','buy',3,price=102,order_type=OrderType.FOK)
    fok_plan,fok_remaining = plan_fills(fok_order,opposite_levels(fok_order,fok_book))
    fok_fills = []
    if validate_plan(fok_order,fok_remaining):
        fok_fills = commit_plan(fok_order,fok_book,fok_plan)
    print('3F · FOK insuficiente, fills:', len(fok_fills))
    print('FOK asks intactos:', [(lv.price,lv.size) for lv in fok_book.asks])
    if through == '3F': return locals()

    # 4A · Integra tus fases en PlannedEngine
    # Comprobación 4A: completa PlannedEngine en matching.py.
    engine = PlannedEngine()
    for kind in (OrderType.MARKET,OrderType.LIMIT,OrderType.IOC,OrderType.FOK):
        policy_book = fresh_book()
        policy_order = Order('BTC','buy',1,price=None if kind is OrderType.MARKET else 101,order_type=kind)
        policy_fills = engine.process(policy_order,policy_book,timestamp=9)
        print(kind.value, 'fills:', [(f.price,round(f.size,6)) for f in policy_fills], 'bids:', [(lv.price,round(lv.size,6)) for lv in policy_book.bids])
    if through == '4A': return locals()

    # 4B · Una orden pequeña cabe
    # Ejercicio 4B: ejecuta MARKET BUY 0.2 sobre un libro nuevo con tu PlannedEngine y guarda small_fills.
    small_fills = engine.process(Order('BTC','buy',.2,order_type=OrderType.MARKET),fresh_book())
    print('4B · pequeña:', [(f.price,f.size) for f in small_fills])
    if through == '4B': return locals()

    # 5A · Calcula precio efectivo
    # Comprobación 5A: completa effective_price en matching.py.
    sweep_fills = engine.process(Order('BTC','buy',1,order_type=OrderType.MARKET),fresh_book())
    eff = effective_price(sweep_fills)
    print('5A · precio efectivo:', eff)
    if through == '5A': return locals()

    # 5B · Coste respecto al mid
    # Ejercicio 5B: guarda buy_slippage = eff - mid inicial y explica el coste positivo de esta compra.
    buy_slippage = eff - fresh_book().mid
    # Respuesta 5B: pagar 101.6 frente a mid 100 cuesta 1.6 USD/BTC; el mid no es ejecutable.
    print('5B · coste compra por unidad:', buy_slippage)
    if through == '5B': return locals()

    # 5C · Mide el barrido
    # Ejercicio 5C: suma los tamaños de sweep_fills en executed y cuenta sus fills en levels_used.
    executed = sum(fill.size for fill in sweep_fills)
    levels_used = len(sweep_fills)
    print('5C · ejecutado / tramos:', executed, levels_used)
    if through == '5C': return locals()

    data_path = Path(__file__).resolve().parent / 'exchange/_data/btc_lob_snapshots.csv'
    with data_path.open(newline='') as stream:
        csv_row = next(csv.DictReader(stream))
    # 6A · Tu motor llega al CSV
    # Ejercicio 6A: construye csv_book, pide FOK por el doble de su liquidez ask y conserva csv_fills.
    csv_book = SnapshotBook.from_snapshot('BTCUSDT',csv_row,10)
    csv_available = csv_book.depth('sell',10)
    csv_order = Order('BTCUSDT','buy',2*csv_available,price=csv_book.asks[-1].price,order_type=OrderType.FOK)
    csv_fills = engine.process(csv_order,csv_book)
    print('6A · CSV FOK fills:',len(csv_fills))
    print('CSV liquidez tras FOK:',round(csv_book.depth('sell',10),6))
    csv_market_book = SnapshotBook.from_snapshot('BTCUSDT',csv_row,10)
    csv_market = Order('BTCUSDT','buy',.1,order_type=OrderType.MARKET)
    csv_market_fills = engine.process(csv_market,csv_market_book)
    print('CSV precio ejecutado:', effective_price(csv_market_fills))
    if through == '6A': return locals()

    # 6B · Contrasta con un oráculo explícito
    # Comprobación 6B: completa compare_engine en matching.py.
    for side,price in [('buy',101),('sell',99)]:
        for kind in (OrderType.MARKET,OrderType.LIMIT,OrderType.IOC,OrderType.FOK):
            matched = compare_engine(PlannedEngine,side,1.5,kind,None if kind is OrderType.MARKET else price)
            print('6B · contraste:',side,kind.value,matched)
    if through == '6B': return locals()

    # Lectura 6C: predice dos compras consecutivas antes de ejecutar este contraste.
    shared = fresh_book()
    first = engine.process(Order('BTC', 'buy', .3, order_type=OrderType.MARKET), shared)
    second = engine.process(Order('BTC', 'buy', .3, order_type=OrderType.MARKET), shared)
    print('6C · Consecutivas:', [(f.price, round(f.size, 9)) for f in first],
          [(f.price, round(f.size, 9)) for f in second], '| asks:', book_state(shared)[1])
    separate = [engine.process(Order('BTC', 'buy', .3, order_type=OrderType.MARKET), fresh_book())
                for _ in range(2)]
    print('6C · Libros nuevos:', [[(f.price, round(f.size, 9)) for f in fills] for fills in separate])

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
```

## `opcionales.py`

```python
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
    # Ejercicio 7C: OPTIONAL: devuelve fills, pendiente y aceptación reutilizando las mismas fases; FOK rechazada no confirma.
    plan,remaining=plan_fills(order,opposite_levels(order,book))
    accepted=validate_plan(order,remaining)
    if not accepted:
        return [],remaining,False
    fills=commit_plan(order,book,plan)
    if order.order_type is OrderType.LIMIT:
        rest_limit(order,book,remaining)
    return fills,remaining,True

CHECKPOINTS = ('7A', '7B', '7C', '7D')


def practice(through=None):

    # 7A · Invierte el lado
    # Ejercicio 7A: OPTIONAL: vende 0.5 a mercado sobre sell_book y guarda sold para observar caja y bid restante.
    sell_book = fresh_book()
    sold = PlannedEngine().process(Order('BTC','sell',.5,order_type=OrderType.MARKET),sell_book)
    print('7A · venta:',[(f.price,f.size) for f in sold])
    print('caja / bid restante:',sum(f.cash_flow() for f in sold),sell_book.bids[0].size)
    if through == '7A': return locals()

    # 7B · Dos tamaños caben en el mismo nivel
    # Ejercicio 7B: OPTIONAL: compara compras MARKET de 0.1 y 0.2 en libros nuevos y guarda same_prices.
    same_prices = []
    for size in (.1,.2):
        fs=PlannedEngine().process(Order('BTC','buy',size,order_type=OrderType.MARKET),fresh_book())
        same_prices.append(sum(f.price*f.size for f in fs)/sum(f.size for f in fs))
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
    # Ejercicio 7D: OPTIONAL: calcula eff_prices para MARKET 0.1, 1 y 5 sobre copias nuevas de la fila sintética.
    eff_prices=[]
    for size in (.1,1.,5.):
        fresh=SnapshotBook.from_snapshot('BTCUSDT',csv_row,10)
        fs=PlannedEngine().process(Order('BTCUSDT','buy',size,order_type=OrderType.MARKET),fresh)
        eff_prices.append(sum(f.price*f.size for f in fs)/sum(f.size for f in fs))
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
```

## Respuestas y decisiones por apartado

**1B** · Se toman 0.4 BTC y quedan 0.6 pendientes. El tamaño del Level sigue en 0.4: calcular no consume.

**1C** · La BUY limitada a 101 acepta 101 y rechaza 102. SELL invierte la desigualdad; la igualdad cruza.

**2A** · El plan MARKET contiene 0.4@101 y 0.6@102. Son referencias a los niveles del mismo libro, no fills confirmados; no se reutiliza un plan después de consumirlo.

**2B** · Dos fills de una misma orden; asks finales [(102,1)]. El timestamp y order_id viajan en cada ejecución. El plan no actualiza caja; Fill.cash_flow solo calcula su signo.

**3A** · fresh_book reconstruye niveles nuevos. Comparar políticas sobre un libro ya consumido cambia también la liquidez y mezcla dos efectos.

**3B** · Hay 2 BTC en asks, pero solo 0.4 son admisibles a límite 101. Liquidez total y liquidez al precio permitido son distintas.

**3C** · BUY 1 a 101 planea 0.4 y deja 0.6; SELL 1.5 a 99 planea 1 y deja 0.5. No muta ningún lado.

**3D** · Solo el remanente LIMIT entra al lado propio. No genera un fill. Agregar al mismo precio mantiene un nivel por precio y la ordenación.

**3E** · IOC ejecuta 0.4 y cancela 0.6; no añade bid. MARKET no tiene el límite y completa 1 entre ambos asks.

**3F** · FOK 3 a 102 no cabe: cero fills y ambos lados intactos. También FOK 1 a 101 se rechaza aunque el plan tenga 0.4: planificar no equivale a ejecutar.

**4A** · Encapsulación: el consumidor solo llama process(order,book,timestamp); las fases no se duplican por política. Composición: el motor recibe Order y SnapshotBook y devuelve ExecutionFill. Rechazar antes de commit evita necesitar rollback.

**4B** · MARKET 0.2 produce un fill a 101: cabe en el primer ask.

**5A** · (101×0.4 + 102×0.6)/1 = 101.6 USD/BTC. La media simple 101.5 no pesa tamaños; sin fills no hay precio efectivo.

**5B** · 101.6 − mid 100 = +1.6 USD/BTC. Es coste frente al mid inicial, no rentabilidad ni una comisión. El mid no es un precio ejecutable.

**5C** · Se ejecuta 1 BTC en dos tramos. No son dos órdenes y esta comparación no estima impacto sobre snapshots futuros.

**6A** · FOK por el doble de la profundidad ask se rechaza y conserva todos los niveles. La MARKET de 0.1 en otra foto ejecuta a 100021.8 USDT/BTC. El CSV es sintético; la forma externa cambia, la factory y el consumidor se mantienen.

**6B** · Ocho True comparan fills y ambos lados finales. Omitir order_id permite comparar intenciones equivalentes; comprobar solo fills escondería un motor que consume liquidez incorrecta.

**6C** · En el mismo libro: primera compra [(101,0.3)]; segunda [(101,0.1),(102,0.2)]. Después solo queda ask 102×1.4. Sobre libros nuevos ambas compras se ejecutan 0.3 a 101. En la primera prueba la liquidez consumida persiste; en la segunda controlas el estado inicial para comparar. Ninguna avanza el reloj ni modela prioridad de cola. Inténtalo antes de abrir la solución.

**7A** · OPTIONAL: vender 0.5 produce [(99,0.5)], caja +49.5 USD y bid restante 0.5. Una venta consume bids.

**7B** · OPTIONAL: [101,101]. Los dos tamaños caben en 0.4 BTC; aumentar cantidad no empeora necesariamente el precio.

**7C** · OPTIONAL: trace_process conserva las fases del principal. FOK devuelve accepted=False antes de commit; LIMIT es la única que añade remanente.

**7D** · OPTIONAL: [100021.8,100021.8,100026.655162…] USDT/BTC. Se reconstruye la foto para que la comparación mida el tamaño pedido, no la liquidez consumida anteriormente.
