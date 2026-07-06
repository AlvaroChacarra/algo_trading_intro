# Clase 4 — OOP I — Order y Fill

> Convertir el dict de orden en una clase Order con métodos, y modelar el resultado de un cruce con Fill. Primer módulo de verdad del paquete exchange.

## Contexto teórico

Programación orientada a objetos: una **clase** es una plantilla; un **objeto** es una
instancia rellena. La idea central es juntar **datos y comportamiento**: la orden no solo
guarda su precio y tamaño, sabe calcular su nocional. `__repr__` hace que el objeto sepa
describirse a sí mismo.

En mercado: una `Order` (intención) y un `Fill` (ejecución). El **cash flow** de un fill lleva
signo: comprar saca caja (negativo), vender la mete (positivo). Esa convención de signo es la
base de todo el PnL del curso.

## Qué construyes hoy

**clases Order y Fill (exchange/orders.py, trades.py)**

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

## Ejercicios de construcción

- **1. La clase Order** — class, __init__ y self
- **2. Un método: notional** — el dato opera consigo mismo
- **3. __repr__: que sepa describirse** — dunder methods
- **4. La clase Fill y su cash_flow** — segunda clase + signo
- **5. Instánciala y opérala** — crear objetos y llamar métodos
- **6. De la orden al dinero** — juntar Order, Fill y cash_flow

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/04_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/04_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Un objeto empaqueta datos y comportamiento: la orden ya sabe calcular su nocional.
