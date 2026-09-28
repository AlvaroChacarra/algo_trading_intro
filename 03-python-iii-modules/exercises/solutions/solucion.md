# Solución · Lesson 3

## Cómo usar esta solución

Compara primero el apartado que has intentado. Los bloques completos se copian en
el archivo indicado dentro de `exercises`; esta carpeta contiene referencia
textual, no una segunda implementación ejecutable. La numeración sigue el enunciado.

| Apartado | Dónde contrastarlo | Por qué se hace así |
| --- | --- | --- |
| 1.a | `analytics.py`: llamada a `best_prices` | Reutilizar el filtrado de L2. |
| 1.b | `analytics.py`: retorno con `None` | Evitar calcular sin ambos lados. |
| 1.c | `analytics.py`: retorno final | Devolver mid y spread al programa. |
| 2.a | `main.py`: imports | Conectar módulos sin copiar funciones. |
| 2.b–2.c | `main.py`: `orders` y `only_buys` | Comparar mercado completo e incompleto. |
| 3.a–3.b | `main.py`: `try/except` | Tratar la entrada inválida concreta. |
| 4.a–4.b | Guarda proporcionada, experimento y restauración | Sin condición, importar también llama a main; con ella, no. |
| 5.a–5.b | Variante OPTIONAL al final | Acceder a la misma función a través del módulo. |

## `functional.py`

Esta pieza viene de L2.

```python
"""Lesson 2 — funciones reutilizables que Lesson 3 importa como módulo."""


def make_order(side, price, size):
    if side not in ("buy", "sell"):
        raise ValueError("side debe ser 'buy' o 'sell'")
    if price <= 0:
        raise ValueError("price debe ser positivo")
    if size <= 0:
        raise ValueError("size debe ser positivo")
    return {"side": side, "price": price, "size": size}


def best_prices(orders):
    buys = [order["price"] for order in orders if order["side"] == "buy"]
    sells = [order["price"] for order in orders if order["side"] == "sell"]

    bid = max(buys) if buys else None
    ask = min(sells) if sells else None

    return bid, ask
```

## `analytics.py`

```python
"""Lesson 3 — compón funciones de otros módulos sin copiar su implementación."""

from functional import best_prices


def describe(orders):
    bid, ask = best_prices(orders)

    if bid is None or ask is None:
        return {"mid": None, "spread": None}

    return {
        "mid": (bid + ask) / 2,
        "spread": ask - bid,
    }
```

## `main.py`

```python
"""Lesson 3 — conecta módulos y construye el programa."""

from functional import make_order
from analytics import describe


def main():
    orders = [
        make_order("buy", 99, 2),
        make_order("sell", 101, 3),
    ]

    print("mercado:", describe(orders))

    only_buys = [
        make_order("buy", 99, 2),
    ]

    print("solo compras:", describe(only_buys))

    try:
        make_order("buy", -10, 1)
    except ValueError as error:
        print("orden rechazada:", error)


if __name__ == "__main__":
    main()
```

## Comprobaciones · Ejercicios 2–4

Desde `exercises`, ejecuta `python main.py`. Esperas:

```text
mercado: {'mid': 100.0, 'spread': 2}
solo compras: {'mid': None, 'spread': None}
orden rechazada: price debe ser positivo
```

Y:

```bash
python -c "import main"
```

no imprime nada.

## Ejercicio 5 · OPTIONAL · Variante de importación

**5.a.** En el bloque completo de `main.py`, cambia la importación a
`import analytics` y sustituye las dos consultas por:

```python
    print("mercado:", analytics.describe(orders))
    print("solo compras:", analytics.describe(only_buys))
```

Cada línea reemplaza su consulta original, después de crear su lista; no añadas
estas líneas como consultas adicionales. El import de `make_order` se conserva.
**5.b.** Repite `python main.py` y `python -c "import main"`: la salida es idéntica
y el import sigue siendo silencioso. Has cambiado el acceso al nombre, no la función.

## Criterio de cierre y continuidad

`main` coordina, `analytics` calcula y `functional` aporta las operaciones de L2.
El retorno temprano evita hacer aritmética con `None`. La guarda permite importar
sin ejecutar las demostraciones. En L4 mantendrás esta separación al importar `Fill`.
