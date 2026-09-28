# Solución · Lesson 4

## Cómo usar esta solución

Compara primero el apartado que has intentado. Copia cada bloque completo en el archivo indicado dentro de `exercises`.
La solución es texto: no existe otro programa ejecutable en esta carpeta.

| Apartado | Dónde contrastarlo | Por qué se hace así |
| --- | --- | --- |
| 1.a | `models.py`: asignaciones en `__init__` | Cada instancia conserva sus datos. |
| 1.b | `main.py`: import | Reutilizar la clase desde otro archivo, como en L3. |
| 2.a–2.b | `main.py`: creación y atributos | Comprobar que compra y venta son independientes. |
| 3.a | `models.py`: `cash_flow` | Devolver dinero con el signo de la ejecución. |
| 3.b | `main.py`: consultas de flujo | Consultar dos veces no registra otra ejecución. |
| 4.a–4.b | `main.py`: cierre completo | Relacionar caja 20 con posición 0. |
| 5.a–5.b | `main.py`: escenario parcial | Separar caja de unidades pendientes de valorar. |
| 6.a | `models.py`: `__repr__` | Construir un texto con los datos del objeto. |
| 6.b–6.c | `main.py`: impresión, error y guarda | Observar la validación e importar sin ejecutar. |
| 7.a–7.b | Experimentos OPTIONAL al final | Distinguir objetos y valores guardados. |

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

## `main.py`

```python
from models import Fill


def main():
    buy = Fill('buy', 100, 2)
    sell = Fill('sell', 110, 2)
    print('Compra:', buy.side, buy.price, buy.size)
    print('Venta:', sell.side, sell.price, sell.size)
    print('Compra intacta:', buy.side, buy.price, buy.size)
    print('Flujos:', buy.cash_flow(), sell.cash_flow(), buy.cash_flow())

    total_cash = buy.cash_flow() + sell.cash_flow()
    remaining_units = buy.size - sell.size
    print('Caja neta:', total_cash)
    print('Unidades restantes:', remaining_units)

    # Escenario alternativo: sustituye la venta completa, no la acumula.
    partial_sell = Fill('sell', 110, 1)
    partial_cash = buy.cash_flow() + partial_sell.cash_flow()
    remaining_units = buy.size - partial_sell.size
    print('Venta parcial: caja / unidades:', partial_cash, remaining_units)

    print(buy)
    try:
        Fill('buy', -10, 2)
    except ValueError as error:
        print('Ejecución rechazada:', error)


if __name__ == '__main__':
    main()
```

## Comprobaciones · Ejercicios 2–6

Desde `exercises`, ejecuta `python main.py`. `python -c "import main"` no imprime nada.

```text
Compra: buy 100 2
Venta: sell 110 2
Compra intacta: buy 100 2
Flujos: -200 220 -200
Caja neta: 20
Unidades restantes: 0
Venta parcial: caja / unidades: -90 1
Fill(buy 2 @ 100)
Ejecución rechazada: fill requiere lado válido y valores positivos finitos
```

La vuelta completa deja caja 20 y posición 0; la alternativa parcial deja caja −90
 y una unidad pendiente de valorar. Consultar un flujo no contabiliza una cuenta.

## Ejercicio 7 · OPTIONAL · Añadir al final de `main()`

Los siguientes bloques van **dentro de `main()`**, después del bloque `try/except`,
con cuatro espacios de sangría. Son experimentos sobre la misma clase.

**7.a · Instancias independientes.** Cambiar `f` conserva los datos de `g`.

```python
    f = Fill('buy', 100, 2)
    g = Fill('buy', 100, 2)
    f.price = 110
    print(f.cash_flow(), g.cash_flow())  # -220 -200
```

**7.b · Valor guardado y valor recalculado.** Crear `f` de nuevo reinicia el experimento.

```python
    f = Fill('buy', 100, 2)
    f.notional = f.price * f.size
    f.price = 110
    print(f.notional, f.price * f.size)  # 200 220
```

## Criterio de cierre y continuidad

El método usa los atributos actuales y devuelve un resultado sin llevar una cuenta.
`main.py` combina los flujos y tamaños. En L5 `PositionTracker` reutilizará esta clase para
registrar ejecuciones y mantener caja y posición; no necesitas los experimentos OPTIONAL.
