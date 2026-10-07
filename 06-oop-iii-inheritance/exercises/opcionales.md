# Variantes OPTIONAL · L6

Cada bloque es independiente: cópialo a `mi_optional.py` junto a tus módulos y ejecuta
`python mi_optional.py`. Conserva cada intento. Los apartados 8A–8B usan las clases
que terminaste en signals.py; si aún no terminaste la práctica, guarda el intento y consulta su solución antes de estas dos variantes. Las demás variantes traen familias de ejemplo con una entrada escalar, indicadas en cada bloque; no cambian el contrato data de signals.py.
No necesitas completar un apartado opcional para intentar otro. Las soluciones
pueden anotar `float | None` y `-> str`: documentan entrada y retorno, sin cambiar
la ejecución ni añadir validaciones.

## Variante 8A

Crea cautious como RSISignal con niveles 20/80 y guarda su decisión sobre data.
Predice qué cambia respecto a 30/70: el indicador es el mismo; cambia su interpretación.

Edita los huecos del bloque; los imports y los cierres están proporcionados.

```python
from signals import RSISignal

closes = [100, 101, 102, 103, 104, 105, 106, 107, 106, 105, 104, 104, 104, 104, 104]
data = {'closes': closes, 'imbalance': 0.5}
# TODO · Ejercicio 8A: OPTIONAL · crea cautious con niveles 20/80 y consulta decide(data).
cautious = None
decision = None
print('niveles RSI 20/80:', decision)
```

<details><summary>Contrasta después de predecir</summary>

`hold`. El RSI sigue en 70; no ha alcanzado el nuevo nivel de venta.

</details>

## Variante 8B

Guarda responses recorriendo RSISignal() e ImbalanceSignal(0.3) sobre data.
Predice ambas respuestas antes de ejecutar.

Edita el hueco del bloque; los imports y los datos están proporcionados.

```python
from signals import RSISignal, ImbalanceSignal

closes = [100, 101, 102, 103, 102, 101, 100, 99, 98, 97, 96, 96, 96, 96, 96, 96]
data = {'closes': closes, 'imbalance': -0.5}
# TODO · Ejercicio 8B: OPTIONAL · guarda responses aplicando las dos reglas al mismo data.
responses = []
print('otro mercado:', responses)
```

<details><summary>Contrasta después de predecir</summary>

`['buy', 'sell']`: RSI 30 compra; imbalance −0.5 vende.

</details>

## Variante 8C

Guarda en falta_name si SinSuper('rota', 0.3) carece de name. Completa Mini usando super().__init__(name), guarda thr y aplica la misma banda simétrica del principal: None y límites → hold. Crea m=Mini('m1', 0.3) y guarda label=m.label().

Edita los huecos del bloque; el código anterior al comentario está proporcionado.

```python
from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self, name):
        self.name = name

    def label(self):
        return self.name

    @abstractmethod
    def decide(self, imbalance):
        ...

class SinSuper(Strategy):
    def __init__(self, name, thr):
        self.thr = thr

    def decide(self, imbalance):
        if imbalance is None:
            return 'hold'
        if imbalance > self.thr:
            return 'buy'
        if imbalance < -self.thr:
            return 'sell'
        return 'hold'
# TODO · Ejercicio 8C: OPTIONAL · contrasta name ausente; completa Mini con super, banda y label.
falta_name = None

class Mini(Strategy):
    def __init__(self, name, thr):
        pass

    def decide(self, imbalance):
        pass

m = None
label = None
# Observación proporcionada; ejecútala después de completar los huecos.
print('SinSuper carece de name:', falta_name)
print('nombre heredado:', label)
print('decisiones:', [m.decide(value) for value in [0.5, 0.3, -0.5]])
```

<details><summary>Contrasta después de predecir</summary>

`True`, `'m1'` y `['buy', 'hold', 'sell']`. La igualdad conserva hold.

</details>

## Variante 8D

Intenta crear `IncompleteEmpty` e `IncompleteBody` y guarda en `blocked`
un booleano por clase: `True` si aparece `TypeError`, o `False` si se crea.
Completa `Complete.decide` delegando con `super()` al cuerpo de `BodyStrategy`,
y guarda `fallback=Complete().decide(0)`.
Deben resultar `[True, True]` y `'hold'`.


Edita los huecos del bloque; el código anterior al comentario está proporcionado.

```python
from abc import ABC, abstractmethod

class EmptyStrategy(ABC):
    @abstractmethod
    def decide(self, imbalance):
        ...

class BodyStrategy(ABC):
    @abstractmethod
    def decide(self, imbalance):
        return 'hold'

class IncompleteEmpty(EmptyStrategy):
    pass

class IncompleteBody(BodyStrategy):
    pass
# TODO · Ejercicio 8D: OPTIONAL · comprueba ambas clases incompletas y delega decide con super.
blocked = []
for cls in (IncompleteEmpty, IncompleteBody):
    # Intenta crear cls() y registra si TypeError lo impide.
    pass

class Complete(BodyStrategy):
    def decide(self, imbalance):
        pass

fallback = None
# Observación proporcionada; ejecútala después de completar los huecos.
print('clases incompletas bloqueadas:', blocked)
print('respuesta heredada:', fallback)
```

<details><summary>Contrasta después de predecir</summary>

`[True, True]` y `'hold'`. Un método abstracto puede tener cuerpo y seguir exigiendo sobrescritura.

</details>

## Variante 8E

Recorre `objects` llamando a `decide(0.5)` y guarda `decisions`;
guarda también `membership` con `isinstance(obj, Strategy)` para cada objeto
y `n_strats` contando los que pertenecen a esa familia.
Para `objects[0]`, guarda además `es_momentum` comprobando su clase concreta.
Deben resultar `['buy', 'buy']`, `[True, False]`, `1` y `True`.


Edita los huecos del bloque; el código anterior al comentario está proporcionado.

```python
class Strategy:
    def decide(self, imbalance):
        return 'hold'

class Momentum(Strategy):
    def decide(self, imbalance):
        if imbalance is None:
            return 'hold'
        if imbalance > 0.3:
            return 'buy'
        if imbalance < -0.3:
            return 'sell'
        return 'hold'

class Impostora:
    def decide(self, imbalance):
        return 'buy'

objects = [Momentum(), Impostora()]
# TODO · Ejercicio 8E: OPTIONAL · calcula decisiones, pertenencia, recuento y clase del primer objeto.
decisions = None
membership = None
n_strats = None
es_momentum = None
# Observación proporcionada; ejecútala después de completar los huecos.
print('decisiones:', decisions)
print('pertenecen a Strategy:', membership)
print('número de estrategias:', n_strats)
print('primera es Momentum:', es_momentum)
```

<details><summary>Contrasta después de predecir</summary>

`['buy', 'buy']`, `[True, False]`, `1` y `True`. Una llamada compatible no exige pertenecer a la misma clase base.

</details>

## Variante 8F

Define Strategy como ABC y Momentum/Contrarian como hijas. Momentum compra por encima de 0.3 y vende por debajo de −0.3; Contrarian invierte solo buy/sell. Ambas devuelven hold en None y en [−0.3,0.3]. Guarda las instancias en strategies y sus decisiones ante 0.5 en decisions.

Edita los huecos del bloque; el código anterior al comentario está proporcionado.

```python

# TODO · Ejercicio 8F: OPTIONAL · declara Strategy abstracta y dos hijas con direcciones opuestas.
from abc import ABC, abstractmethod

class Strategy(ABC):
    # Declara decide como método abstracto.
    pass

class Momentum(Strategy):
    pass

class Contrarian(Strategy):
    pass

strategies = None
decisions = None
# Observación proporcionada; ejecútala después de completar los huecos.
print('con 0.5:', decisions)
print('con -0.5:', [strategy.decide(-0.5) for strategy in strategies])
print('con 0:', [strategy.decide(0) for strategy in strategies])
```

<details><summary>Contrasta después de predecir</summary>

`['buy', 'sell']`, `['sell', 'buy']` y `['hold', 'hold']`: el contraste invierte la dirección, conservando la banda de espera.

</details>
