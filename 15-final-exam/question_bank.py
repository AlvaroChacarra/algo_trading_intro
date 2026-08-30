"""question_bank.py — banco de preguntas del curso.

Fuente única de verdad para la práctica acumulativa pública de L15 y el
checkpoint de mitad de curso (tras L6). Cada pregunta es una tupla:

    (enunciado, opción A, opción B, opción C, correcta, tema)

`CANONICAL` son las 40 preguntas de práctica, en orden fijo: es lo que
`generate_exam.py` emite por defecto (`examen.html`, reproducible al byte).
`EXTRA` amplía el pool para poder generar variantes equilibradas con
`generate_exam.py --seed N` (mismo reparto por tema, preguntas distintas), útil
para práctica adicional. Este banco y sus respuestas ya son públicos y **no
son aptos para una convocatoria oficial**. El banco oficial debe crearse de
nuevo y permanecer en la futura fuente privada.
`CHECKPOINT` cubre solo L1-L6 (Python, módulos y POO): el autoexamen de mitad
de curso.

Temas del examen: framework · oop · microstructure · matching · execution · mm · as
Temas del checkpoint: python · modules · oop

La tupla se mantiene deliberadamente estable. Los registros `*_METADATA`,
separados de las preguntas, añaden trazabilidad pública y determinista sin
exponer ni duplicar respuestas.
"""

from __future__ import annotations

from dataclasses import dataclass
import random as _random

# ---------------------------------------------------------------------------
# 40 preguntas de práctica acumulativa (orden fijo)
# ---------------------------------------------------------------------------
CANONICAL = [
    # --- Integración y lectura de código L1-L6/L9-L10 ---------------------
    ("Un loop llama `market.step()` y después decide `if book.spread < limite: enviar()`. ¿Qué conecta esa secuencia?",
     "El control de flujo de L1 con el reloj/estado de Market de L9",
     "La herencia de L6 con la contabilidad de L5",
     "El muestreo VWAP de L12 con la utilidad CARA",
     "A", "framework"),
    ("Lee `spread = ask - bid; decision = 'buy' if spread <= 2 else 'wait'`. Con `bid=99` y `ask=101`, `decision` vale…",
     "'wait'",
     "'buy'",
     "2",
     "B", "python"),
    ("Lee `best = max(o['price'] for o in book if o['side']=='buy')`. Para buys 99 y 101, `best` vale…",
     "99",
     "100",
     "101",
     "C", "python"),
    ("BUG: importar `order_book` lanza inmediatamente el backtest de demo. ¿Qué falta?",
     "Mover la ejecución bajo `if __name__ == '__main__':`",
     "Cambiar todas las funciones a métodos estáticos",
     "Capturar siempre `Exception` al importar",
     "A", "modules"),
    ("Lee `Fill(... side='buy', price=100, size=0.5).cash_flow()`. El resultado correcto es…",
     "+50: comprar aumenta caja",
     "−50: comprar consume caja",
     "0: un fill no afecta a caja",
     "B", "oop"),
    ("BUG: `book.mid()` produce `TypeError: 'float' object is not callable`. La API canónica define `mid` como…",
     "property; debe leerse `book.mid`",
     "classmethod; debe llamarse `OrderBook.mid()`",
     "función del módulo; debe llamarse sin book",
     "A", "oop"),
    ("Lee `class Momentum(Strategy):\n    def on_book_update(self, book): return []`. La clase ya es instanciable porque…",
     "Ha implementado el método abstracto del contrato Strategy",
     "Toda subclase de Python es instanciable aunque omita abstractmethods",
     "Devuelve una lista vacía",
     "A", "framework"),
    ("La composición que ve el alumno en L5 es…",
     "OrderBook contiene niveles; PositionTracker consume objetos Fill",
     "Order hereda de OrderBook",
     "Market hereda de Strategy",
     "A", "oop"),
    ("L2 calcula `best_bid(book)` sobre listas y L7 expone `book.best_bid` sobre `OrderBook`. ¿Qué debe conservar el puente?",
     "El significado económico del mejor bid, aunque cambie la representación",
     "La sintaxis exacta de función para siempre",
     "La mutabilidad de la lista externa dentro del objeto",
     "A", "framework"),
    ("¿Qué permite pasar del módulo reutilizable de L3 a una Strategy enchufable en L10?",
     "Separar importación de ejecución y exponer un contrato estable",
     "Ejecutar la demo cada vez que se importa el módulo",
     "Acoplar la estrategia directamente al motor de matching",
     "A", "framework"),

    # --- Microestructura ---------------------------------------------------
    ("El spread es…",
     "best_ask - best_bid",
     "best_bid - best_ask",
     "(best_bid + best_ask)/2",
     "A", "microstructure"),
    ("Lee `microprice=(ask*bid_size + bid*ask_size)/(bid_size+ask_size)`. Con bid 99×3 y ask 101×1 vale…",
     "99.5",
     "100.0",
     "100.5",
     "C", "microstructure"),
    ("BUG: una FOK de tamaño 2 consume 1 unidad del primer nivel y después descubre que no puede completarse. ¿Qué invariante se violó?",
     "PLAN→VALIDATE→COMMIT: no debía mutar el libro antes de validar el total",
     "Una FOK siempre puede llenarse parcialmente",
     "El best bid debe ser un método, no una property",
     "A", "matching"),
    ("La profundidad (depth) de un lado mide…",
     "El tamaño acumulado en los primeros niveles",
     "La distancia al mid",
     "El número de trades ejecutados",
     "A", "microstructure"),
    ("El mid simple frente al microprice…",
     "El microprice suele anticipar mejor el siguiente movimiento a corto plazo",
     "Son siempre idénticos",
     "El mid es mejor predictor a corto",
     "A", "microstructure"),
    ("Liquidez visible en el libro vs negociación real:",
     "El libro muestra intención; no todo se ejecuta y puede cancelarse",
     "Todo lo del libro se ejecuta seguro",
     "Son lo mismo",
     "A", "microstructure"),

    # --- Tipos de orden y matching ----------------------------------------
    ("Una MARKET buy de tamaño grande sobre un libro fino…",
     "Barre varios niveles y paga un precio efectivo peor que el best ask",
     "Se ejecuta toda al best ask",
     "Se cancela si no hay liquidez al best ask",
     "A", "matching"),
    ("BUG: `snap = market.snapshots; snap[0]['asks'][0][0] = 999` cambia después el replay. ¿Cuál es la corrección?",
     "Devolver una copia profunda de los snapshots",
     "Convertir `snapshots` en variable global",
     "Reordenar asks de mayor a menor",
     "A", "engine"),
    ("BUG: una `Cancel(order_id=7)` del tick siguiente no hace nada porque el runner vació `resting`. ¿Qué contrato falta?",
     "Persistir órdenes resting y su remanente por ID hasta fill/cancel/fin de vida",
     "Convertir toda cancelación en MARKET",
     "Cancelar siempre el nivel de precio completo",
     "A", "framework"),
    ("BUG: para una compra a 101 con decision mid 100 se calcula slippage `100-101=-1`. ¿Cuál es el signo correcto?",
     "+1 para coste comprador: `fill_price - decision_mid`",
     "−1, porque todo slippage comprador es beneficio",
     "0, porque el benchmark no importa",
     "A", "execution"),
    ("El precio efectivo de una market que barre niveles es…",
     "El nocional total dividido por el tamaño total ejecutado",
     "Siempre el best bid",
     "El precio del último nivel tocado",
     "A", "matching"),
    ("Más tamaño en una market order implica, normalmente…",
     "Peor precio efectivo (más slippage)",
     "Mejor precio efectivo",
     "El mismo precio efectivo",
     "A", "matching"),
    ("Un Fill atraviesa `MatchingEngine → PositionTracker → métricas`. ¿Qué debe conservarse para interpretar el resultado?",
     "Lado, precio, tamaño y benchmark de la decisión que originó el fill",
     "Solo el último precio del día",
     "Solo el número total de órdenes enviadas",
     "A", "matching"),
    ("Cruzar ya (market) vs esperar barato (limit) es un trade-off entre…",
     "Certeza de ejecución vs precio",
     "Volatilidad vs volumen",
     "Cash vs equity",
     "A", "matching"),

    # --- Ejecución / VWAP --------------------------------------------------
    ("¿Qué demuestra que VWAP puede reutilizar el framework de L6/L10 sin acoplarse al runner?",
     "Implementa Strategy, propone acciones y actualiza ejecución al recibir fills",
     "Llama directamente a internals de MatchingEngine",
     "Sobrescribe el tipo de cada OrderBook",
     "A", "execution"),
    ("TWAP frente a VWAP:",
     "TWAP reparte en trozos iguales en el tiempo; VWAP pondera por volumen",
     "TWAP pondera por volumen; VWAP por tiempo",
     "Son idénticos",
     "A", "execution"),
    ("Libro, matching y benchmark deben compartir estado temporal porque…",
     "El slippage solo es interpretable contra el mid observado al decidir la orden",
     "El precio final basta para explicar cualquier fill",
     "Matching no depende del libro",
     "A", "execution"),
    ("Lee `sizes=[round(100*w) for w in (0.2,0.5,0.3)]`. El schedule es…",
     "[20, 50, 30]",
     "[20, 70, 100]",
     "[33, 33, 34]",
     "A", "execution"),
    ("BUG: VWAP hace `_executed += child_size` al enviar, aunque solo se llena la mitad. ¿Qué debe contabilizar?",
     "Solo tamaños confirmados en `on_fill`",
     "Todo tamaño solicitado, aunque sea rechazado",
     "El número de snapshots recorridos",
     "A", "execution"),
    ("Para medir el slippage de un fill individual, el benchmark natural es…",
     "El decision mid de la orden hija que originó ese fill",
     "El precio de cierre del año",
     "El best ask final",
     "A", "execution"),
    ("El loop de Market, el lifecycle de Strategy y el inventario del market maker deben coordinarse para que…",
     "cada cancel/fill afecte al estado correcto antes del siguiente tick",
     "el inventario se reinicie después de cada fill",
     "las órdenes resting desaparezcan al cambiar el mid",
     "A", "execution"),

    # --- Market making / Avellaneda-Stoikov -------------------------------
    ("El PnL de un market maker viene de…",
     "Comprar en el bid y vender en el ask, capturando el spread",
     "Cruzar market orders agresivas",
     "Pagar el spread cada vuelta",
     "A", "mm"),
    ("El principal riesgo de un market maker es…",
     "El inventario (posición acumulada cuando el flujo es desequilibrado)",
     "Tener demasiada caja",
     "Cotizar un spread demasiado ancho",
     "A", "mm"),
    ("El skew por inventario consiste en…",
     "Bajar ambas cotizaciones cuando estás largo para volver a plano",
     "Subir el spread sin mover el centro",
     "Cancelar todas las órdenes",
     "A", "mm"),
    ("El reservation price de Avellaneda-Stoikov con inventario largo…",
     "Está por debajo del mid (incentiva soltar)",
     "Está por encima del mid",
     "Coincide siempre con el mid",
     "A", "as"),
    ("Lee `r=s-q*gamma*sigma**2*tau`. Con s=100, q=2, gamma=0.1, sigma=2 y tau=0.5, r vale…",
     "99.6",
     "100.4",
     "96.0",
     "A", "as"),
    ("BUG dimensional: la fórmula usa τ normalizado, pero el simulador interpreta σ como volatilidad por tick. ¿Qué corrección es coherente?",
     "Expresar σ por horizonte o escalar el incremento por `1/sqrt(T)`",
     "Eliminar σ de la fórmula",
     "Multiplicar simultáneamente τ y σ por T",
     "A", "as"),
    ("Lee `lambda_delta=A*exp(-kappa*delta)`. Con A=1, kappa=1 y delta=0, la intensidad vale…",
     "0",
     "1",
     "e",
     "B", "as"),
    ("Adverse selection para un market maker significa…",
     "Acumular posición justo cuando el mercado se mueve en tu contra",
     "Cotizar el mismo precio que el competidor",
     "Tener un spread negativo",
     "A", "mm"),
    ("¿Por qué el market making se simula con un modelo de intensidad de fills λ(δ)=A·e^(-κδ)?",
     "Porque una limit lejos del mid se ejecuta con menos probabilidad que una cerca",
     "Porque las market orders siempre fallan",
     "Porque el mid nunca se mueve",
     "A", "as"),
]

# ---------------------------------------------------------------------------
# Pool ampliado: preguntas equivalentes en dificultad para variantes por seed
# ---------------------------------------------------------------------------
EXTRA = [
    # --- framework ---------------------------------------------------------
    ("El método `on_fill(self, fill)` de una Strategy sirve para…",
     "Reaccionar a las ejecuciones propias y actualizar el estado interno",
     "Enviar una nueva orden obligatoriamente",
     "Cerrar el backtest",
     "A", "framework"),
    ("`NewOrder` y `Cancel` en el framework son…",
     "Las acciones que on_book_update puede devolver",
     "Dos subclases de Order",
     "Métodos del Backtest",
     "A", "framework"),
    ("Durante `Backtest.run()`, ¿cuándo se invoca `Strategy.on_fill`?",
     "Después de confirmar una ejecución propia, para cerrar el feedback de la estrategia",
     "Antes de enviar cualquier acción al mercado",
     "Solo una vez, al finalizar el replay",
     "A", "framework"),
    ("Que `Strategy` sea una clase abstracta (ABC) obliga a…",
     "Implementar on_book_update en cada subclase concreta",
     "Definir un símbolo por defecto",
     "Heredar también de Order",
     "A", "framework"),
    ("VWAPStrategy y MarketMaker reutilizan el contrato Strategy aunque sus runners difieran porque…",
     "Ambos proponen acciones y reciben fills mediante el mismo interfaz; el modelo de ejecución lo aporta cada runner",
     "Backtest detecta el tipo y simula llegadas límite automáticamente",
     "El contrato obliga a usar siempre el mismo runner",
     "A", "framework"),

    # --- oop ---------------------------------------------------------------
    ("`__repr__` en una clase sirve para…",
     "Que el objeto se imprima de forma legible al inspeccionarlo",
     "Comparar dos objetos por igualdad",
     "Hacer la clase abstracta",
     "A", "oop"),
    ("`super().__init__('momentum')` en una subclase…",
     "Llama al constructor de la clase base para reutilizar su inicialización",
     "Crea una instancia nueva de la base",
     "Sobrescribe el método decide",
     "A", "oop"),
    ("Encapsular `_cash` tras `apply_fill`/`equity` evita que…",
     "Se modifique el estado de forma incoherente desde fuera",
     "El atributo ocupe memoria",
     "La clase pueda heredarse",
     "A", "oop"),
    ("`Fill.cash_flow()` de una venta de 0.2 @ 100 vale…",
     "+20",
     "-20",
     "0",
     "A", "oop"),
    ("Poner `@abstractmethod` sobre un método hace que…",
     "La clase no se pueda instanciar sin implementar ese método",
     "El método sea más rápido",
     "El método se ejecute automáticamente",
     "A", "oop"),

    # --- microstructure ----------------------------------------------------
    ("`best_bid` de un libro es…",
     "El precio de compra más alto disponible",
     "El precio de venta más bajo",
     "La media de todas las compras",
     "A", "microstructure"),
    ("El mid de un libro se calcula como…",
     "(best_bid + best_ask) / 2",
     "best_ask - best_bid",
     "best_bid × best_ask",
     "A", "microstructure"),
    ("Un spread estrecho suele indicar…",
     "Un mercado líquido y con poca fricción para cruzar",
     "Un mercado ilíquido",
     "Alta volatilidad garantizada",
     "A", "microstructure"),
    ("El imbalance (bid_size−ask_size)/(bid_size+ask_size) está acotado en…",
     "[-1, 1]",
     "[0, 1]",
     "[-∞, +∞]",
     "A", "microstructure"),
    ("El microprice se acerca al best_ask cuando…",
     "Hay mucho más tamaño en el bid que en el ask",
     "El spread es cero",
     "No hay órdenes de compra",
     "A", "microstructure"),
    ("Sumar el tamaño de los 5 primeros niveles de un lado da…",
     "La profundidad (depth) a 5 niveles de ese lado",
     "El imbalance",
     "El microprice",
     "A", "microstructure"),

    # --- matching ----------------------------------------------------------
    ("Una IOC buy de 1.0 que solo encuentra 0.6 al cruzar…",
     "Llena 0.6 y cancela los 0.4 restantes",
     "Se queda esperando a que aparezcan 0.4 más",
     "No ejecuta nada por no completarse",
     "A", "matching"),
    ("Una LIMIT sell colocada por debajo del best_bid…",
     "Cruza de inmediato contra los bids (limit marketable)",
     "Descansa siempre en el libro",
     "Se rechaza por precio inválido",
     "A", "matching"),
    ("El slippage de una market se mide como…",
     "La diferencia entre su precio efectivo y el precio de referencia (mid/best)",
     "El número de niveles del libro",
     "El tiempo hasta el fill",
     "A", "matching"),
    ("Una FOK que puede completarse sumando varios niveles…",
     "Se ejecuta entera, atravesando esos niveles",
     "Se ejecuta solo al primer nivel",
     "Se cancela por tocar más de un nivel",
     "A", "matching"),
    ("Entre dos market buys iguales, la que cae sobre el libro más profundo…",
     "Sufre menos slippage",
     "Sufre más slippage",
     "Paga exactamente lo mismo",
     "A", "matching"),
    ("Que una limit 'descanse' en el libro significa que…",
     "Queda pendiente esperando contraparte, sin ejecutarse aún",
     "Ya se ejecutó del todo",
     "Se convirtió en market",
     "A", "matching"),
    ("El 'peaje' que paga una market agresiva al barrer es…",
     "Que cada nivel siguiente que toca es peor que el anterior",
     "Una comisión fija del exchange",
     "El tiempo de espera en cola",
     "A", "matching"),
    ("Frente a una market, una limit del mismo lado…",
     "Puede no ejecutarse, pero si lo hace es a un precio igual o mejor",
     "Siempre se ejecuta antes",
     "Siempre paga más caro",
     "A", "matching"),

    # --- execution ---------------------------------------------------------
    ("Un perfil VWAP [0.1, 0.2, 0.4, 0.2, 0.1] indica que…",
     "Se ejecuta más volumen en el centro de la ventana",
     "Se ejecuta todo al principio",
     "Se ejecuta todo al final",
     "A", "execution"),
    ("Un perfil de ejecución plano [1,1,1,1,1] equivale a…",
     "Un TWAP (trozos iguales en el tiempo)",
     "Una orden FOK",
     "Una única market al cierre",
     "A", "execution"),
    ("Normalizar un perfil de volumen significa…",
     "Dividir cada peso por la suma para que sumen 1",
     "Ordenarlo de mayor a menor",
     "Quedarse con el máximo",
     "A", "execution"),
    ("El impacto de mercado de una ejecución crece con…",
     "El tamaño que se manda de golpe",
     "El número de símbolos distintos",
     "La longitud del nombre del ticker",
     "A", "execution"),
    ("Al comparar schedules TWAP y VWAP estáticos, la conclusión correcta es…",
     "Medir ambos con el mismo tamaño, horizonte y benchmark: el nombre no garantiza menor coste",
     "Elegir siempre VWAP sin medirlo",
     "Descartar el benchmark de llegada",
     "A", "execution"),
    ("El `horizon` de una VWAPStrategy representa…",
     "Los intervalos sobre los que reparte el tamaño objetivo",
     "El precio máximo aceptable de la orden",
     "La volatilidad histórica del activo",
     "A", "execution"),
    ("Comparar el precio medio de toda la orden padre con su parent arrival mid mide…",
     "El implementation shortfall de la decisión completa",
     "La volatilidad del día",
     "El número de niveles del libro",
     "A", "execution"),

    # --- mm ----------------------------------------------------------------
    ("Un MarketMaker con inventory_skew=0…",
     "Cotiza simétrico al mid, sin corregir por inventario",
     "No cotiza nunca",
     "Solo cotiza en el bid",
     "A", "mm"),
    ("Cotizar un spread más ancho como market maker…",
     "Reduce la probabilidad de fill pero mejora el margen por vuelta",
     "Aumenta la probabilidad de fill",
     "No cambia nada",
     "A", "mm"),
    ("El `half_spread` de un MarketMaker es…",
     "La distancia del bid y del ask al centro (reservation price)",
     "El spread total del mercado",
     "La comisión del exchange",
     "A", "mm"),
    ("Si a un market maker solo le compran (flujo comprador)…",
     "Se queda corto de inventario y pierde si el precio sube",
     "Acumula caja sin riesgo",
     "Se queda plano automáticamente",
     "A", "mm"),

    # --- as ----------------------------------------------------------------
    ("El optimal spread de Avellaneda-Stoikov depende de…",
     "γ, σ², κ y τ (aversión, volatilidad, intensidad de llegada y tiempo restante)",
     "Solo del inventario actual",
     "Solo del símbolo",
     "A", "as"),
    ("El término (2/γ)·ln(1+γ/κ) del spread óptimo refleja…",
     "La intensidad de llegada de órdenes (κ)",
     "El inventario acumulado",
     "El tiempo restante",
     "A", "as"),
    ("Con inventario 0, el reservation price de A-S…",
     "Coincide con el mid",
     "Está siempre por debajo del mid",
     "Está siempre por encima del mid",
     "A", "as"),
    ("Más volatilidad σ en A-S…",
     "Ensancha el spread y aleja más el reservation price con inventario",
     "Estrecha el spread",
     "No afecta a las cotizaciones",
     "A", "as"),
    ("El horizonte T en A-S representa…",
     "El límite temporal que lleva τ a 0; por sí solo no garantiza inventario plano",
     "El número de niveles del libro",
     "La comisión por operación",
     "A", "as"),
]

# ---------------------------------------------------------------------------
# Checkpoint de mitad de curso: SOLO L1-L6 (Python, módulos, POO)
# ---------------------------------------------------------------------------
CHECKPOINT = [
    # --- python (L1-L2) ----------------------------------------------------
    ("En Python, ¿`type(3)` y `type(3.0)` son el mismo tipo?",
     "No: 3 es int y 3.0 es float, tipos distintos",
     "Sí, ambos son int",
     "Sí, ambos son float",
     "A", "python"),
    ("`'BTC' + 'USDT'` produce…",
     "'BTCUSDT' (concatena las dos cadenas)",
     "Un error de tipos",
     "'BTC USDT' con un espacio",
     "A", "python"),
    ("`order['price']` sobre un dict accede a…",
     "El valor asociado a la clave 'price'",
     "La posición 'price' de una lista",
     "Un atributo del objeto order",
     "A", "python"),
    ("Con bid=100 y ask=102, `(bid + ask) / 2` da…",
     "101.0 (un float)",
     "101 (un int)",
     "'101'",
     "A", "python"),
    ("`sum(o['size'] for o in libro if o['side']=='buy')` calcula…",
     "El tamaño total de las órdenes de compra",
     "El número de órdenes del libro",
     "El precio medio",
     "A", "python"),
    ("`len([1, 2, 3])` vale…",
     "3",
     "2",
     "6",
     "A", "python"),
    ("La comprehension `[o['price'] for o in libro]` produce…",
     "Una lista con los precios de cada orden",
     "Un único número",
     "Un diccionario de precios",
     "A", "python"),
    ("En `if i % 50 == 0`, el operador `%`…",
     "Es el resto de la división: True una vez cada 50",
     "Es un porcentaje",
     "Divide y redondea",
     "A", "python"),
    ("En `if spread <= 20: ... elif spread <= 60: ...`, el `elif`…",
     "Solo se evalúa si el `if` anterior fue falso",
     "Se evalúa siempre",
     "Sustituye al `if`",
     "A", "python"),
    ("Una tupla `(mid - s/2, mid + s/2)` sirve para…",
     "Devolver dos valores juntos (p. ej. bid y ask)",
     "Modificar una lista en el sitio",
     "Definir un diccionario",
     "A", "python"),

    # --- modules (L3) ------------------------------------------------------
    ("`from order_book import best_bid` importa…",
     "Solo la función best_bid, usable sin prefijo",
     "Todo el módulo con prefijo order_book.",
     "Una copia del módulo entero",
     "A", "modules"),
    ("`try: ... except ValueError: ...` sirve para…",
     "Capturar un error concreto sin que el programa se caiga",
     "Ignorar todos los errores posibles",
     "Lanzar un error a propósito",
     "A", "modules"),
    ("`raise ValueError('size debe ser positivo')` hace que…",
     "Se lance un error y se corte la ejecución de la función ahí",
     "Se imprima un aviso y siga",
     "Se devuelva None",
     "A", "modules"),
    ("`import order_book` frente a `from order_book import *`…",
     "El primero obliga a usar el prefijo `order_book.`",
     "Son exactamente equivalentes",
     "El primero no importa nada",
     "A", "modules"),

    # --- oop (L4-L6) -------------------------------------------------------
    ("En `def __init__(self, symbol, ...)`, `self` es…",
     "La instancia concreta que se está creando",
     "El nombre de la clase",
     "Un módulo importado",
     "A", "oop"),
    ("`Order('BTC', 'buy', 0.5, price=100)` es…",
     "Instanciar la clase: crear un objeto Order",
     "Llamar a una función suelta",
     "Definir la clase Order",
     "A", "oop"),
    ("Un método frente a una función suelta…",
     "Vive dentro de la clase y recibe `self`",
     "Es siempre más rápido",
     "No puede devolver nada",
     "A", "oop"),
    ("`Fill.cash_flow()` de una compra es negativo porque…",
     "Comprar saca caja (pagas)",
     "Comprar siempre pierde dinero",
     "Es un error de signo",
     "A", "oop"),
    ("`PositionTracker` con `_cash` y `_position` privados es un ejemplo de…",
     "Encapsulación: el estado se toca por métodos",
     "Herencia",
     "Polimorfismo",
     "A", "oop"),
    ("Un `OrderBook` que contiene niveles es un ejemplo de…",
     "Composición (tiene-un), no herencia",
     "Herencia (es-un)",
     "Una función pura",
     "A", "oop"),
    ("`class Momentum(Strategy):` establece que Momentum…",
     "Hereda de Strategy (relación es-un)",
     "Contiene un objeto Strategy",
     "Es idéntica a Strategy",
     "A", "oop"),
    ("Sobrescribir (override) un método significa…",
     "Redefinirlo en la subclase con el mismo nombre",
     "Llamarlo dos veces",
     "Borrarlo de la clase base",
     "A", "oop"),
    ("Una clase abstracta (ABC) con `@abstractmethod`…",
     "No se puede instanciar directamente; obliga a las subclases",
     "Se instancia igual que cualquier otra",
     "No admite subclases",
     "A", "oop"),
    ("El polimorfismo permite…",
     "Tratar a Momentum y Contrarian igual porque comparten interfaz",
     "Que una clase cambie de nombre en ejecución",
     "Que un int se vuelva str solo",
     "A", "oop"),
]


# ---------------------------------------------------------------------------
# Trazabilidad pública (separada de las tuplas que consume el generador)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class QuestionMetadata:
    """Contrato pedagógico de una pregunta, sin enunciado ni respuesta.

    `distribution_type` usa exactamente las categorías de
    `pedagogy/assessment_blueprint.yml`. Los enlaces `(lesson, objective)`
    apuntan exclusivamente a objetivos evaluables LIVE/REQUIRED. Para una
    integración, `integration_rationale` documenta el puente entre bloques.
    """

    item_id: str
    lessons: tuple[int, ...]
    objectives: tuple[str, ...]
    distribution_type: str
    cognitive_level: str
    difficulty: str
    concept_ids: tuple[str, ...]
    api_ids: tuple[str, ...]
    notation_ids: tuple[str, ...]
    integration_rationale: str | None = None


# Objetivos reales del blueprint. Mantener los pares juntos evita que una
# pregunta pueda declarar una lección y un objetivo de otra por accidente.
_L01_EXEC = (1, "l01-explain-execution")
_L01_DATA = (1, "l01-model-market-data")
_L01_DECIDE = (1, "l01-turn-data-into-decision")
_L02_FUNCS = (2, "l02-extract-functions")
_L02_BOOK = (2, "l02-read-functional-book")
_L02_SORT = (2, "l02-read-sorting-tools")
_L03_REUSE = (3, "l03-reuse-module")
_L03_ERRORS = (3, "l03-handle-domain-errors")
_L03_IMPORT = (3, "l03-separate-import-and-execution")
_L04_OBJECTS = (4, "l04-build-domain-objects")
_L04_CTORS = (4, "l04-read-canonical-constructors")
_L04_CASH = (4, "l04-interpret-cash-flow")
_L05_BOOK = (5, "l05-compose-book")
_L05_FILLS = (5, "l05-account-for-fills")
_L05_INVARIANTS = (5, "l05-protect-invariants")
_L06_FAMILY = (6, "l06-build-strategy-family")
_L06_POLY = (6, "l06-explain-polymorphism")
_L06_CONTRACT = (6, "l06-enforce-contract")
_L06_INIT = (6, "l06-initialize-subclasses")
_L07_BOOK = (7, "l07-build-book")
_L07_METRICS = (7, "l07-read-metrics")
_L07_BOUNDARY = (7, "l07-build-stable-boundary")
_L08_ATOMIC = (8, "l08-explain-atomicity")
_L08_POLICIES = (8, "l08-compare-order-policies")
_L08_IMPACT = (8, "l08-connect-size-to-impact")
_L09_MARKET = (9, "l09-compose-market")
_L09_LOOP = (9, "l09-run-time-loop")
_L09_RESET = (9, "l09-reset-lifecycle")
_L10_MAP = (10, "l10-map-toy-to-production")
_L10_SEPARATE = (10, "l10-separate-decision-execution")
_L10_FEEDBACK = (10, "l10-close-feedback-loop")
_L10_LIFECYCLE = (10, "l10-read-lifecycle")
_L11_BENCH = (11, "l11-benchmark-strategy")
_L11_SLIPPAGE = (11, "l11-interpret-slippage")
_L11_RISK = (11, "l11-track-inventory-risk")
_L12_COMPARE = (12, "l12-compare-schedules")
_L12_RUN = (12, "l12-run-vwap-strategy")
_L13_LIQUIDITY = (13, "l13-explain-liquidity-provision")
_L13_INVENTORY = (13, "l13-control-inventory")
_L13_RISK_FILLS = (13, "l13-prepare-risk-and-fills")
_L14_RESERVATION = (14, "l14-interpret-reservation-price")
_L14_SPREAD = (14, "l14-interpret-optimal-spread")
_L14_LAB = (14, "l14-run-parameter-lab")
_L14_CAPSTONE = (14, "l14-build-capstone")
_L15_INTEGRATE = (15, "l15-integrate-course")


def _build_metadata(prefix: str, questions: list, rows: tuple,
                    semantics: tuple | None = None) -> tuple[QuestionMetadata, ...]:
    """Materializa ids estables sin acoplar metadatos a la tupla histórica."""
    if len(rows) != len(questions):
        raise ValueError(f"{prefix}: {len(rows)} metadatos para {len(questions)} preguntas")
    if semantics is None:
        semantics = tuple(((), (), ()) for _ in questions)
    if len(semantics) != len(questions):
        raise ValueError(f"{prefix}: {len(semantics)} semánticas para {len(questions)} preguntas")
    result = []
    for index, ((links, distribution, level, difficulty, rationale),
                (concept_ids, api_ids, notation_ids)) in enumerate(
                    zip(rows, semantics), 1):
        result.append(QuestionMetadata(
            item_id=f"{prefix}-{index:03d}",
            lessons=tuple(lesson for lesson, _ in links),
            objectives=tuple(objective for _, objective in links),
            distribution_type=distribution,
            cognitive_level=level,
            difficulty=difficulty,
            concept_ids=tuple(concept_ids),
            api_ids=tuple(api_ids),
            notation_ids=tuple(notation_ids),
            integration_rationale=rationale,
        ))
    return tuple(result)


# Ocho ítems CANONICAL son integraciones explícitas. Los otros 32 se reparten
# en 8 code_reading, 8 conceptual, 8 debugging y 8 financial_interpretation:
# la distribución 8×5 declarada para L15 queda así comprobable al byte.
_CANONICAL_TRACE = (
    ((_L01_DECIDE, _L09_LOOP, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Conecta control de flujo de FOUNDATIONS con el reloj de Market en ENGINE."),
    ((_L01_DECIDE,), "code_reading", "apply", "low", None),
    ((_L02_FUNCS, _L02_BOOK, _L02_SORT), "code_reading", "apply", "medium", None),
    ((_L03_REUSE, _L03_IMPORT), "debugging", "analyze", "medium", None),
    ((_L04_CASH,), "code_reading", "apply", "medium", None),
    ((_L05_BOOK,), "debugging", "analyze", "medium", None),
    ((_L06_CONTRACT, _L10_MAP), "code_reading", "analyze", "medium", None),
    ((_L05_BOOK,), "conceptual", "understand", "medium", None),
    ((_L02_FUNCS, _L02_BOOK, _L07_BOOK, _L07_METRICS, _L15_INTEGRATE),
     "integration", "analyze", "hard",
     "Conserva la semántica del book entre función de FOUNDATIONS y objeto de ENGINE."),
    ((_L03_REUSE, _L10_MAP, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Conecta módulos reutilizables de FOUNDATIONS con el contrato Strategy de ENGINE."),
    ((_L07_METRICS,), "financial_interpretation", "understand", "medium", None),
    ((_L07_METRICS, _L07_BOUNDARY), "code_reading", "apply", "hard", None),
    ((_L08_ATOMIC,), "debugging", "analyze", "hard", None),
    ((_L07_METRICS, _L07_BOUNDARY), "financial_interpretation", "apply", "medium", None),
    ((_L07_METRICS, _L07_BOUNDARY), "financial_interpretation", "analyze", "hard", None),
    ((_L07_BOOK, _L07_BOUNDARY), "conceptual", "analyze", "medium", None),
    ((_L08_IMPACT,), "financial_interpretation", "apply", "medium", None),
    ((_L09_MARKET, _L09_RESET), "debugging", "analyze", "hard", None),
    ((_L10_SEPARATE, _L10_LIFECYCLE), "debugging", "analyze", "hard", None),
    ((_L11_SLIPPAGE,), "debugging", "analyze", "hard", None),
    ((_L08_IMPACT,), "financial_interpretation", "apply", "medium", None),
    ((_L08_IMPACT,), "financial_interpretation", "analyze", "medium", None),
    ((_L04_CASH, _L05_FILLS, _L11_SLIPPAGE, _L15_INTEGRATE),
     "integration", "evaluate", "hard",
     "Sigue un Fill desde objetos/contabilidad de FOUNDATIONS hasta métricas de STRATEGIES."),
    ((_L08_POLICIES,), "conceptual", "analyze", "medium", None),
    ((_L06_POLY, _L10_MAP, _L12_RUN, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Aplica polimorfismo de FOUNDATIONS al contrato de ENGINE y a VWAP."),
    ((_L12_COMPARE,), "conceptual", "understand", "medium", None),
    ((_L07_METRICS, _L08_POLICIES, _L11_SLIPPAGE, _L15_INTEGRATE),
     "integration", "analyze", "hard",
     "Une estado del book y matching de ENGINE con el benchmark de STRATEGIES."),
    ((_L12_COMPARE, _L12_RUN), "code_reading", "apply", "medium", None),
    ((_L10_FEEDBACK, _L12_RUN), "debugging", "analyze", "hard", None),
    ((_L11_BENCH, _L11_SLIPPAGE), "conceptual", "apply", "medium", None),
    ((_L09_LOOP, _L10_SEPARATE, _L10_LIFECYCLE, _L13_INVENTORY, _L15_INTEGRATE),
     "integration", "evaluate", "hard",
     "Coordina reloj de ENGINE, lifecycle/cancel y riesgo de inventario en STRATEGIES."),
    ((_L13_LIQUIDITY,), "financial_interpretation", "understand", "medium", None),
    ((_L13_INVENTORY,), "financial_interpretation", "analyze", "medium", None),
    ((_L13_INVENTORY,), "conceptual", "apply", "medium", None),
    ((_L14_RESERVATION,), "conceptual", "apply", "hard", None),
    ((_L14_RESERVATION,), "code_reading", "analyze", "hard", None),
    ((_L14_RESERVATION, _L14_LAB), "debugging", "analyze", "hard", None),
    ((_L13_RISK_FILLS,), "code_reading", "analyze", "hard", None),
    ((_L13_LIQUIDITY,), "conceptual", "analyze", "hard", None),
    ((_L08_POLICIES, _L13_RISK_FILLS, _L14_LAB, _L15_INTEGRATE),
     "integration", "evaluate", "hard",
     "Conecta ejecución de límites en ENGINE con intensidad de fills y el laboratorio A-S."),
)


# Referencias semánticas explícitas de cada stem canónico. A diferencia de una
# blacklist de palabras, estos ids permiten probar cobertura y excluir cualquier
# concepto/API/notación cuya única ruta sea OPTIONAL.
_CANONICAL_SEMANTICS = (
    (("python.control_flow", "engine.time_loop"), ("market.step",), ()),
    (("python.control_flow", "microstructure.spread"), (), ()),
    (("python.generator_expression",), ("functional.best_bid",), ()),
    (("python.main_guard", "python.imports"), (), ()),
    (("exchange.fill",), ("fill.cash_flow",), ("notation.cash_flow",)),
    (("oop.computed_property",), ("orderbook.mid",), ()),
    (("oop.abstract_base_class", "framework.strategy_contract"),
     ("strategy.on_book_update",), ()),
    (("oop.composition",), (), ()),
    (("functional.order_book", "python.dataclass", "market.level"),
     ("functional.best_bid", "orderbook.best_bid"), ()),
    (("python.modules", "framework.strategy_contract"),
     ("strategy.on_book_update",), ()),
    (("market.book_metrics",), ("orderbook.best_bid", "orderbook.best_ask"), ()),
    (("market.book_metrics",), ("orderbook.microprice",), ()),
    (("matching.atomicity", "matching.plan_validate_commit"),
     ("matching.process",), ()),
    (("market.book_metrics",), ("orderbook.depth",), ()),
    (("market.book_metrics",), ("orderbook.microprice",), ()),
    (("market.external_boundary",), (), ()),
    (("execution.market_impact",), (), ()),
    (("engine.market", "engine.lifecycle"), ("market.snapshots",), ()),
    (("framework.lifecycle", "architecture.actions"), ("cancel.constructor",), ()),
    (("metrics.slippage",), ("backtest_result.fills",),
     ("notation.slippage_signed",)),
    (("execution.market_impact",), (), ()),
    (("execution.market_impact",), (), ()),
    (("exchange.fill", "exchange.position_tracker", "metrics.slippage"),
     ("fill.cash_flow", "tracker.apply_fill", "backtest_result.fills"),
     ("notation.cash_flow", "notation.slippage_signed")),
    (("matching.order_policies",), (), ()),
    (("oop.polymorphism", "framework.strategy_contract", "strategy.vwap"),
     ("strategy.on_book_update", "backtest.run"), ()),
    (("execution.twap", "execution.vwap"), (), ("notation.twap", "notation.vwap")),
    (("market.book_metrics", "matching.order_policies", "metrics.slippage"),
     ("matching.process", "backtest_result.fills"), ("notation.slippage_signed",)),
    (("execution.vwap", "strategy.vwap"), ("vwap_strategy.constructor",),
     ("notation.vwap",)),
    (("strategy.vwap", "architecture.execution_feedback"),
     ("strategy.on_fill", "backtest_result.fills"), ()),
    (("metrics.arrival_price",), (), ("notation.slippage_signed",)),
    (("engine.time_loop", "framework.lifecycle", "inventory.risk"),
     ("market.step", "cancel.constructor", "market_maker.inventory"), ()),
    (("market_making.liquidity_provision",), (), ()),
    (("inventory.risk",), ("market_maker.inventory",), ("notation.inventory",)),
    (("inventory.skew",), ("market_maker.reservation_price",),
     ("notation.inventory",)),
    (("as.reservation_price",), ("avellaneda_stoikov.reservation_price",),
     ("notation.as_reservation_price",)),
    (("as.reservation_price", "as.gamma", "as.sigma", "as.time_horizon"),
     ("avellaneda_stoikov.reservation_price",), ("notation.as_reservation_price",)),
    (("as.sigma", "as.time_horizon", "simulation.parameter_sweep"), (),
     ("notation.as_reservation_price",)),
    (("market_making.fill_intensity",), (), ("notation.fill_intensity",)),
    (("market_making.adverse_selection",), (), ()),
    (("matching.order_policies", "market_making.fill_intensity", "as.optimal_spread"),
     ("matching.process", "mm_simulation.run"),
     ("notation.fill_intensity", "notation.as_optimal_spread")),
)


_EXTRA_TRACE = (
    ((_L05_FILLS, _L10_FEEDBACK, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Conecta la contabilidad de fills de FOUNDATIONS con el feedback del motor."),
    ((_L10_SEPARATE,), "code_reading", "understand", "medium", None),
    ((_L09_LOOP, _L10_FEEDBACK, _L11_BENCH, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Sigue un fill desde el bucle de ENGINE hasta el estado medido en STRATEGIES."),
    ((_L06_CONTRACT,), "debugging", "analyze", "medium", None),
    ((_L06_POLY, _L10_MAP, _L12_RUN, _L13_LIQUIDITY, _L15_INTEGRATE),
     "integration", "evaluate", "hard",
     "Aplica polimorfismo de FOUNDATIONS al motor y a estrategias de ejecución y liquidez."),
    ((_L04_OBJECTS,), "code_reading", "understand", "low", None),
    ((_L06_INIT,), "code_reading", "apply", "medium", None),
    ((_L05_INVARIANTS,), "debugging", "analyze", "medium", None),
    ((_L04_CASH,), "code_reading", "apply", "medium", None),
    ((_L06_CONTRACT,), "debugging", "analyze", "medium", None),
    ((_L07_BOOK,), "financial_interpretation", "understand", "low", None),
    ((_L07_METRICS,), "conceptual", "apply", "low", None),
    ((_L07_METRICS,), "financial_interpretation", "understand", "medium", None),
    ((_L07_METRICS,), "code_reading", "apply", "medium", None),
    ((_L07_METRICS,), "financial_interpretation", "analyze", "hard", None),
    ((_L07_METRICS,), "financial_interpretation", "apply", "medium", None),
    ((_L08_POLICIES,), "debugging", "analyze", "medium", None),
    ((_L08_POLICIES,), "debugging", "analyze", "medium", None),
    ((_L08_IMPACT, _L11_SLIPPAGE, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Relaciona matching de ENGINE con la medición de coste en STRATEGIES."),
    ((_L08_ATOMIC,), "debugging", "analyze", "hard", None),
    ((_L08_IMPACT,), "financial_interpretation", "analyze", "medium", None),
    ((_L08_POLICIES,), "conceptual", "understand", "medium", None),
    ((_L08_IMPACT,), "financial_interpretation", "analyze", "medium", None),
    ((_L08_POLICIES,), "conceptual", "analyze", "medium", None),
    ((_L12_COMPARE,), "code_reading", "apply", "medium", None),
    ((_L12_COMPARE,), "conceptual", "understand", "low", None),
    ((_L12_COMPARE,), "debugging", "analyze", "medium", None),
    ((_L08_IMPACT, _L12_COMPARE, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Une impacto por tamaño de ENGINE con planificación VWAP de STRATEGIES."),
    ((_L10_MAP, _L12_COMPARE, _L15_INTEGRATE), "integration", "evaluate", "hard",
     "Contrasta complejidad de estrategia con el principio de validación del motor."),
    ((_L12_RUN,), "code_reading", "understand", "medium", None),
    ((_L07_METRICS, _L11_SLIPPAGE, _L15_INTEGRATE), "integration", "analyze", "hard",
     "Conecta el mid del libro en ENGINE con el benchmark de STRATEGIES."),
    ((_L13_INVENTORY,), "conceptual", "apply", "medium", None),
    ((_L13_LIQUIDITY,), "financial_interpretation", "analyze", "medium", None),
    ((_L13_LIQUIDITY,), "conceptual", "understand", "medium", None),
    ((_L05_FILLS, _L13_INVENTORY, _L15_INTEGRATE), "integration", "evaluate", "hard",
     "Lleva los fills de FOUNDATIONS al riesgo de inventario del market maker."),
    ((_L14_SPREAD,), "conceptual", "understand", "hard", None),
    ((_L14_SPREAD,), "code_reading", "analyze", "hard", None),
    ((_L14_RESERVATION,), "conceptual", "apply", "medium", None),
    ((_L14_LAB,), "debugging", "analyze", "hard", None),
    ((_L14_RESERVATION,), "financial_interpretation", "analyze", "hard", None),
)


_CHECKPOINT_TRACE = (
    ((_L01_DATA,), "code_reading", "understand", "low", None),
    ((_L01_DATA,), "code_reading", "apply", "low", None),
    ((_L01_DATA,), "code_reading", "apply", "low", None),
    ((_L01_DECIDE,), "financial_interpretation", "apply", "low", None),
    ((_L02_BOOK,), "code_reading", "apply", "medium", None),
    ((_L01_DATA,), "code_reading", "understand", "low", None),
    ((_L02_BOOK,), "code_reading", "apply", "medium", None),
    ((_L01_EXEC,), "debugging", "analyze", "medium", None),
    ((_L01_DECIDE,), "debugging", "analyze", "medium", None),
    ((_L02_FUNCS,), "code_reading", "apply", "medium", None),
    ((_L03_REUSE,), "code_reading", "understand", "low", None),
    ((_L03_ERRORS,), "debugging", "analyze", "medium", None),
    ((_L03_ERRORS,), "debugging", "analyze", "medium", None),
    ((_L03_IMPORT,), "conceptual", "understand", "medium", None),
    ((_L04_OBJECTS,), "conceptual", "understand", "low", None),
    ((_L04_CTORS,), "code_reading", "apply", "medium", None),
    ((_L04_OBJECTS,), "conceptual", "understand", "low", None),
    ((_L04_CASH,), "financial_interpretation", "apply", "medium", None),
    ((_L05_INVARIANTS,), "debugging", "analyze", "medium", None),
    ((_L05_BOOK,), "conceptual", "understand", "medium", None),
    ((_L06_FAMILY,), "conceptual", "understand", "medium", None),
    ((_L06_FAMILY,), "debugging", "analyze", "medium", None),
    ((_L06_CONTRACT,), "debugging", "analyze", "medium", None),
    ((_L06_POLY,), "conceptual", "apply", "medium", None),
)


CANONICAL_METADATA = _build_metadata(
    "L15-CAN", CANONICAL, _CANONICAL_TRACE, _CANONICAL_SEMANTICS
)
EXTRA_METADATA = _build_metadata("L15-EXT", EXTRA, _EXTRA_TRACE)
CHECKPOINT_METADATA = _build_metadata("CK6", CHECKPOINT, _CHECKPOINT_TRACE)

# Registro único para auditorías y herramientas docentes. El valor conserva la
# correspondencia posicional pregunta↔metadata sin duplicar stems ni respuestas.
PUBLIC_BANKS = {
    "CANONICAL": (CANONICAL, CANONICAL_METADATA),
    "EXTRA": (EXTRA, EXTRA_METADATA),
    "CHECKPOINT": (CHECKPOINT, CHECKPOINT_METADATA),
}


# ---------------------------------------------------------------------------
# Muestreo balanceado por tema (para variantes reproducibles con --seed)
# ---------------------------------------------------------------------------
def _by_topic(pool: list) -> dict:
    d: dict = {}
    for q in pool:
        d.setdefault(q[5], []).append(q)
    return d


def sample_balanced(pool: list, targets: dict, seed: int) -> list:
    """Muestrea `targets[tema]` preguntas de cada tema, sin repetir, de forma
    reproducible por `seed`. El orden final también se baraja con la semilla.
    Si un tema no tiene suficientes, coge todas las que haya."""
    rng = _random.Random(seed)
    groups = _by_topic(pool)
    chosen: list = []
    for topic, k in targets.items():
        bucket = list(groups.get(topic, []))
        rng.shuffle(bucket)
        chosen.extend(bucket[:k])
    rng.shuffle(chosen)
    return chosen


# Reparto de la práctica pública por tema (coincide con las 40 canónicas)
EXAM_TARGETS = {
    "framework": 5, "oop": 5, "microstructure": 6, "matching": 8,
    "execution": 7, "mm": 4, "as": 5,
}
EXAM_POOL = CANONICAL + EXTRA

# Reparto del checkpoint (20 de 24)
CHECKPOINT_TARGETS = {"python": 8, "modules": 3, "oop": 9}
