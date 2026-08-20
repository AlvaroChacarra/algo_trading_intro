"""lessons_docs.py — contexto teórico y técnico por lección.

Alimenta los README.md y CLAUDE.md de cada carpeta. `theory` = trasfondo
conceptual (trading + CS); `technical` = qué se construye y cómo encaja con las
piezas anteriores. Markdown libre.
"""

DOCS = {
1: {
"theory": """**Un lenguaje de programación formaliza nuestra intención para que una máquina pueda
ejecutarla.** La línea `mid = (bid + ask) / 2` no llega directamente a la CPU. Python es el
lenguaje; **CPython** es su implementación estándar, escrita principalmente en C. CPython analiza
el source, lo compila a **Python bytecode** y ejecuta ese bytecode mediante su máquina virtual.

El viaje es: source → tokens → árbol (AST) → Python bytecode → CPython VM → CPU. El bytecode
contiene instrucciones para la VM y no es machine code nativo de x86-64 o ARM64. Por tanto:
**Python source ≠ bytecode ≠ machine code** y **CPython ≠ bytecode**.

C++ suele seguir otro pipeline: source → GCC/Clang/MSVC → machine code nativo → CPU. C++ ofrece
rendimiento, control y detección de muchos errores antes de ejecutar. Python destaca por su ciclo
`write → run → inspect → fix`, su interactividad y su ecosistema. Un **SyntaxError** impide compilar
el source; otros errores pueden aparecer cuando la VM alcanza la operación problemática. Sobre
este modelo construimos un algoritmo: **dato → cálculo → decisión** (snapshot → `spread`/`mid` →
un `if` que decide).""",
"technical": """Sin paquete todavía: tipos básicos (`int`, `float`, `str`), listas, diccionarios, `for`,
`if` y funciones. Una orden es un `dict` con `symbol`, `side`, `price`, `size`; un libro es una
lista de esos dicts.

La presentación HTML (a medida, con **Pyodide** ejecutando Python real en el navegador) lleva 5
simuladores: texto→bits (`ord`/`bin`), CPython vs compilación nativa, el viaje de una línea con
**tokens/AST/bytecode reales** (`tokenize`/`ast`/`dis`), el editor en vivo, los retos de
romper-código y el rule builder. El notebook refuerza con `ord`/`bin` y `dis` (auxiliares A4-A5).

Continuidad: el vocabulario (`symbol/side/price/size`) será **literalmente** el de los atributos
de la clase `Order` en L3. Los dicts de hoy son los objetos de pasado mañana.""",
},
2: {
"theory": """Una función encapsula una idea reutilizable. Un **libro de órdenes** es una lista de
órdenes; añadir, cancelar y medir presión son operaciones sobre esa lista. El **imbalance**
`(vol_buy - vol_sell)/(vol_buy + vol_sell)` resume de qué lado empuja el mercado en [-1, 1].

El momento clave es pedagógico: cuando cinco funciones distintas reciben todas el mismo
`book` como primer argumento y lo manosean, el código está pidiendo a gritos que `book` deje
de ser un dato pasivo y se convierta en un **objeto con métodos**. Ese es el puente a OOP.""",
"technical": """Funciones puras que construyen y transforman datos: `make_order`, `add_order(book, order)`,
`cancel_order(book, id)`, `best_bid/best_ask(book)`, `spread/mid(book)`, `imbalance(book)`. Todas
reciben `book` explícitamente — anticipan exactamente los métodos de `OrderBook` en L4
(`book.best_bid()`, `book.imbalance()`). Cero clases: el objetivo es *sentir el dolor* del estado
compartido.

El deck a medida (Pyodide) trae un **libro vivo** interactivo: añades/cancelas órdenes y ves
best_bid/ask, spread, mid e imbalance reaccionar. El núcleo son 7 ejercicios que culminan en
"construye y lee tu libro"; el auxiliar cuenta cuántas funciones reciben `book` (7 → puente a
POO). `order_book.py` consolida las funciones + un `main` 1:1 con el núcleo.""",
},
3: {
"theory": """Programación orientada a objetos: una **clase** es una plantilla; un **objeto** es una
instancia rellena. La idea central es juntar **datos y comportamiento**: la orden no solo
guarda su precio y tamaño, sabe calcular su nocional. `__repr__` hace que el objeto sepa
describirse a sí mismo.

En mercado: una `Order` (intención) y un `Fill` (ejecución). El **cash flow** de un fill lleva
signo: comprar saca caja (negativo), vender la mete (positivo). Esa convención de signo es la
base de todo el PnL del curso.""",
"technical": """Primeros módulos reales del paquete: `exchange/orders.py` (`Order`, `Side`, `OrderType`) y
`exchange/trades.py` (`Fill`). `Side` y `OrderType` heredan de `str, Enum`: se comparan con
`"buy"`/`"sell"` como antes, pero rechazan valores inválidos. `Order.notional()` reemplaza la
función `compute_notional` de L1; `Fill.cash_flow()` formaliza el signo por lado.

El deck a medida (Pyodide) trae el morph dict→clase, un **Order inspector** (cambias
side/price/size y ves notional y `__repr__`) y un visualizador del **signo del cash_flow**. El
núcleo son 6 ejercicios que culminan en "de la orden al dinero" (Order→Fill→cash_flow); el `.py`
entregable es `orders_demo.py`.

Continuidad: los atributos son los campos del dict de L1. En el cuaderno se construyen las
clases *inline* (estilo L1-L2); el paquete `exchange/` las trae ya pulidas como referencia.
Puente: una orden suelta; ¿quién suma los cash_flows y lleva la cuenta? El PositionTracker (L5).""",
},
4: {
"theory": """Dos ideas de diseño: **composición** (un objeto contiene otros) y **encapsulación**
(estado interno que se toca solo por métodos). El `OrderBook` contiene niveles de precio y
expone métricas como métodos. El `PositionTracker` es una pequeña máquina de estado: parte de
caja y posición a cero y las actualiza con cada `Fill`.

El concepto financiero clave es **equity** = `cash + position · mark_price`: tu valor total
marcando el inventario al precio actual de mercado. Es la fotografía de PnL que se usará en
todos los backtests.""",
"technical": """`exchange/book.py` (`OrderBook`, `Level`) con bids ordenados desc y asks asc, y métodos
`best_bid/best_ask/spread/mid/imbalance`. `exchange/portfolio.py` (`PositionTracker`) con
`_cash`/`_position` como implementación interna, `apply_fill(fill)` y `equity(mark)`.

Composición explícita: `OrderBook` contiene `Level`; `PositionTracker.apply_fill` consume
objetos `Fill` de L3. Aquí el alumno *ve* a los objetos hablándose entre sí — el objetivo
declarado del curso.

El deck a medida (Pyodide) trae un inspector del `OrderBook` (métricas como métodos) y un widget
del `PositionTracker` (pulsas fills y ves cash/posición/equity, con slider de mark). El núcleo
son 6 ejercicios que culminan en "los dos objetos, juntos"; el `.py` entregable es `book_demo.py`.
Puente: ya creas (L4) y compones (L5) objetos; falta la última pieza de OOP — compartir un
esqueleto entre muchos objetos: herencia (L6).""",
},
5: {
"theory": """Microestructura: cómo se forma el precio en el detalle del libro.
- **Spread**: coste implícito de cruzar de un lado a otro.
- **Mid** vs **microprice**: el microprice pondera el mid por el tamaño del lado *contrario*,
  porque el lado con menos tamaño es el que probablemente se mueva — mejor predictor a corto.
- **Imbalance**: presión compradora/vendedora; un imbalance positivo suele preceder subidas.
- **Depth**: cuánto aguanta el libro un golpe (resiliencia).

Distinción importante: la **liquidez visible** del libro es intención, no negociación; puede
cancelarse antes de ejecutarse.""",
"technical": """`book.py` gana las métricas de lectura (`microprice`, `imbalance(levels)`,
`depth(side, levels)`). `market.py` aporta `Market.sample()` — carga 500 snapshots reales de
BTCUSDT empaquetados (`exchange/_data/`) sin configurar rutas — y `OrderBook.from_snapshot`.

A partir de aquí los ejercicios trabajan sobre datos reales con `Market.sample().step()`. El
paquete acumulado ya incluye el motor de datos completo.""",
},
6: {
"theory": """El **matching** convierte el libro de foto estática en mercado con dinámica. Prioridad
precio-tiempo: una orden entrante consume primero los mejores niveles del lado contrario.

Tipos de orden y su trade-off **coste / certeza / riesgo**:
- **MARKET**: cruza al precio que haga falta; segura pero paga **slippage** al barrer niveles.
- **LIMIT**: solo cruza a tu precio o mejor; barata pero el resto descansa (incierta).
- **IOC** (immediate-or-cancel): cruza lo que pueda, cancela el resto.
- **FOK** (fill-or-kill): todo o nada.

El **precio efectivo** de una market es el VWAP de sus fills, peor que el best ask cuanto más grande.""",
"technical": """`exchange/matching.py` (`MatchingEngine.process(order, book) -> list[Fill]`): recorre el lado
contrario, planifica el cruce, aplica FOK (todo-o-nada), consume liquidez (muta el libro) y
descansa el remanente de una LIMIT. Devuelve los `Fill` generados.

Conecta todo lo anterior: recibe `Order` (L3), opera sobre `OrderBook` (L4), produce `Fill`
(L3). Es la primera pieza con lógica de ramas no trivial.""",
},
7: {
"theory": """Una simulación de mercado = **estado** (el libro) + **dinámica** (el matching) +
**tiempo** (el loop). El **replay** reproduce snapshots históricos en orden; en cada instante
puedes enviar órdenes contra el libro de ese momento.

Llevar la cuenta en el tiempo es lo que distingue un cálculo puntual de una estrategia: se
acumulan fills en un `PositionTracker` y se marca el equity a cada paso, obteniendo la curva
de PnL. Modelo de simulación: el libro se reconstruye en cada snapshot, así que las órdenes
límite no persisten entre pasos (las estrategias que quieren persistencia re-cotizan).""",
"technical": """`exchange/market.py` (`Market`): `step()` reconstruye el libro desde el siguiente snapshot
y lo devuelve (o `None` al acabar); `submit(order)` cruza contra el libro actual vía el
`MatchingEngine`; `reset()` rebobina. Se compone con `PositionTracker` para seguir inventario
y equity. Es el andamiaje sobre el que se monta el `Backtest` en L8.""",
},
8: {
"theory": """El principio de diseño más importante del curso: **separar la decisión de la ejecución**.
Una estrategia no ejecuta órdenes — las *pide*. Reacciona al libro y devuelve acciones; el
motor decide qué hacer con ellas.

Eso se modela con una **clase base abstracta** (interfaz) y **polimorfismo**: cualquier
subclase de `Strategy` encaja en el mismo runner. Esta ignorancia mutua (la estrategia no sabe
del motor, el motor no sabe de la estrategia concreta) es lo que hace el sistema modular y
permite que el alumno enchufe la suya.""",
"technical": """`exchange/strategy.py`: `Strategy(ABC)` con `on_book_update(book) -> list[Action]`
(abstracto), `on_fill`, `on_start/on_end`; acciones `NewOrder` y `Cancel`.
`exchange/backtest.py`: `Backtest(market, strategy)` recorre el mercado, pasa cada libro a la
estrategia, ejecuta sus acciones contra el matching, actualiza el `PositionTracker` y registra
`BacktestResult` (fills, equity_curve, final_equity/position). El **mismo** `run()` sirve para
toda estrategia — el pico arquitectónico del curso.""",
},
9: {
"theory": """Una estrategia de verdad necesita una **señal** y una **métrica honesta**. La señal aquí es
el imbalance: largo cuando el libro empuja arriba, corto cuando empuja abajo.

Medir bien exige un **benchmark**: el **mid de llegada** (arrival mid). Tu ejecución es buena
si compraste por debajo (o vendiste por encima) de él — eso es el **slippage**. Y cuidado con
el **riesgo escondido**: un equity positivo acompañado de un inventario enorme no es una buena
estrategia, es una apuesta direccional disfrazada. Por eso se miran a la vez equity, posición
final y número de fills.""",
"technical": """Subclase de `Strategy` parametrizada por umbral, usando `book.imbalance(3)`. Lectura
completa de `BacktestResult`: `final_equity`, `final_position`, `n_fills`, `equity_curve`.
Comparación de umbrales (más bajo = más operaciones = más inventario). Cierra el bloque
L1–L9: el motor está completo y se puede medir. Checkpoint integrador.""",
},
10: {
"theory": """Primer algoritmo de **ejecución**. Mandar una orden grande de golpe barre el libro y paga
impacto; **trocearla** en el tiempo lo reduce. Dos baselines:
- **TWAP** (time-weighted): trozos iguales en el tiempo. Honesto y difícil de batir sin info.
- **VWAP** (volume-weighted): pondera por el **perfil de volumen** intradía, para acercarse al
  precio medio ponderado por volumen — el benchmark estándar de ejecución institucional.

El perfil son pesos relativos: se normalizan, así que importan las proporciones, no la escala.""",
"technical": """`exchange/strategies/vwap.py` (`VWAPStrategy(symbol, side, total_size, horizon, profile)`):
en cada tick emite una market order del tamaño del trozo (peso normalizado × total). Sin
perfil → TWAP uniforme. Es una subclase de `Strategy`: se enchufa al `Backtest` exactamente
igual que cualquier otra — primera demostración del valor del framework de L8.""",
},
11: {
"theory": """El perfil fijo asume que hoy se parece a la media. Pero el **flujo reciente informa**: si
el volumen de los últimos intervalos se desvía, conviene reaccionar.
- **Ventana rolada**: predice el volumen del próximo intervalo como media de los últimos *k*.
- **Perfil dinámico**: normaliza las predicciones en pesos.
- **Factor de corrección**: si vas por detrás del plan, acelera; si vas por delante, frena.

Extensión opcional: predecir volumen con una **regresión** es el primer paso de ML aplicado;
la pendiente de mínimos cuadrados (cov/var) es lo que hace `LinearRegression` por dentro.""",
"technical": """Funciones de predicción en stdlib: `rolling_mean`, normalización a perfil, `correction(
target_so_far, executed, remaining)`. El perfil dinámico se pasa a `VWAPStrategy`. La
regresión a mano (`slope = cov/var`) mantiene el curso sin dependencias y desmitifica el ML.
Aquí encaja, como auxiliar, el antiguo pipeline de data science del curso.""",
},
12: {
"theory": """El otro lado del mercado: el **market maker** cotiza bid y ask y gana el **spread**. Su
enemigo es el **inventario**: si el flujo es desequilibrado acumula posición justo cuando el
mercado va en su contra (**adverse selection**).

Aparece la **utilidad CARA** `-e^{-γW}` y el parámetro de **aversión al riesgo** γ. La primera
defensa es el **skew por inventario**: el *reservation price* = `mid - skew·inventario` baja
ambas cotizaciones cuando estás largo, para que te compren menos y te vendan más y vuelvas a
plano.""",
"technical": """`exchange/strategies/market_maker.py` (`MarketMaker`): `quotes(book) -> (bid, ask)` en torno
al `reservation_price`, `on_fill` actualiza el inventario interno. Y `exchange/simulation.py`
(`MMSimulation`): como una limit no se cruza en el replay de snapshots, el market making se
simula contra un mid en paseo aleatorio con **modelo de intensidad de fills**
`λ(δ) = A·e^{-κδ}` (más cerca del mid, más probable que te ejecuten).""",
},
13: {
"theory": """**Avellaneda-Stoikov (2008)** sustituye el skew heurístico por el óptimo. Sale de maximizar
utilidad CARA sobre la riqueza final con inventario incierto; la solución (vía la ecuación
HJB de control óptimo estocástico — no hace falta derivarla) da dos fórmulas cerradas:

- **Reservation price**: `r = s − q·γ·σ²·(T−t)` — el mid ajustado por inventario `q` y tiempo.
- **Optimal spread**: `d = γ·σ²·(T−t) + (2/γ)·ln(1 + γ/κ)` — cuánto separas tus cotizaciones.

Detalle clave: el ajuste por inventario **se apaga al acercarse el cierre** (`t → T`).""",
"technical": """`AvellanedaStoikov(MarketMaker)`: parámetros `gamma`, `sigma`, `kappa`, `horizon`; sobrescribe
`reservation_price` y añade `optimal_spread`, y `quotes` cotiza simétrico en torno a `r`. El
contador `_t` avanza el tiempo. Al ser subclase de `MarketMaker`, hereda `on_fill`/inventario y
se enchufa al mismo `MMSimulation`. Demuestra herencia + especialización.""",
},
14: {
"theory": """Poner el modelo a correr. Frente a un market maker naive, el A-S **controla el inventario**
mucho mejor: el reservation price lo empuja a soltar antes de cargar demasiado.

El **barrido de γ** muestra el trade-off sin atajos: más aversión inclina más el reservation
price y reduce el inventario máximo, pero al cotizar más defensivo captura menos spread (menos
PnL). No hay free lunch — esa es la intuición que se lleva el alumno. El cierre del bloque es
que el alumno **escribe su propia estrategia** y la enchufa al simulador.""",
"technical": """`MMSimulation(strategy, steps, A, kappa, sigma)` → `SimResult(mid, inventory, pnl)` con
`final_pnl` y `max_inventory`. Ejercicios de comparación: skew vs no-skew (determinista, misma
semilla), magnitud del reservation price vs γ. Auxiliar: subclasear `MarketMaker` (p.ej.
`FlatMaker`) y simularlo — el alumno cierra el círculo escribiendo y enchufando lo suyo.""",
},
}


# Textos de las clases NUEVAS del rediseño a 6 fundamentos (numeración actual).
EXTRA_DOCS = {
3: {
"theory": """Cuando tus funciones crecen, no pueden vivir sueltas en un notebook: las guardas en un
archivo `.py` — un **módulo** — y lo **importas** desde donde lo necesites. `import order_book`
trae el módulo entero; `from order_book import spread` trae solo una función. Así reutilizas
código sin copiarlo, que es justo lo que harás con el paquete `exchange/` desde la clase 7
(`import exchange`).

La segunda mitad de la clase son los **errores**: una función como `best_bid` revienta con un
libro vacío. `try/except` atrapa el fallo y devuelve algo sensato; `raise` lanza un error claro
cuando el dato no tiene sentido. Una librería de verdad no se cae con un dato raro.""",
"technical": """Pre-paquete: se trabaja con el módulo `order_book.py` (las funciones de L2) y un `main.py`
que lo importa. El deck a medida (Pyodide) escribe el módulo en el sistema de archivos virtual y
lo importa en vivo. Conceptos: `import` vs `from ... import`, alias, `try/except`, `raise`,
excepciones propias, `if __name__ == "__main__"` y argumentos por defecto. El núcleo (6) culmina
construyendo y leyendo un libro a través del módulo importado; el `.py` entregable es
`order_book.py` (módulo) + `main.py` (lo importa). Puente: el código ya es una librería, pero
datos y funciones siguen separados → juntarlos = objetos (L4).""",
},
6: {
"theory": """La pieza que sostiene todo el framework: vas a tener **muchas estrategias** que comparten un
esqueleto. La **herencia** deja que una subclase reutilice y **sobrescriba** los métodos de una
base. Una **clase abstracta** (`ABC` + `@abstractmethod`) fija un contrato: no se puede
instanciar hasta implementar el método. Y el **polimorfismo** es llamar al mismo método sobre
objetos distintos y que cada uno responda lo suyo — el código que los usa no necesita saber cuál
es cuál.

Se enseña construyendo una familia `Strategy` de juguete (Momentum, Contrarian): exactamente el
patrón que en la clase 10 se conecta al motor real. El alumno llega al framework con la herencia
ya dominada, no a presión.""",
"technical": """Pura OOP, sin dependencias: una base abstracta `Strategy` con `@abstractmethod decide` y
subclases que la implementan; un bucle polimórfico (`[s.decide(imb) for s in strategies]`).
Conceptos: herencia, override, `super().__init__`, `ABC`/`@abstractmethod`, `isinstance`,
polimorfismo. El deck a medida (Pyodide) trae un **simulador de polimorfismo** en vivo: mueves el
imbalance y Momentum/Contrarian/Flat deciden cada uno lo suyo con la misma llamada. El `.py`
entregable es `strategies_toy.py` (base + Momentum + Contrarian + bucle polimórfico). Puente
directo a L10: ese `Strategy` de juguete se formaliza como la interfaz del framework y se enchufa
al `Backtest`.""",
},
}
