# Solución · Lesson 5

Compara cada apartado después de intentarlo. Copia los bloques completos en sus
archivos dentro de `exercises`; no hay un segundo programa ejecutable resuelto.
El bloque `models.py` se incorpora automáticamente desde la solución canónica de L4.
Si tienes tu propio Fill terminado, consérvalo: no necesitas una clase distinta.

| Apartado | Archivo | Decisión |
| --- | --- | --- |
| 1.a | portfolio.py | Estado propio en cada instancia. |
| 1.b–1.c | main.py | Importar y crear no contabiliza el fill. |
| 2.a–2.b | portfolio.py / main.py | Reutilizar cash_flow y actualizar ambas patas. |
| 3.a–3.b | portfolio.py / main.py | Devolver equity sin cambiar estado. |
| 4.a | main.py | Acumular la venta sobre la compra. |
| 5.a–5.c | book.py / main.py | Leer objetos, calcular mid y tratar None. |
| 6.a–6.c | main.py | Recalcular la propiedad, consultar imbalance e importar en silencio. |
| 7.a–7.c | Variantes al final | Usar las mismas clases en escenarios aislados. |

## `models.py`

```python
"""Una ejecución confirmada: datos y comportamiento en una misma clase."""
from math import isfinite


class Fill:
    def __init__(self, side, price, size):
        # Validación proporcionada; no necesitas modificarla.
        valid_numbers = all(isfinite(x) and x > 0 for x in (price, size))
        if side not in ('buy', 'sell') or not valid_numbers:
            raise ValueError('fill requiere lado válido y valores positivos finitos')
        self.side = side
        self.price = price
        self.size = size

    def cash_flow(self):
        sign = -1 if self.side == 'buy' else 1
        return sign * self.price * self.size

    def __repr__(self):
        return f'Fill({self.side} {self.size} @ {self.price})'
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

## `book.py`

```python
"""Level y la ordenación están proporcionados; completa únicamente mid."""


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

## `main.py`

```python
# Ejercicio 1.b
from models import Fill
from portfolio import PositionTracker
# Ejercicio 5.a
from book import Level, OrderBook


def main():
    # Ejercicio 1.c
    tracker = PositionTracker(cash=1000)
    buy = Fill('buy', 101, 2)
    print('Inicio:', tracker.cash, tracker.position)

    # Ejercicio 2.b
    tracker.apply_fill(buy)
    print('Compra:', tracker.cash, tracker.position)

    # Ejercicio 3.b
    print('Valoraciones:', tracker.equity(100), tracker.equity(105))
    print('Estado intacto:', tracker.cash, tracker.position)

    # Ejercicio 4.a
    sell = Fill('sell', 103, 1)
    tracker.apply_fill(sell)
    print('Venta:', tracker.cash, tracker.position, tracker.equity(100))

    # Ejercicio 5.a
    book = OrderBook([Level(98, 1), Level(99, 2)], [Level(101, 3)])
    best_bid = book.bids[0]
    print('Mejor bid:', best_bid.price)

    # Ejercicio 5.c
    mark = book.mid
    if mark is None:
        print('Sin referencia para valorar')
    else:
        print('Valoración con libro:', tracker.equity(mark))
    one_side = OrderBook([Level(99, 2)], [])
    mark = one_side.mid
    if mark is None:
        print('Sin referencia para valorar')
    else:
        print('Valoración unilateral:', tracker.equity(mark))

    # Ejercicio 6.a
    previous_mid = book.mid
    book.asks[0].price = 103
    print('Guardado / actual:', previous_mid, book.mid)
    book.asks[0].price = 101

    # Ejercicio 6.b
    print('Imbalance:', book.imbalance(levels=1))

    # OPTIONAL · Ejercicio 7.a: dos carteras independientes.
    # OPTIONAL · Ejercicio 7.b: consultar frente a aplicar dos veces.
    # OPTIONAL · Ejercicio 7.c: comparar profundidades del mismo libro.


# Ejercicio 6.c: proporcionado, igual que en L3 y L4.
if __name__ == '__main__':
    main()
```

## Resultados y lectura

```text
Inicio: 1000 0.0
Compra: 798 2.0
Valoraciones: 998.0 1008.0
Estado intacto: 798 2.0
Venta: 901 1.0 1001.0
Mejor bid: 99
Valoración con libro: 1001.0
Sin referencia para valorar
Guardado / actual: 100.0 101.0
Imbalance: -0.2
```

`apply_fill` modifica la instancia y devuelve None. `equity` y `mid` calculan
sin contabilizar operaciones. El mark 105 no persiste en la cartera. No duplicamos
la fórmula de Fill: cambiar su comportamiento cambia lo que recibe el tracker.

## OPTIONAL · Ejercicios 7.a–7.c

Inserta este bloque al final de `main()`, conservando la sangría. Usa las mismas
clases y el libro restaurado; las carteras nuevas aíslan los experimentos.

```python
    # Ejercicio 7.a
    a = PositionTracker(1000)
    b = PositionTracker(1000)
    a.apply_fill(Fill('buy', 101, 2))
    print(a.cash, a.position, b.cash, b.position)

    # Ejercicio 7.b
    probe = PositionTracker(1000)
    probe.apply_fill(buy)
    print(probe.equity(100), probe.equity(100))
    probe.apply_fill(buy)
    print(probe.cash, probe.position)

    # Ejercicio 7.c
    print(book.imbalance(levels=1), book.imbalance(levels=2))
```

Esperas `798 2.0 1000 0.0`, `998.0 998.0`, `596 4.0`, `-0.2 0.0`.
Consultar no muta; aplicar dos veces sí. La segunda cartera no recibe la llamada.
