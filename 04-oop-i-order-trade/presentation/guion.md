# Guion — Clase 4: OOP I — Order y Trade

**Idea central:** Un objeto empaqueta datos y comportamiento: la orden ya sabe calcular su nocional.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: De dict a clase

- **Qué decir:** Una clase es una plantilla. `__init__` guarda los datos (lo que antes eran claves del dict) como atributos. Crear un objeto es rellenar la plantilla.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Métodos: el dato sabe operar consigo mismo

- **Qué decir:** Antes tenías compute_notional(order). Ahora la orden lo sabe hacer sola: order.notional(). El comportamiento vive junto al dato.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: Fill: el resultado de un cruce

- **Qué decir:** Cuando una orden se ejecuta, genera un Fill. Su cash_flow es negativo si compras (sale caja) y positivo si vendes.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
