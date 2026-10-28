# Soluciones · L11

Guarda tu intento antes de consultar. Cada archivo tiene un único bloque completo copiable, con el mismo encargo inmediatamente encima de la respuesta. Las bases necesarias ya están incluidas. REQUIRED funciona sin OPTIONAL.

## Respuestas y decisiones por apartado

**1A** · Equity [998.4,1000.4,998.4,1001.4,995.4], dos fills (101×0.4,102×0.6), caja 898.4 y posición 1. La compra cambia caja/posición; después cambia el mark.

**1B** · Picos [1000,1000.4,1000.4,1001.4,1001.4]. La caja inicial cuenta como primer pico aunque la primera equity ya tenga un coste.

**1C** · Caídas [1.6,0,2,0,6] USDT: pico previo menos equity actual. La curva original no cambia.

**1D** · Drawdown máximo 6 USDT, desde 1001.4 hasta 995.4. PnL final −4.6 USDT: mide otra pregunta. Curva vacía: 0.

**2A** · Precio ponderado 101.6 USDT/BTC: (101×0.4+102×0.6)/1. La media simple 101.5 ignora tamaños. Sin fills: None.

**2B** · Arrival 100, coste adverso 160 bps; 1 bps=1/10000. BUY por encima o SELL por debajo da coste positivo. La comisión es otra cifra. Sin fills válidos: None; nunca precio ficticio cero.

**2C** · Máximo |q|=1 BTC, final=1 BTC. Con [0,−2,0], final 0 y máximo 2. Solo mide las posiciones registradas al cierre de cada foto: no el máximo entre fills.

**3A** · Hold: 5 fotos, 0 fills, posición 0, PnL 0, drawdown 0. Es un control válido para el resultado; no ejecuta la misma cantidad que BuyOnce.

**3B** · Arrival 100; PnL −4.6 USDT; 5 fotos y 2 fills. capture_arrival([]) devuelve None. El mercado de referencia es nuevo y no adelanta el experimento.

**3C** · Imbalance(3), thr 0.3 y clip 0.05: 5 fills, posición 0.25 y PnL −1.1. Se usan hasta tres niveles disponibles; estas fotos tienen menos. None e igualdad no operan. Se conserva el runner, sin introducir límites adicionales.

**3D** · Controles: PnL [−1.05,−0.15,−0.5], fills [4,3,5]; fuera=True para −1.1. Dentro o fuera de tres resultados no valida edge. Comparten fotos, caja, tarifa y clip; su actividad y exposición no son iguales.

**3E** · thr 0.1: 5 fills, máximo inventario 0.25 BTC y PnL −1.1. thr 0.5: 0 fills, inventario 0 y PnL 0. Menor umbral no garantiza mejor PnL. Los ratios ilustrativos son 15 y 60 USDT/BTC, no Sharpe ni riesgo completo; elegir sobre la misma muestra no demuestra alpha.

**4A** · summary: pnl −4.6 USDT, drawdown 6 USDT, cost_bps 160, max_inventory 1 BTC. Se componen funciones, sin rehacer la contabilidad ni cambiar ResearchResult.

**4B** · Mismos fills, precio ponderado y coste 160 bps. Fee 0.1016 USDT; PnL −4.7016; equity final 995.2984. Drawdown máximo sigue en 6: restar ese mismo coste a pico y valle no cambia su diferencia en este caso.

**5A** · OPTIONAL. Ambas curvas acaban en −2 USDT; drawdowns 2 y 6. Una cuenta de PnL usa base 0; una de equity usa su caja inicial.

**5B** · OPTIONAL. Ambas posiciones finales son 0; máximos absolutos 1 y 3 BTC. Terminar plano no describe la exposición anterior.

**5C** · OPTIONAL. Curva de cinco puntos; pico en foto 3 (1001.4), valle en foto 4 (995.4), caída 6 USDT. En terminal la lista es la observación; el dibujo proporcionado está disponible si se ejecuta en un entorno con IPython.

**5D** · OPTIONAL. A=300 y B=375 kcal/€; mejor=B según ese ratio. No mide calidad nutricional, como PnL por inventario no mide todo el riesgo.

## `metrics.py`

```python
"""Métricas sobre registros: leer y componer, sin cambiar mercado ni cartera."""
from math import isfinite


def running_peaks(equity, initial_equity):
    # Ejercicio 1B: conserva el mayor pico visto en running_peaks, empezando en initial_equity; devuelve un pico por observación.
    peak = initial_equity
    peaks = []
    for value in equity:
        peak = max(peak, value)
        peaks.append(peak)
    return peaks


def drawdowns(equity, initial_equity=1000):
    # Ejercicio 1C: compón running_peaks para devolver pico menos equity en cada observación, sin modificar la curva.
    peaks = running_peaks(equity, initial_equity)
    return [peak-value for peak,value in zip(peaks,equity)]


def max_drawdown(equity, initial_equity=1000):
    # Ejercicio 1D: devuelve la mayor caída calculada por drawdowns; una curva vacía devuelve 0.0.
    return max(drawdowns(equity, initial_equity), default=0.0)


def weighted_price(fills):
    # Ejercicio 2A: pondera price por size en weighted_price; divide por cantidad confirmada y devuelve None sin fills.
    quantity = sum(fill.size for fill in fills)
    if quantity == 0:
        return None
    return sum(fill.price*fill.size for fill in fills)/quantity


def execution_cost_bps(fills, arrival_mid, side):
    # Ejercicio 2B: calcula execution_cost_bps frente al arrival previo, con signo buy/sell; conserva las guardias proporcionadas y separa fees.
    if not isfinite(arrival_mid) or arrival_mid <= 0 or side not in ('buy','sell'):
        raise ValueError('referencia positiva y lado válido')
    if any(fill.side != side for fill in fills):
        raise ValueError('agrupa fills del mismo lado')
    average = weighted_price(fills)
    if average is None:
        return None
    sign = 1 if side == 'buy' else -1
    return sign*(average-arrival_mid)/arrival_mid*10000


def max_inventory(positions):
    # Ejercicio 2C: devuelve el máximo valor absoluto de positions, o 0.0 si está vacío; mide inventario muestreado en BTC.
    return max((abs(position) for position in positions), default=0.0)


def capture_arrival(market):
    # Ejercicio 3B: completa capture_arrival y guarda arrival, pnl, pasos y n_fills del experimento original; separa equity de PnL.
    first = market.step()
    return first.mid if first is not None else None
```

## `signals.py`

```python
"""La regla nueva conserva el contrato Strategy y el mismo runner."""
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class ImbalanceStrategy(Strategy):
    def __init__(self, thr=0.3):
        self.thr = thr
    def on_book_update(self, book):
        # Ejercicio 3C: implementa ImbalanceStrategy con thr parametrizable, imbalance(3) y clip 0.05 MARKET; None e igualdad devuelven [].
        imb = book.imbalance(3)
        if imb is None:
            return []
        if imb > self.thr:
            return [NewOrder(Order(book.symbol,'buy',0.05,order_type=OrderType.MARKET))]
        if imb < -self.thr:
            return [NewOrder(Order(book.symbol,'sell',0.05,order_type=OrderType.MARKET))]
        return []
```

## `main.py`

```python
"""L11: observar, medir y comparar el mismo experimento."""
from known_strategies import BuyOnce, Hold
from runner import ResearchBacktest
from market import ReplayMarket
from book import SnapshotBook
from metrics import (running_peaks, drawdowns, max_drawdown, weighted_price,
                     execution_cost_bps, max_inventory, capture_arrival)
from signals import ImbalanceStrategy
from benchmarks import RandomControl, CONTROL_SEEDS
from metrics_support import metric_rows

STEPS = ("1A", "1B", "1C", "1D", "2A", "2B", "2C", "3A", "3B", "3C", "3D", "3E", "4A", "4B")


def rounded(values):
    # Proporcionado: redondeo solo para presentar, nunca para calcular métricas.
    return [round(value, 4) for value in values]


def practice(through=None):
    print('Cinco fotos · mid 100 → 102 → 100 → 103 → 97 · caja 1000 USDT')
    # Ejercicio 1A: ejecuta BuyOnce(1) con las cinco metric_rows, cash=1000 y sin fees; guarda result para medir el mismo experimento.
    result = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), BuyOnce(1), cash=1000).run()
    print('1A · equity:', rounded(result.equity_curve))
    print('1A · fills:', [(f.price, f.size) for f in result.fills])
    if through == '1A': return locals()

    peaks = running_peaks(result.equity_curve, 1000)
    print('1B · picos:', rounded(peaks))
    if through == '1B': return locals()
    falls = drawdowns(result.equity_curve)
    print('1C · caídas:', rounded(falls))
    if through == '1C': return locals()
    print('1D · máximo drawdown:', round(max_drawdown(result.equity_curve), 4))
    if through == '1D': return locals()

    average = weighted_price(result.fills)
    print('2A · precio ponderado / sin fills:', round(average, 4), weighted_price([]))
    if through == '2A': return locals()
    # Proporcionado: misma referencia observable ANTES de enviar la primera orden.
    parent_arrival = SnapshotBook.from_snapshot('BTC', metric_rows[0], 2).mid
    print('2B · arrival / coste bps / fees:', parent_arrival,
          round(execution_cost_bps(result.fills, parent_arrival, 'buy'), 4), result.fees)
    if through == '2B': return locals()
    print('2C · posición final / máximo:', result.final_position, max_inventory(result.positions))
    if through == '2C': return locals()

    # Ejercicio 3A: ejecuta Hold con las mismas filas, caja y fees que BuyOnce; guarda hold_result como control sin operaciones.
    hold_result = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), Hold(), cash=1000).run()
    print('3A · Hold: fills / PnL / drawdown:', hold_result.n_fills,
          hold_result.final_equity - 1000, max_drawdown(hold_result.equity_curve))
    if through == '3A': return locals()
    # Ejercicio 3B: completa capture_arrival y guarda arrival, pnl, pasos y n_fills del experimento original; separa equity de PnL.
    arrival = capture_arrival(ReplayMarket(metric_rows, 'BTC', 2))
    pnl = result.final_equity - 1000
    pasos = result.n_steps
    n_fills = result.n_fills
    print('3B · arrival / PnL / pasos / fills:', arrival, round(pnl, 4), pasos, n_fills)
    if through == '3B': return locals()
    signal_result = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), ImbalanceStrategy(.3)).run()
    print('3C · señal: PnL / fills / máximo inventario:', round(signal_result.final_equity - 1000, 4),
          signal_result.n_fills, max_inventory(signal_result.positions))
    if through == '3C': return locals()

    # Proporcionado: controles sobre las mismas fotos, caja, tarifa y tamaño 0.05.
    # La actividad y la exposición pueden diferir; RandomControl limpia su semilla en on_start.
    controls = [ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), RandomControl(seed)).run()
                for seed in CONTROL_SEEDS]
    monos = [r.final_equity - 1000 for r in controls]
    mi_equity = signal_result.final_equity - 1000
    # Ejercicio 3D: compara mi_equity con el rango de monos en fuera; justifica por qué ese rango no valida una señal.
    fuera = mi_equity < min(monos) or mi_equity > max(monos)
    print('3D · controles: PnL / fills:', [(round(r.final_equity-1000, 4), r.n_fills) for r in controls])
    print('3D · fuera del rango:', fuera)
    if through == '3D': return locals()

    # Ejercicio 3E: predice y ejecuta los umbrales 0.1 y 0.5 en low/high; calcula ratio_a y ratio_b y explica las unidades de sus denominadores.
    low = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), ImbalanceStrategy(.1)).run()
    high = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), ImbalanceStrategy(.5)).run()
    ratio_a = 30 / 2
    ratio_b = 24 / .4
    print('3E · umbrales: PnL / fills / máximo:',
          [(round(r.final_equity-1000, 4), r.n_fills, max_inventory(r.positions)) for r in (low, high)])
    print('3E · ratios ilustrativos, USDT/BTC:', ratio_a, ratio_b)
    if through == '3E': return locals()

    # Ejercicio 4A: compón summary con pnl, drawdown, cost_bps y max_inventory del mismo result, sin redefinir las métricas.
    summary = {'pnl': result.final_equity-1000,
               'drawdown': max_drawdown(result.equity_curve),
               'cost_bps': execution_cost_bps(result.fills, arrival, 'buy'),
               'max_inventory': max_inventory(result.positions)}
    print('4A · diagnóstico:', {k: round(v, 4) for k, v in summary.items()})
    if through == '4A': return locals()
    # Ejercicio 4B: ejecuta otra vez BuyOnce con 10 bps en fee_result; conserva arrival y compara precio, comisión y resultado.
    fee_result = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), BuyOnce(1), fee_bps=10, cash=1000).run()
    print('4B · coste bps / fees / PnL / drawdown:',
          round(execution_cost_bps(fee_result.fills, arrival, 'buy'), 4), round(fee_result.fees, 4),
          round(fee_result.final_equity-1000, 4), round(max_drawdown(fee_result.equity_curve), 4))
    if through == '4B': return locals()
    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L11: mide el mismo experimento por apartados.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## `opcionales.py`

```python
"""Variantes OPTIONAL: misma conclusión final, recorridos distintos."""
from metrics import max_drawdown, max_inventory
from known_strategies import BuyOnce
from runner import ResearchBacktest
from market import ReplayMarket
from metrics_support import metric_rows, show_curve

STEPS = ('5A', '5B', '5C', '5D')


def practice(through=None):
    # Ejercicio 5A: OPTIONAL: calcula dd_a y dd_b con initial_equity=0 para dos curvas que terminan en el mismo PnL.
    dd_a = max_drawdown([0, -1, -2], 0)
    dd_b = max_drawdown([0, 3, 1, 4, -2], 0)
    print('5A · mismo PnL, drawdowns:', dd_a, dd_b)
    if through == '5A': return locals()
    # Ejercicio 5B: OPTIONAL: calcula exposure_a y exposure_b para dos recorridos que terminan planos, sin confundir final con máximo.
    exposure_a = max_inventory([0, 1, 0])
    exposure_b = max_inventory([0, -3, 0])
    print('5B · posición final cero, máximos:', exposure_a, exposure_b)
    if through == '5B': return locals()
    result = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), BuyOnce(1), cash=1000).run()
    # Ejercicio 5C: OPTIONAL: guarda curve del nuevo result y localiza el pico y valle de su peor caída; usa el dibujo proporcionado.
    curve = result.equity_curve
    print('5C · curva / peor caída:', curve, max_drawdown(curve))
    show_curve(curve, 1000)
    if through == '5C': return locals()
    kcal_a, precio_a = 1800, 6.0
    kcal_b, precio_b = 1500, 4.0
    # Ejercicio 5D: OPTIONAL: calcula kcal por euro de las dos cestas y guarda mejor; explica qué mide y qué omite ese ratio.
    ratio_a = kcal_a / precio_a
    ratio_b = kcal_b / precio_b
    mejor = 'A' if ratio_a > ratio_b else 'B'
    print('5D · kcal/€:', ratio_a, ratio_b, 'mayor:', mejor)
    if through == '5D': return locals()
    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L11: variantes OPTIONAL independientes.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## Bases locales incluidas

Estos archivos ya están resueltos y no se modifican en L11. Sus comentarios
pertenecen a la clase de origen; no añaden apartados a esta práctica.

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

## `known_strategies.py`

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
