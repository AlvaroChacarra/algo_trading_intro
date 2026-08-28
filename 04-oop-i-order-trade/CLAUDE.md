# Clase 4 — OOP I — Order y Fill (guía de implementación)

Pieza del framework: **OrderMini y FillMini como modelos didácticos; migración explícita a exchange.Order y exchange.Fill**.

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

Continuidad: los atributos son los campos del dict de L1. Para no fingir que dos firmas distintas
son la misma API, el cuaderno construye `OrderMini(symbol, side, price, size)` y
`FillMini(symbol, side, price, size)`. Antes de entrar en `exchange/` se muestra la migración:
`Order(symbol, side, size, price=...)` añade tipo/id y `Fill(order_id, symbol, side, price, size)`
añade trazabilidad. Esos nombres y firmas públicas quedan estables desde L4.

Puente: una orden suelta; ¿quién suma los cash flows y lleva la cuenta? `PositionTracker` (L5).

## Presentación (3 bloques)

1. **De dict a clase** — Una clase es una plantilla. `__init__` guarda los datos (lo que antes eran claves del dict) como atributos. Crear un objeto es rellenar la plantilla.
2. **Métodos: el dato sabe operar consigo mismo** — Antes tenías compute_notional(order). Ahora la orden lo sabe hacer sola: order.notional(). El comportamiento vive junto al dato.
3. **Fill: el resultado de un cruce** — Cuando una orden se ejecuta, genera un Fill. Su cash_flow es negativo si compras (sale caja) y positivo si vendes.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `04_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El snapshot de `exchange/` declara exactamente la superficie disponible en L4. La lección construye su pieza sobre esa superficie; el snapshot siguiente conserva el estado acumulado sin presuponer que cada clase añada un módulo nuevo.
