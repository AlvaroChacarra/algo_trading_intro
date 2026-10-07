# Solución de consulta · L12

Cada bloque es el archivo completo resuelto. Busca el mismo apartado del enunciado: el comentario conserva el encargo y debajo está la respuesta. Copia solo después de intentarlo. Conserva tu carpeta personal; para contrastar sustituye el archivo correspondiente y ejecuta la misma comprobación del apartado. Las bases y datos ya están incluidos.

## `profiles.py`

```python
"""Pesos sin unidades y tamaños programados en BTC."""
from math import isfinite


def normalize_profile(raw):
    # Ejercicio 1A: completa normalize_profile(raw): valida una lista no vacía de valores finitos no negativos y suma positiva; devuelve cada valor dividido por la suma.
    if not raw or not all(isfinite(value) and value >= 0 for value in raw) or sum(raw) <= 0:
        raise ValueError('perfil finito, no negativo y con suma positiva')
    total = sum(raw)
    return [value/total for value in raw]


def slice_sizes(weights,total_size):
    # Ejercicio 1B: completa slice_sizes(weights, total_size): devuelve cada peso multiplicado por total_size, sin modificar weights.
    return [total_size*weight for weight in weights]
```

## `execution.py`

```python
"""Una Strategy: programa el objetivo; los fills confirman ejecución."""
from math import isfinite
from profiles import normalize_profile, slice_sizes
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class StudentVWAPStrategy(Strategy):
    def __init__(self, side: str, total_size: float, profile: list[float], symbol: str = 'BTC'):
        if side not in ('buy','sell') or not isfinite(total_size) or total_size <= 0:
            raise ValueError('lado válido y tamaño positivo')
        self.side = side
        self.symbol = symbol
        self.total_size = total_size
        self.weights = normalize_profile(profile)
        self.sizes = slice_sizes(self.weights,total_size)
        self.on_start(None)

    def on_start(self, ctx):
        # Ejercicio 2A: completa on_start(ctx): reinicia step a 0, target y executed a 0.0; conserva el constructor proporcionado.
        self.step = 0
        self.target = 0.0
        self.executed = 0.0

    def advance_target(self):
        # Ejercicio 2B: completa advance_target(): devuelve False al agotar sizes; si queda intervalo, suma sizes[step] a target, incrementa step y devuelve True.
        if self.step >= len(self.sizes):
            return False
        self.target += self.sizes[self.step]
        self.step += 1
        return True

    def on_fill(self, fill):
        # Ejercicio 2C: completa on_fill(fill): suma solo fill.size a executed; enviar una orden no aumenta este contador.
        self.executed += fill.size

    def pending_size(self):
        # Ejercicio 2D: completa pending_size(): devuelve max(0.0, target-executed), sin modificar el estado.
        return max(0.0, self.target-self.executed)

    def on_book_update(self, book):
        # Ejercicio 2E: completa on_book_update(book): avanza el objetivo; si queda horizonte y pending_size()>1e-12, devuelve una NewOrder MARKET de ese tamaño; en otro caso devuelve [].
        if not self.advance_target():
            return []
        size = self.pending_size()
        if size <= 1e-12:
            return []
        return [NewOrder(Order(self.symbol,self.side,size,
                               order_type=OrderType.MARKET))]
```

## `main.py`

```python
"""L12: del encargo al calendario y a la ejecución confirmada."""
from profiles import normalize_profile, slice_sizes
from execution import StudentVWAPStrategy
from runner import ResearchBacktest
from market import ReplayMarket
from book import SnapshotBook
from matching import ExecutionFill
from metrics import weighted_price, execution_cost_bps
from scenarios import raw, total_size, partial_rows, raw_u, schedule_rows, precios, volumenes

STEPS = ('1A', '1B', '2A', '2B', '2C', '2D', '2E', '2F', '3A', '3B', '4A', '4B', '4C', '4D', '4E', '4F', '4G', '5A')


def practice(through=None):
    print('Encargo: 5 BTC · cinco intervalos iguales · perfil conocido antes de operar')
    weights = normalize_profile(raw)
    print('1A · pesos:', weights, 'suma:', sum(weights))
    if through == '1A': return locals()

    sizes = slice_sizes(weights,total_size)
    print('1B · tamaños BTC:', sizes, 'total:', sum(sizes))
    if through == '1B': return locals()


    print('Variación: compra 1 BTC · dos intervalos · fills parciales')
    schedule = StudentVWAPStrategy('buy',1,[1,1])
    print('2A · estado inicial:', schedule.step, schedule.target, schedule.executed)
    if through == '2A': return locals()

    available = schedule.advance_target()
    print('2B · primer objetivo:', available, schedule.target, 'confirmado:', schedule.executed)
    if through == '2B': return locals()

    schedule.on_fill(ExecutionFill(0,'BTC','buy',101,.25))
    print('2C · confirmado BTC:', schedule.executed)
    if through == '2C': return locals()

    schedule.advance_target()
    print('2D · objetivo / confirmado / déficit:', schedule.target, schedule.executed, schedule.pending_size())
    if through == '2D': return locals()

    trace = StudentVWAPStrategy('buy',1,[1,1])
    print('2E · nueva instancia para la traza: step / executed:', trace.step, trace.executed)
    if through == '2E': return locals()

    # Ejercicio 2F: guarda first_action y second_action de trace.on_book_update(None), confirmando entre ambas un ExecutionFill de 0.25 BTC; predice el segundo tamaño y comprueba que no hay tercer envío.
    first_action = trace.on_book_update(None)[0]
    trace.on_fill(ExecutionFill(first_action.order.id,'BTC','buy',101,.25))
    second_action = trace.on_book_update(None)[0]
    print('2F · primer / segundo envío BTC:', first_action.order.size, second_action.order.size)
    print('2F · confirmado / sin tercer envío:', trace.executed, trace.on_book_update(None))
    if through == '2F': return locals()

    # Ejercicio 3A: guarda strategy como StudentVWAPStrategy buy, total 1, perfil [1,1]; ejecuta ResearchBacktest con partial_rows, profundidad 1, cash 1000 y fee_bps=10; guarda execution.
    strategy = StudentVWAPStrategy('buy',1,[1,1])
    execution = ResearchBacktest(ReplayMarket(partial_rows,'BTC',1),strategy,fee_bps=10,cash=1000).run()
    print('3A · fills:', [(f.price,f.size) for f in execution.fills])
    print('3A · mercado / intervalos:', execution.n_steps, strategy.step)
    if through == '3A': return locals()

    # Ejercicio 3B: fija arrival en el mid de la primera partial_rows antes de operar; guarda vwap_price con weighted_price, price_cost con execution_cost_bps y residual como total_size-executed.
    arrival = SnapshotBook.from_snapshot('BTC',partial_rows[0],1).mid
    vwap_price = weighted_price(execution.fills)
    price_cost = execution_cost_bps(execution.fills,arrival,'buy')
    residual = strategy.total_size-strategy.executed
    print('cierre ejecución propia:', round(strategy.executed,4), round(residual,4), round(vwap_price,4), round(price_cost,4), round(execution.fees,4))
    if through == '3B': return locals()

    # Ejercicio 4A: guarda w20 normalizando veinte unos; calcula total20 sumando slice_sizes(w20,1); predice el peso de cada intervalo.
    w20 = normalize_profile([1]*20)
    total20 = sum(slice_sizes(w20,1))
    print('4A · peso / total:', w20[0], round(total20,6))
    if through == '4A': return locals()

    # Ejercicio 4B: normaliza raw_u=[3,1,1,1,4] en pesos_u y calcula sizes_u para 5 BTC; conserva el total.
    pesos_u = normalize_profile(raw_u)
    sizes_u = slice_sizes(pesos_u,5)
    print('4B · pesos / tamaños BTC:', pesos_u, sizes_u)
    if through == '4B': return locals()

    # Ejercicio 4C: ejecuta tu clase buy de 5 BTC con [1]*5 y raw_u sobre schedule_rows; guarda twap_result y vwap_result; compara fills y precio ponderado.
    twap_result = ResearchBacktest(ReplayMarket(schedule_rows,'BTC',1),StudentVWAPStrategy('buy',5,[1]*5)).run()
    vwap_result = ResearchBacktest(ReplayMarket(schedule_rows,'BTC',1),StudentVWAPStrategy('buy',5,raw_u)).run()
    print('4C · TWAP / VWAP: cantidad y precio:', [(sum(f.size for f in r.fills),weighted_price(r.fills)) for r in (twap_result,vwap_result)])
    if through == '4C': return locals()

    # Ejercicio 4D: calcula coste_bps de una venta a 99974.5 frente al arrival 100000 y explica por qué un coste positivo es adverso.
    coste_bps = (100000-99974.5)/100000*10000
    print('4D · coste venta bps:', round(coste_bps,4))
    if through == '4D': return locals()

    # Ejercicio 4E: calcula avg_manual para 0.25 BTC a 101 y 0.75 a 103; explica por qué 102, la media simple, no representa esos fills.
    avg_manual = (101*.25+103*.75)/(.25+.75)
    print('4E · precio manual / fills:', avg_manual, vwap_price)
    if through == '4E': return locals()

    # Ejercicio 4F: calcula vwap_sesion con precios [100,101,102] y volumenes [5,2,1]; contrasta con vwap_price y explica por qué el volumen futuro solo sirve para evaluar después.
    vwap_sesion = sum(p*v for p,v in zip(precios,volumenes))/sum(volumenes)
    print('4F · VWAP sesión / propios fills:', vwap_sesion, vwap_price)
    if through == '4F': return locals()

    # Ejercicio 4G: ejecuta tu clase sell de 1 BTC con [1,1] sobre partial_rows; guarda sell_result y ejecutado como suma de tamaños de sus fills; explica el signo de final_position.
    sell_result = ResearchBacktest(ReplayMarket(partial_rows,'BTC',1),StudentVWAPStrategy('sell',1,[1,1])).run()
    ejecutado = sum(f.size for f in sell_result.fills)
    print('4G · venta: BTC / posición / coste bps:', ejecutado, sell_result.final_position, round(execution_cost_bps(sell_result.fills,100,'sell'),4))
    if through == '4G': return locals()

    # Ejercicio 5A: copia partial_rows en short_rows y cambia solo ask_size_1 de la segunda foto a 0.5; ejecuta sparse_strategy y sparse_result, calcula shortfall y comprueba que otra foto líquida no abre un nuevo intervalo.
    short_rows = [dict(row) for row in partial_rows]
    short_rows[1]['ask_size_1'] = .5
    sparse_strategy = StudentVWAPStrategy('buy',1,[1,1])
    sparse_result = ResearchBacktest(ReplayMarket(short_rows,'BTC',1),sparse_strategy).run()
    shortfall = sparse_strategy.total_size-sparse_strategy.executed
    print('5A · confirmado / déficit / intervalos / fotos:', sparse_strategy.executed, shortfall, sparse_strategy.step, sparse_result.n_steps)
    print('5A · sin envío posterior:', sparse_strategy.on_book_update(None))
    if through == '5A': return locals()

    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L12: sigue los apartados del enunciado.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## `opcionales.py`

```python
"""OPTIONAL: variantes y previsiones; no alteran la estrategia requerida."""
from math import isfinite
from profiles import normalize_profile, slice_sizes
from execution import StudentVWAPStrategy
from matching import ExecutionFill

STEPS = ('6A','6B','6C','6D','6E','6F','6G','6H')


def rolling_mean(xs,k):
    # Ejercicio 6C: OPTIONAL: completa rolling_mean(xs,k): exige k entero entre 1 y len(xs), lanza ValueError fuera del dominio y devuelve la media de los últimos k valores.
    if not isinstance(k,int) or not 1<=k<=len(xs):
        raise ValueError('k debe ser entero entre 1 y len(xs)')
    return sum(xs[-k:])/k


def correction(target_so_far,executed,remaining_slices):
    # Ejercicio 6F: OPTIONAL: completa correction(target_so_far,executed,remaining_slices): exige valores finitos y 0<=executed<=target_so_far e intervalos enteros positivos; devuelve el déficit dividido por intervalos, o lanza ValueError.
    from math import isfinite
    if (not isfinite(target_so_far) or not isfinite(executed)
            or not 0<=executed<=target_so_far
            or not isinstance(remaining_slices,int) or remaining_slices<=0):
        raise ValueError('déficit no negativo y número entero positivo de intervalos requeridos')
    return (target_so_far-executed)/remaining_slices


def slope(xs,ys):
    # Ejercicio 6G: OPTIONAL: completa slope(xs,ys) con productos centrados divididos por variación de x; exige pares finitos del mismo tamaño, al menos dos y x variable; calcula b, intercept y prediction para xs=[1,2,3], ys=[3,5,7], x nuevo 4.
    from math import isfinite
    if len(xs)!=len(ys) or len(xs)<2 or not all(isfinite(v) for v in list(xs)+list(ys)):
        raise ValueError('necesitas al menos dos pares finitos')
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    numerator=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    denominator=sum((x-mx)**2 for x in xs)
    if denominator==0:
        raise ValueError('x debe variar')
    return numerator/denominator


def practice(through=None):
    print("OPTIONAL · pasado disponible; ninguna previsión se conecta al runner")
    # Ejercicio 6A: OPTIONAL: guarda a y b como pesos de dos estrategias buy de 1 BTC con perfiles [2]*5 y [1]*5; predice si cambian las proporciones.
    a = StudentVWAPStrategy('buy',1,[2]*5).weights
    b = StudentVWAPStrategy('buy',1,[1]*5).weights
    print('6A · misma escala relativa:',a==b,a)
    if through == '6A': return locals()

    # Ejercicio 6B: OPTIONAL: crea variant buy de 1 BTC con [1,1], pide first, confirma un fill de 0.4 BTC y guarda next_size de la siguiente acción.
    variant = StudentVWAPStrategy('buy',1,[1,1])
    first = variant.on_book_update(None)[0]
    variant.on_fill(ExecutionFill(first.order.id,'BTC','buy',101,.4))
    next_size = variant.on_book_update(None)[0].order.size
    print('6B · fill / siguiente orden:',variant.executed,next_size)
    if through == '6B': return locals()

    print('6C · últimos dos:', rolling_mean([1, 2, 3, 4], 2))
    print('6C · toda la serie:', rolling_mean([1, 2, 3, 4], 4))
    if through == '6C': return locals()

    volumes = [100,120,90,110,130]
    # Ejercicio 6D: OPTIONAL: guarda pred como media de los últimos tres volumes=[100,120,90,110,130], sin consultar un volumen futuro.
    pred = rolling_mean(volumes,3)
    print('6D · próximo volumen estimado:', pred)
    if through == '6D': return locals()

    preds = [120,80,200]
    # Ejercicio 6E: OPTIONAL: guarda profile normalizando preds=[120,80,200] con tu función normalize_profile.
    profile = normalize_profile(preds)
    print('6E · perfil:', profile, 'suma:', sum(profile))
    if through == '6E': return locals()

    print('6F · extra por intervalo:', round(correction(0.5, 0.3, 2), 6))
    print('6F · sin déficit:', correction(0.5, 0.5, 2))
    if through == '6F': return locals()

    xs=[1,2,3]
    ys=[3,5,7]
    b=slope(xs,ys)
    intercept=sum(ys)/len(ys)-b*sum(xs)/len(xs)
    prediction=intercept+b*4
    print('6G · pendiente:', b, 'intercepto:', intercept, 'predicción x=4:', prediction)
    if through == '6G': return locals()

    demanda = [5,10,20,25,20,10,6,4]
    # Ejercicio 6H: OPTIONAL: guarda plan de 100 barras normalizando demanda=[5,10,20,25,20,10,6,4] y usando slice_sizes; explica qué representa cada tamaño.
    plan = slice_sizes(normalize_profile(demanda),100)
    print('6H · plan de barras:', plan)
    print('6H · total:', sum(plan))
    if through == '6H': return locals()

    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L12: variantes OPTIONAL.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## Respuestas y decisiones por apartado

**1A** · Pesos [0.2]*5, suma 1. También [0,1,3] produce [0,0.25,0.75]. Cambiar la escala de todos los volúmenes no altera sus proporciones.

**1B** · Cinco tamaños de 1 BTC, total 5. Todavía no son fills. La conservación del encargo se decide antes de cualquier ejecución.

**2A** · step=0, target=0.0, executed=0.0. Todos los callbacks pertenecen a la misma Strategy y usan mensajes de L10.

**2B** · True, objetivo 0.5; confirmado 0.0.

**2C** · Confirmado 0.25 BTC.

**2D** · Tras avanzar otra vez: objetivo 1, confirmado 0.25, pendiente 0.75.

**2E** · Nueva traza inicial sin ejecución; el callback emitirá una acción o [].

**2F** · Primer envío 0.5, segundo 0.75; confirmado sigue en 0.25; tercer envío [].

**3A** · (.25a 101,.75a 103), cantidad 1, déficit 0;3 fotos y 2 intervalos. Aquí había liquidez suficiente; el calendario no la garantiza. La prueba manual y el runner comparten clase, métodos y mensajes.

**3B** · Cantidad 1, residual 0, precio 102.5, coste 250 bps y fees 0.1025. El nombre VWAP del precio de fills no lo convierte en VWAP de mercado. La misma cadena produce la ejecución y las métricas.

**4A** · .05 y 1.0. Es reparto temporal, no una predicción de precios.

**4B** · [.3,.1,.1,.1,.4] y[1.5,.5,.5,.5,2]BTC. Es volumen esperado supuesto; volumen negociado y profundidad visible son distintos.

**4C** · Ambos 5 BTC a precio 101. Coincidir en una muestra no implica que todos los perfiles sean equivalentes. Un replay sustituye cada foto: no modela impacto persistente de tus órdenes.

**4D** · 2.55 bps: precio de venta inferior a referencia. Un coste positivo es adverso tanto al comprar como al vender.

**4E** · 102.5 y 102.5. La comprobación independiente conecta el resultado con sus unidades.

**4F** · 100.5 frente a 102.5; son poblaciones distintas. El benchmark ex post no se convierte en información de decisión ex ante.

**4G** · Ejecutado 1, posición −1 y coste 0 bps: 0.5 a 99 y 0.5 a 101 promedian 100. No significa ejecución gratuita frente a cada decision mid. Un parent arrival distinto del decision mid mide una pregunta distinta.

**5A** · Confirmado 0.75, déficit 0.25, 2 intervalos y 3 fotos; [] después. La liquidez del último intervalo limita la ejecución. Terminar el calendario y completar el objetivo son hechos diferentes. Una foto adicional no abre un intervalo nuevo: advance_target devuelve False y no se envía otra orden; el déficit sigue siendo 0.25 BTC.

**6A** · True y cinco pesos 0.2. El constructor reutiliza normalize_profile, no otra fórmula.

**6B** · .4 y 0.6 BTC. Se mantiene exactamente la clase y la familia de mensajes del principal.

**6C** · últimos dos: 3.5 toda la serie: 2.5 Extensión OPTIONAL: no altera el runner ni es prerrequisito posterior.

**6D** · próximo volumen estimado: 110.0 Extensión OPTIONAL: no altera el runner ni es prerrequisito posterior.

**6E** · perfil: [0.3, 0.2, 0.5] suma: 1.0 Extensión OPTIONAL: no altera el runner ni es prerrequisito posterior.

**6F** · extra por intervalo: 0.1 sin déficit: 0.0 Es un extra por intervalo, no el tamaño total de la próxima orden. Extensión OPTIONAL: no altera el runner ni es prerrequisito posterior.

**6G** · pendiente: 2.0 intercepto: 1.0 predicción x=4: 9.0 El ajuste describe estos tres pares; no valida una predicción fuera de muestra. Extensión OPTIONAL: no altera el runner ni es prerrequisito posterior.

**6H** · plan de barras: [5.0, 10.0, 20.0, 25.0, 20.0, 10.0, 6.0, 4.0] total: 100.0 Extensión OPTIONAL: no altera el runner ni es prerrequisito posterior.

Enviar 0.5 y confirmar 0.25 deja 0.25 pendiente del primer intervalo. En el segundo el objetivo acumulado es 1, así que se pide 0.75. La tercera foto no envía nada: el perfil tiene dos intervalos. Restar envíos en vez de fills oculta el déficit. En 5A se ejecutan 0.75 y faltan 0.25 aunque llegue más liquidez.

TWAP distribuye uniformemente en intervalos de igual duración; VWAP usa proporciones de volumen esperado conocidas antes. En 4C ambos ejecutan 5 a 101: una muestra no identifica mejora causal ni modela impacto persistente. En 4F el VWAP de sesión 100.5 y el de tus fills 102.5 ponderan poblaciones distintas. El coste de venta de 4G es 0 respecto al parent arrival 100, pero cada fill cruza su spread; no equivale a ejecución gratuita.

## Bases incluidas

Se incorporan directamente desde sus respuestas canónicas; ya están completas en la entrega. No requieren otro ejercicio.

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
