# Clase 3 — OOP I — Order y Trade

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

Continuidad: los atributos son los campos del dict de L1. En el cuaderno se construyen las
clases *inline* (estilo L1-L2); el paquete `exchange/` las trae ya pulidas como referencia.

## Ejercicios de construcción

- **1. La clase Order** — class e __init__
- **2. Método notional** — métodos
- **3. __repr__ legible** — dunder methods
- **4. La clase Fill** — segunda clase + método
- **5. Úsalas juntas** — instanciar y operar

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/03_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/03_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Un objeto empaqueta datos y comportamiento: la orden ya sabe calcular su nocional.
