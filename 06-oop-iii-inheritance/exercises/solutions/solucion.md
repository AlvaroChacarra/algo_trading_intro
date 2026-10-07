# Solución L6 · consulta después del intento

Copia los archivos completos en una copia personal y ejecuta `python main.py`.
`indicators.py` está proporcionado: consérvalo. El libro se inserta desde la
única solución canónica L5. Las decisiones no son órdenes ni resultados de inversión.

## `book.py`

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

## `signals.py`

```python
"""Dos reglas sobre el mismo dato: decidir no envía una orden."""
from abc import ABC, abstractmethod
from indicators import rsi


class Signal(ABC):
    def __init__(self, name='Signal'):
        # Proporcionado: estado común para identificar cualquier regla.
        self.name = name

    # Ejercicio 2A: marca decide como método abstracto.
    @abstractmethod
    def decide(self, data: dict) -> str:
        raise NotImplementedError


# Ejercicio 3A: declara RSISignal como hija de Signal.
class RSISignal(Signal):
    def __init__(self, period=14, buy_level=30, sell_level=70):
        # Proporcionado: parámetros coherentes para esta regla pequeña.
        if type(period) is not int or period < 1:
            raise ValueError('period debe ser un entero positivo')
        if not 0 <= buy_level < sell_level <= 100:
            raise ValueError('usa 0 <= buy_level < sell_level <= 100')
        # Ejercicio 3A: inicializa el nombre heredado como 'RSI'.
        super().__init__('RSI')
        self.period = period
        self.buy_level = buy_level
        self.sell_level = sell_level

    def decide(self, data: dict) -> str:
        # Proporcionado: consume el indicador, no lo vuelve a construir.
        value = rsi(data.get('closes', []), self.period)
        if value is None:
            return 'hold'
        # Ejercicio 3B: interpreta value con los niveles de esta instancia:
        # compra en <= buy_level, vende en >= sell_level; interior -> hold.
        if value <= self.buy_level:
            return 'buy'
        if value >= self.sell_level:
            return 'sell'
        return 'hold'


class ImbalanceSignal(Signal):
    def __init__(self, threshold=0.3):
        # Proporcionado: la banda del desequilibrio es no negativa.
        if not 0 <= threshold <= 1:
            raise ValueError('threshold debe estar entre 0 y 1')
        # Ejercicio 4A: inicializa el nombre heredado como 'Imbalance'.
        super().__init__('Imbalance')
        self.threshold = threshold

    def decide(self, data: dict) -> str:
        # Proporcionado: misma entrada que RSI, campo diferente.
        imbalance = data.get('imbalance')
        # Ejercicio 4A: trata None antes de comparar.
        if imbalance is None:
            return 'hold'
        # Ejercicio 4B: aplica la banda estricta de la instancia.
        if imbalance > self.threshold:
            return 'buy'
        if imbalance < -self.threshold:
            return 'sell'
        return 'hold'
```

## `main.py`

```python
"""Conecta tu libro y tus reglas. Completa un apartado y ejecútalo de nuevo."""
from book import Level, OrderBook
from indicators import rsi
from signals import Signal, RSISignal, ImbalanceSignal


def main():
    # Proporcionado: datos sintéticos docentes, no cotizaciones reales.
    # Un cierre diario en USD; 15 observaciones para calcular 14 cambios.
    closes = [100, 101, 102, 103, 104, 105, 106, 107, 106, 105, 104, 104, 104, 104, 104]
    book = OrderBook([Level(99, 3)], [Level(101, 1)])
    # Ejercicio 1A: consulta imbalance del libro con un nivel.
    imb = book.imbalance(levels=1)
    # Proporcionado: ambas hijas recibirán este mismo diccionario.
    data = {'closes': closes, 'imbalance': imb}
    print('dato compartido | RSI 14:', rsi(closes, 14), '| imbalance:', imb)

    # Proporcionado: captura solo el error esperado al crear la base abstracta.
    try:
        Signal()
        print('base instanciada: falta el decorador')
    except TypeError:
        print('base abstracta: necesita decide concreto')

    # Ejercicio 3C: crea rsi_rule y muestra su nombre y decisión sobre data.
    rsi_rule = RSISignal()
    print(rsi_rule.name + ':', rsi_rule.decide(data))

    # Ejercicio 4C: crea imbalance_rule con umbral 0.3 y muestra su decisión.
    imbalance_rule = ImbalanceSignal(0.3)
    print(imbalance_rule.name + ':', imbalance_rule.decide(data))

    # Ejercicio 5A: recorre ambas reglas con el mismo data.
    rules = [rsi_rule, imbalance_rule]
    decisions = []
    for rule in rules:
        decisions.append(rule.decide(data))
    print('mismo dato, dos reglas:', decisions)

    # Proporcionado: ventanas sintéticas que sitúan el RSI exactamente en 30 y 70.
    closes30 = [100, 101, 102, 103, 102, 101, 100, 99, 98, 97, 96, 96, 96, 96, 96]
    closes70 = closes
    rsi_inputs = [{'closes': values} for values in
                  [closes30, closes70, closes[:14], [100] * 15]]
    missing = OrderBook([], []).imbalance(levels=1)
    imbalance_inputs = [{'imbalance': value} for value in [missing, -0.3, 0.3]]
    # Ejercicio 6A: prueba fronteras, ausencia y cambios de parámetros.
    rsi_boundaries = [rsi_rule.decide(item) for item in rsi_inputs]
    imbalance_boundaries = [imbalance_rule.decide(item) for item in imbalance_inputs]
    print('RSI: límites, sin historia y plano:', rsi_boundaries)
    print('imbalance: ausencia y límites:', imbalance_boundaries)
    print('mismos cierres, período 3:', RSISignal(period=3).decide(data))
    print('mismos cierres, niveles 20/80:', RSISignal(buy_level=20, sell_level=80).decide(data))
    print('mismo imbalance, umbral 0.6:', ImbalanceSignal(0.6).decide(data))

    # Ejercicio 6B: cambia cierres y tamaños; conserva las dos reglas.
    other = OrderBook([Level(99, 1)], [Level(101, 3)])
    other_data = {'closes': closes30, 'imbalance': other.imbalance(levels=1)}
    print('transferencia:', [rule.decide(other_data) for rule in rules])

    # Lectura 7A: traza super en enunciado.md; no cambia este programa.


if __name__ == '__main__':
    main()
```

## Predicciones REQUIRED

**1A:** tamaños 3 y 1 producen `(3-1)/(3+1)=0.5`; RSI 14 sigue en 70.0.
**3A:** la cabecera establece pertenencia a Signal; super inicializa name='RSI' en
la misma instancia que almacena period=14 y los niveles 30/70.
**3B:** con la ventana plana, RSI 50 queda entre los niveles y devuelve hold.
La hija escribe el comportamiento concreto de decide; el padre declara el contrato.
**4A:** None produce hold antes de comparar; super guarda name='Imbalance'.
**4B:** la banda es estricta: +0.3 y -0.3 producen hold. Se usa self.threshold,
por lo que crear otra instancia cambia la banda sin reescribir decide.
**5A:** la lista contiene objetos distintos y ambas llamadas usan el mismo data:
['sell', 'buy']. Es polimorfismo; no se consulta el nombre de la clase.
**2A:** Signal() produce TypeError; quitar el decorador permite crearla. La base
establece el contrato y conserva name; cada hija implementa su propia decisión.
**3C:** RSI: sell, incluso en RSI 70 exacto. Con historia insuficiente devuelve hold.
self es rsi_rule; data contiene ambos campos. super guarda name sobre ese mismo objeto.
**4C:** Imbalance: buy. La otra hija no cambia su respuesta ni el umbral de esta instancia.
**6A:** RSI devuelve ['buy', 'sell', 'hold', 'hold']; imbalance devuelve
['hold', 'hold', 'hold']. El período 3 consulta tres cambios planos y da RSI 50 → hold;
los niveles 20/80 conservan RSI 70 pero lo dejan dentro de su banda → hold.
El umbral 0.6 deja imbalance 0.5 en la banda → hold. Cada parámetro se usa de verdad.
**6B:** Los cierres nuevos dan RSI 30 y el libro da −0.5: ['buy', 'sell'].
RSI lee closes; imbalance lee imbalance. Una tercera hija recibiría el mismo diccionario
y sobrescribiría decide; el bucle seguiría igual. Solo bid con tamaño 3 produce +1, no None.
**7A:** SinInit guarda {'name': 'a'}; SinSuper solo {'threshold': 0.3}; ConSuper
{'name': 'c', 'threshold': 0.3}. Consultar .name en SinSuper produce AttributeError.
Las tres heredan decide → hold; super prepara el mismo objeto, no otra instancia.

## OPTIONAL · Ejercicio 8A

En `mi_optional.py`, conserva los cierres e imports de Variante 8A y sustituye los huecos.

```python
# Ejercicio 8A: OPTIONAL · crea cautious con niveles 20/80 y consulta decide(data).
cautious = RSISignal(buy_level=20, sell_level=80)
decision = cautious.decide(data)
```

`hold`: RSI sigue en 70, pero la regla ahora vende a partir de 80.

## OPTIONAL · Ejercicio 8B

En `mi_optional.py`, conserva el diccionario de Variante 8B y sustituye el hueco.

```python
# Ejercicio 8B: OPTIONAL · guarda responses aplicando las dos reglas al mismo data.
responses = [rule.decide(data) for rule in [RSISignal(), ImbalanceSignal(0.3)]]
```

`['buy', 'sell']`: RSI 30 e imbalance −0.5, la misma llamada sobre hijas diferentes.

## OPTIONAL · Ejercicio 8C

En `mi_optional.py`, conserva imports/datos/clases proporcionados de Variante 8C;
sustituye el bloque editable por este código y ejecuta la observación del enunciado.

```python
# Ejercicio 8C: OPTIONAL · contrasta name ausente; completa Mini con super, banda y label.
falta_name = not hasattr(SinSuper('rota', 0.3), 'name')

class Mini(Strategy):
    def __init__(self, name, thr):
        super().__init__(name)
        self.thr = thr

    def decide(self, imbalance: float | None) -> str:
        if imbalance is None:
            return 'hold'
        if imbalance > self.thr:
            return 'buy'
        if imbalance < -self.thr:
            return 'sell'
        return 'hold'

m = Mini('m1', 0.3)
label = m.label()
```

`True`, `'m1'` y `['buy', 'hold', 'sell']`. La igualdad conserva hold.

## OPTIONAL · Ejercicio 8D

En `mi_optional.py`, conserva imports/datos/clases proporcionados de Variante 8D;
sustituye el bloque editable por este código y ejecuta la observación del enunciado.

```python
# Ejercicio 8D: OPTIONAL · comprueba ambas clases incompletas y delega decide con super.
blocked = []
for cls in (IncompleteEmpty, IncompleteBody):
    try:
        cls()
        blocked.append(False)
    except TypeError:
        blocked.append(True)

class Complete(BodyStrategy):
    def decide(self, imbalance: float | None) -> str:
        return super().decide(imbalance)

fallback = Complete().decide(0)
```

`[True, True]` y `'hold'`. Un método abstracto puede tener cuerpo y seguir exigiendo sobrescritura.

## OPTIONAL · Ejercicio 8E

En `mi_optional.py`, conserva imports/datos/clases proporcionados de Variante 8E;
sustituye el bloque editable por este código y ejecuta la observación del enunciado.

```python
# Ejercicio 8E: OPTIONAL · calcula decisiones, pertenencia, recuento y clase del primer objeto.
decisions = [obj.decide(0.5) for obj in objects]
membership = [isinstance(obj, Strategy) for obj in objects]
n_strats = 0
for obj in objects:
    if isinstance(obj, Strategy):
        n_strats = n_strats + 1
es_momentum = isinstance(objects[0], Momentum)
```

`['buy', 'buy']`, `[True, False]`, `1` y `True`. Una llamada compatible no exige pertenecer a la misma clase base.

## OPTIONAL · Ejercicio 8F

En `mi_optional.py`, conserva imports/datos/clases proporcionados de Variante 8F;
sustituye el bloque editable por este código y ejecuta la observación del enunciado.

```python
# Ejercicio 8F: OPTIONAL · declara Strategy abstracta y dos hijas con direcciones opuestas.
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def decide(self, imbalance: float | None) -> str:
        ...

class Momentum(Strategy):
    def decide(self, imbalance: float | None) -> str:
        if imbalance is None:
            return 'hold'
        if imbalance > 0.3:
            return 'buy'
        if imbalance < -0.3:
            return 'sell'
        return 'hold'

class Contrarian(Strategy):
    def decide(self, imbalance: float | None) -> str:
        if imbalance is None:
            return 'hold'
        if imbalance > 0.3:
            return 'sell'
        if imbalance < -0.3:
            return 'buy'
        return 'hold'

strategies = [Momentum(), Contrarian()]
decisions = [strategy.decide(0.5) for strategy in strategies]
```

`['buy', 'sell']`, `['sell', 'buy']` y `['hold', 'hold']`: el contraste invierte la dirección, conservando la banda de espera.
