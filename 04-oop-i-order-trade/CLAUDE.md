# Clase 4 — OOP I — Order y Fill (guía de implementación)

Pieza del framework: **clases Order y Fill (exchange/orders.py, trades.py)**.

## Teoría que cubre

Programación orientada a objetos: una **clase** es una plantilla; un **objeto** es una
instancia rellena. La idea central es juntar **datos y comportamiento**: la orden no solo
guarda su precio y tamaño, sabe calcular su nocional. `__repr__` hace que el objeto sepa
describirse a sí mismo.

En mercado: una `Order` (intención) y un `Fill` (ejecución). El **cash flow** de un fill lleva
signo: comprar saca caja (negativo), vender la mete (positivo). Esa convención de signo es la
base de todo el PnL del curso.

## Implementación técnica

Primeros módulos reales del paquete: `exchange/orders.py` (`Order`, `Side`, `OrderType`) y
`exchange/trades.py` (`Fill`). `Side` y `OrderType` heredan de `str, Enum`: se comparan con
`"buy"`/`"sell"` como antes, pero rechazan valores inválidos. `Order.notional()` reemplaza la
función `compute_notional` de L1; `Fill.cash_flow()` formaliza el signo por lado.

El deck a medida (Pyodide) trae el morph dict→clase, un **Order inspector** (cambias
side/price/size y ves notional y `__repr__`) y un visualizador del **signo del cash_flow**. El
núcleo son 6 ejercicios que culminan en "de la orden al dinero" (Order→Fill→cash_flow); el `.py`
entregable es `orders_demo.py`.

Continuidad: los atributos son los campos del dict de L1. En el cuaderno se construyen las
clases *inline* (estilo L1-L2); el paquete `exchange/` las trae ya pulidas como referencia.
Puente: una orden suelta; ¿quién suma los cash_flows y lleva la cuenta? El PositionTracker (L5).

## Presentación (3 bloques)

1. **De dict a clase** — Una clase es una plantilla. `__init__` guarda los datos (lo que antes eran claves del dict) como atributos. Crear un objeto es rellenar la plantilla.
2. **Métodos: el dato sabe operar consigo mismo** — Antes tenías compute_notional(order). Ahora la orden lo sabe hacer sola: order.notional(). El comportamiento vive junto al dato.
3. **Fill: el resultado de un cruce** — Cuando una orden se ejecuta, genera un Fill. Su cash_flow es negativo si compras (sale caja) y positivo si vendes.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `04_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
