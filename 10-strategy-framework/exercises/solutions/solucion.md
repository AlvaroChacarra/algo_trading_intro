# Soluciones · L10

Intenta cada apartado y conserva tu copia antes de consultar. Cada archivo tiene un único bloque completo copiable; sustituye el archivo de tu copia local. Los comentarios repiten el encargo y la respuesta está inmediatamente debajo. Los módulos y datos necesarios ya están incluidos. REQUIRED funciona sin OPTIONAL.

## Respuestas y decisiones por apartado

**1A** · Hold propone [] y no genera ningún fill. Strategy es el contrato proporcionado; implementas su hija.

**1B** · on_start restablece False, 0, 0.0 y None. La misma instancia puede empezar de nuevo.

**1C** · Primera consulta: una NewOrder. Segunda: []. done cuenta la propuesta; executed sigue en 0.

**2A** · action.order es BUY 1; crear o inspeccionar esa petición deja caja 1000 y posición 0.

**2B** · Se confirman 101×0.4 y 102×0.6. mark era 100; el ask queda vacío y mid posterior es None. La cartera aún no registra nada.

**2C** · Caja 898.4, posición 1, equity 998.4 al mark 100. Dos callbacks suman 1 BTC. En la segunda foto no hay orden y equity 1000.4 al mid 102.

**3A** · charge(.1016) deja 999.8984 en la sonda aislada. La compra cobra solo sobre su importe confirmado, no por foto.

**3B** · El contenedor vacío devuelve 0 pasos y 0 fills. Una foto puede tener cero o muchos fills; n_steps no es n_fills.

**3C** · reset limpia el mercado; se crean cartera y resultado nuevos. on_start reinicia la estrategia. StartProbe, proporcionada, devuelve started=True; Hold da [1000,1000].

**3D** · Cada ejecución alimenta cartera, fee y callback. BuyOnce(1) genera 2 fills y curva [998.4,1000.4]. Registrar el envío no equivale a contabilizarlo.

**3E** · on_end observa posición 1, después de las operaciones y antes del return. Se devuelve un resultado independiente.

**4A** · La repetición del mismo runner mantiene curva [998.4,1000.4], posición 1 y callbacks 2. No acumula posición 2 ni cuatro callbacks.

**4B** · True/True: callbacks==2 y executed==0.4+0.6. Contar confirmaciones y sumar cantidades son medidas distintas.

**4C** · SellOnce(0.5) usa el mismo runner: caja 1049.5, posición-0.5 y equity 998.5. El ejemplo permite posición corta y no modela margen.

**4D** · Hold: [1000,1000], fees 0. BuyOnce(1): [998.2984,1000.2984], fees 0.1016. Misma ejecución y posición, caja menor por ese coste.

**4E** · Se solicitan 3 BTC; done=True, executed=1 y posición 1. Solo hay 1 BTC de ask en la foto 0. No se reenvían los 2 pendientes: BuyOnce significa una propuesta. Repetir limpia todo: los mismos 2 fills, posición 1 y callbacks 2. La prueba distingue intención de ejecución, no acredita que la regla complete objetivos.

**5A** · OPTIONAL. Al quitar el segundo ask se ejecutan 0.4 BTC y un fill; curva [999.6,1000.4]. La segunda foto no completa lo pendiente.

**5B** · OPTIONAL. True: curvas y posiciones iguales en ambas ejecuciones de la misma instancia; resultados distintos como objetos.

**5C** · OPTIONAL. En estas fotos la regla compra 0.1 cada vez: 2 fills, posición 0.2. None y el umbral exacto no compran. El resultado del fixture no demuestra predicción.

## `strategy.py`

```python
"""Reglas intercambiables: proponen órdenes y reciben confirmaciones."""
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class Hold(Strategy):
    def on_book_update(self, book):
        # Ejercicio 1A: devuelve [] desde Hold.on_book_update: observar el libro no obliga a enviar una orden.
        return []


class BuyOnce(Strategy):
    def __init__(self, size=1.0):
        self.size = size
        self.done = False
        self.callbacks = 0
        self.executed = 0.0
        self.end_position = None

    def on_start(self, ctx):
        # Ejercicio 1B: reinicia done, callbacks, executed y end_position en BuyOnce.on_start para repetir la misma estrategia.
        self.done = False
        self.callbacks = 0
        self.executed = 0.0
        self.end_position = None

    def on_book_update(self, book):
        # Ejercicio 1C: propón una única NewOrder MARKET de self.size usando book.symbol; después devuelve [].
        if self.done:
            return []
        self.done = True
        return [NewOrder(Order(book.symbol, 'buy', self.size,
                               order_type=OrderType.MARKET))]

    def on_fill(self, fill):
        self.callbacks += 1
        self.executed += fill.size

    def on_end(self, ctx):
        self.end_position = ctx.position


class SellOnce(BuyOnce):
    def on_book_update(self,book):
        # Ejercicio 4C: sobrescribe solo SellOnce.on_book_update para proponer una venta MARKET única del tamaño configurado.
        if self.done:
            return []
        self.done=True
        return [NewOrder(Order(book.symbol,'sell',self.size,order_type=OrderType.MARKET))]
```

## `runner.py`

```python
"""Un runner común: coordinar decisiones, fills, costes y valoración."""
from math import isfinite
from portfolio import PositionTracker
from exchange.strategy import NewOrder
from exchange.orders import OrderType
from exchange.backtest import Context


class FeePortfolio(PositionTracker):
    def charge(self, fee):
        if not isfinite(fee) or fee < 0:
            raise ValueError('comisión finita y no negativa')
        # Ejercicio 3A: resta fee de self.cash en FeePortfolio.charge; conserva la validación proporcionada.
        self.cash -= fee


class ResearchResult:
    def __init__(self):
        self.equity_curve = []
        self.positions = []
        self.fills = []
        self.fees = 0.0
        self.final_cash = 0.0
        self.final_position = 0.0
        self.final_equity = 0.0

    @property
    def n_steps(self):
        # Ejercicio 3B: deriva n_steps de equity_curve y n_fills de fills, sin contadores independientes.
        return len(self.equity_curve)

    @property
    def n_fills(self):
        # Ejercicio 3B: deriva n_steps de equity_curve y n_fills de fills, sin contadores independientes.
        return len(self.fills)


class ResearchBacktest:
    def __init__(self, market, strategy, fee_bps=0.0, cash=1000):
        if not isfinite(fee_bps) or fee_bps < 0 or not isfinite(cash):
            raise ValueError('cash finito y comisiones finitas no negativas')
        self.market = market
        self.strategy = strategy
        self.fee_bps = fee_bps
        self.cash = cash

    def run(self):
        self.market.reset()
        tracker = FeePortfolio(self.cash)
        ctx = Context(self.market, tracker)
        result = ResearchResult()
        # Ejercicio 3C: llama on_start(ctx) antes del bucle de ResearchBacktest.run para reiniciar la estrategia.
        self.strategy.on_start(ctx)
        while True:
            book = self.market.step()
            if book is None:
                break
            mark = book.mid
            if mark is None:
                raise ValueError('el replay requiere dos lados para valorar')
            for action in self.strategy.on_book_update(book):
                if not isinstance(action, NewOrder):
                    raise ValueError('este runner admite acciones NewOrder')
                if action.order.order_type not in (OrderType.MARKET, OrderType.IOC):
                    raise ValueError('este runner admite solo MARKET/IOC')
                for fill in self.market.submit(action.order):
                    # Ejercicio 3D: registra cada fill en la cartera, cobra su fee una vez y notifica strategy.on_fill(fill).
                    tracker.apply_fill(fill)
                    fee = fill.price * fill.size * self.fee_bps / 10000
                    # Ejercicio 3D: registra cada fill en la cartera, cobra su fee una vez y notifica strategy.on_fill(fill).
                    tracker.charge(fee)
                    result.fees += fee
                    result.fills.append(fill)
                    # Ejercicio 3D: registra cada fill en la cartera, cobra su fee una vez y notifica strategy.on_fill(fill).
                    self.strategy.on_fill(fill)
            result.equity_curve.append(tracker.equity(mark))
            result.positions.append(tracker.position)
        result.final_cash = tracker.cash
        result.final_position = tracker.position
        result.final_equity = (result.equity_curve[-1]
                               if result.equity_curve else tracker.cash)
        # Ejercicio 3E: llama on_end(ctx) tras la contabilidad final y antes de devolver el resultado.
        self.strategy.on_end(ctx)
        return result
```

## `main.py`

```python
"""Práctica L10: una propuesta, confirmaciones y un runner reutilizable."""
import argparse
from strategy import Hold, BuyOnce, SellOnce
from runner import FeePortfolio, ResearchResult, ResearchBacktest
from market import ReplayMarket
from portfolio import PositionTracker
from book import SnapshotBook
from exchange.backtest import Context
from scenarios import rows


CHECKPOINTS = ('1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B', '3C', '3D', '3E', '4A', '4B', '4C', '4D', '4E')


def practice(through=None):
    print('Dos fotos · mid 100 → 102 · caja 1000 USDT · asks: 101×0.4 + 102×0.6')
    preview_book = SnapshotBook.from_snapshot('BTC', rows[0], 2)
    print('1A · Hold propone:', Hold().on_book_update(preview_book))
    if through == '1A': return locals()

    strategy = BuyOnce(1)
    manual_market = ReplayMarket(rows, symbol='BTC', depth=2)
    tracker = PositionTracker(cash=1000)
    ctx = Context(manual_market, tracker)
    strategy.on_start(ctx)
    print('1B · inicio:', strategy.done, strategy.callbacks, strategy.executed)
    if through == '1B': return locals()

    first_actions = strategy.on_book_update(preview_book)
    print('1C · primera / segunda:', len(first_actions), strategy.on_book_update(preview_book))
    print('confirmado todavía:', strategy.executed)
    if through == '1C': return locals()

    # Ejercicio 2A: guarda la primera petición en action e inspecciona la orden sin enviarla ni cambiar la cartera.
    action = first_actions[0]
    print('2A · petición:', action.order.side.value, action.order.size)
    print('antes del envío, caja / posición:', tracker.cash, tracker.position)
    if through == '2A': return locals()

    # Ejercicio 2B: avanza manual_market, captura su mid antes de ejecutar y envía action.order; guarda active_book, mark y confirmed.
    active_book = manual_market.step()
    mark = active_book.mid
    confirmed = manual_market.submit(action.order)
    print('2B · fills:', [(f.price, f.size) for f in confirmed])
    print('mark anterior / mid después:', mark, active_book.mid)
    print('caja aún sin registrar:', tracker.cash)
    if through == '2B': return locals()

    # Ejercicio 2C: aplica cada fill confirmado a tracker, llama strategy.on_fill por cada uno y guarda first_equity al mark previo.
    for fill in confirmed:
        tracker.apply_fill(fill)
        strategy.on_fill(fill)
    first_equity = tracker.equity(mark)
    print('2C · caja / posición / equity:', tracker.cash, tracker.position, first_equity)
    print('callbacks / ejecutado:', strategy.callbacks, strategy.executed)
    second_book = manual_market.step()
    print('segunda decisión:', strategy.on_book_update(second_book))
    print('segunda equity:', tracker.equity(second_book.mid))
    strategy.on_end(ctx)
    print('cierre manual:', strategy.end_position)
    if through == '2C': return locals()

    fee_probe = FeePortfolio(1000)
    fee_probe.charge(101.6 * 10 / 10000)
    print('3A · comisión / caja:', 101.6 * 10 / 10000, fee_probe.cash)
    if through == '3A': return locals()

    result_probe = ResearchResult()
    print('3B · contenedor vacío:', result_probe.n_steps, result_probe.n_fills)
    if through == '3B': return locals()

    # Proporcionado: sonda de inicio, sin fills ni dependencia del apartado 3D.
    class StartProbe(Hold):
        started = False
        def on_start(self, ctx):
            self.started = True
    start_probe = StartProbe()
    hold_probe = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), start_probe).run()
    print('3C · inicio notificado:', start_probe.started)
    print('control runner:', hold_probe.equity_curve, hold_probe.n_fills)
    if through == '3C': return locals()

    fill_probe = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), BuyOnce(1)).run()
    print('3D · registro runner:', fill_probe.equity_curve, fill_probe.n_fills)
    if through == '3D': return locals()

    runner = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), BuyOnce(1))
    result = runner.run()
    print('3E · runner equity:', result.equity_curve)
    print('runner caja / posición:', result.final_cash, result.final_position)
    print('runner pasos / fills:', result.n_steps, result.n_fills)
    print('cierre callback:', runner.strategy.end_position)
    if through == '3E': return locals()

    # Ejercicio 4A: ejecuta otra vez el mismo runner y guarda repeated, sin crear otra estrategia.
    repeated = runner.run()
    print('4A · repetición equity:', repeated.equity_curve)
    print('repetición posición / callbacks:', repeated.final_position, runner.strategy.callbacks)
    if through == '4A': return locals()

    # Ejercicio 4B: compara callbacks con n_fills y executed con la suma de tamaños de repeated; guarda ambas comprobaciones.
    callbacks_match = runner.strategy.callbacks == repeated.n_fills
    quantity_match = runner.strategy.executed == sum(f.size for f in repeated.fills)
    print('4B · callbacks / cantidad reconciliados:', callbacks_match, quantity_match)
    if through == '4B': return locals()

    sold = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), SellOnce(.5)).run()
    print('4C · venta, caja / posición / equity:', sold.final_cash, sold.final_position, sold.final_equity)
    if through == '4C': return locals()

    # Ejercicio 4D: ejecuta Hold y BuyOnce(1) con 10 bps sobre las mismas filas; guarda hold_result y cost_result.
    hold_result = ResearchBacktest(ReplayMarket(rows,'BTC',2),Hold(),fee_bps=10).run()
    cost_result = ResearchBacktest(ReplayMarket(rows,'BTC',2),BuyOnce(1),fee_bps=10).run()
    print('4D · Hold con fee:', hold_result.equity_curve, hold_result.fees)
    print('BuyOnce con fee:', [round(v, 4) for v in cost_result.equity_curve], round(cost_result.fees, 4))
    print('diferencia final:', round(result.final_equity - cost_result.final_equity, 4))
    if through == '4D': return locals()

    # Ejercicio 4E: predice BuyOnce(3), ejecuta liquidity_runner y repite la misma instancia; guarda liquidity_result y liquidity_repeat.
    liquidity_runner = ResearchBacktest(ReplayMarket(rows,'BTC',2),BuyOnce(3),fee_bps=0,cash=1000)
    liquidity_result = liquidity_runner.run()
    liquidity_repeat = liquidity_runner.run()
    print('4E · solicitado / done / ejecutado / posición:', liquidity_runner.strategy.size, liquidity_runner.strategy.done, liquidity_runner.strategy.executed, liquidity_result.final_position)
    print('fills primera / repetida:', [(f.price, f.size) for f in liquidity_result.fills], [(f.price, f.size) for f in liquidity_repeat.fills])
    print('repetición posición / callbacks:', liquidity_repeat.final_position, liquidity_runner.strategy.callbacks)
    if through == '4E': return locals()

    return locals()


def main(through=None):
    try:
        return practice(through)
    except NotImplementedError as pending:
        print(pending)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Práctica L10 por apartados.')
    parser.add_argument('--through', choices=CHECKPOINTS)
    main(parser.parse_args().through)
```

## `opcionales.py`

```python
"""OPTIONAL: variantes independientes de la ruta requerida."""
import argparse
from strategy import BuyOnce
from runner import ResearchBacktest
from market import ReplayMarket
from scenarios import rows
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class ImbalanceBuyer(Strategy):
    def on_book_update(self,book):
        # Ejercicio 5C: OPTIONAL: compra 0.1 MARKET si imbalance(1)>0.3; en None, igualdad o valores inferiores devuelve [].
        signal=book.imbalance(1)
        if signal is not None and signal>.3:
            return [NewOrder(Order(book.symbol,'buy',.1,order_type=OrderType.MARKET))]
        return []



def practice(through=None):
    print('OPTIONAL · las mismas dos fotos; no es requisito para continuar')
    # Ejercicio 5A: OPTIONAL: copia rows en partial_rows, elimina el segundo ask de la primera foto y ejecuta BuyOnce(1).
    partial_rows = [dict(item) for item in rows]
    del partial_rows[0]['ask_price_2']
    del partial_rows[0]['ask_size_2']
    partial_result = ResearchBacktest(ReplayMarket(partial_rows,'BTC',2),BuyOnce(1)).run()
    print('5A · parcial, fills / posición:', partial_result.n_fills, partial_result.final_position)
    print('parcial equity:', partial_result.equity_curve)
    if through == '5A': return locals()

    # Ejercicio 5B: OPTIONAL: ejecuta dos veces el mismo replay_runner y compara sus curvas y posiciones en same_result.
    replay_runner = ResearchBacktest(ReplayMarket(rows,'BTC',2),BuyOnce(1))
    one = replay_runner.run()
    two = replay_runner.run()
    same_result = one.equity_curve==two.equity_curve and one.positions==two.positions
    print('5B · repetición limpia:', same_result)
    if through == '5B': return locals()

    signal_result = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), ImbalanceBuyer()).run()
    print('5C · señal, fills / posición:', signal_result.n_fills, signal_result.final_position)
    return locals()


def main(through=None):
    try:
        return practice(through)
    except NotImplementedError as pending:
        print(pending)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Variantes OPTIONAL de L10.')
    parser.add_argument('--through', choices=('5A', '5B', '5C'))
    main(parser.parse_args().through)
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
