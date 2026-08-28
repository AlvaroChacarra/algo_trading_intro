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

Continuidad: el vocabulario (`symbol/side/price/size`) reaparece en `OrderMini` en L4 y, tras
la migración explícita de firma, en el `Order` estable de `exchange`. Los dicts de L1 son el
estado que L4 convertirá en objetos.""",
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
reciben `book` explícitamente — anticipan la API de `OrderBook` en L5: métricas sin
argumentos como properties (`book.best_bid`, `book.mid`) y operaciones parametrizadas
como métodos (`book.imbalance(levels)`). Cero clases: el objetivo es *sentir el dolor* del estado
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

Continuidad: los atributos son los campos del dict de L1. Para no fingir que dos firmas distintas
son la misma API, el cuaderno construye `OrderMini(symbol, side, price, size)` y
`FillMini(symbol, side, price, size)`. Antes de entrar en `exchange/` se muestra la migración:
`Order(symbol, side, size, price=...)` añade tipo/id y `Fill(order_id, symbol, side, price, size)`
añade trazabilidad. Esos nombres y firmas públicas quedan estables desde L4.

Puente: una orden suelta; ¿quién suma los cash flows y lleva la cuenta? `PositionTracker` (L5).""",
},
4: {
"theory": """Dos ideas de diseño: **composición** (un objeto contiene otros) y **encapsulación**
(estado interno que se toca solo por su API). El `OrderBook` contiene niveles de precio y
expone las métricas sin argumentos como properties estables. El `PositionTracker` es una pequeña máquina de estado: parte de
caja y posición a cero y las actualiza con cada `Fill`.

El concepto financiero clave es **equity** = `cash + position · mark_price`: tu valor total
marcando el inventario al precio actual de mercado. Es la fotografía de PnL que se usará en
todos los backtests.""",
"technical": """`exchange/book.py` (`OrderBook`, `Level`) con bids ordenados desc y asks asc;
`best_bid/best_ask/spread/mid` son properties e `imbalance(levels)` es método. `exchange/portfolio.py` (`PositionTracker`) con
`_cash`/`_position` como implementación interna, `apply_fill(fill)` y `equity(mark)`.

La construcción usa `OrderBookMini(bids, asks)` con tuplas para aislar composición y properties.
La migración se declara antes de usar el paquete: `OrderBook(symbol, bids: list[Level],
asks: list[Level])`. Las lecturas `best_bid`, `best_ask`, `spread`, `mid` siguen siendo properties
e `imbalance(levels)` sigue siendo método. `PositionTracker.apply_fill` consume el `Fill` estable
introducido en L4.

El deck a medida (Pyodide) trae un inspector del `OrderBook` (métricas como properties) y un widget
del `PositionTracker` (pulsas fills y ves cash/posición/equity, con slider de mark). El núcleo
son 6 ejercicios que culminan en "los dos objetos, juntos"; el `.py` entregable es `book_demo.py`.
Puente: ya creas (L4) y compones (L5) objetos; falta la última pieza de OOP — compartir un
esqueleto entre muchos objetos: herencia (L6).""",
},
5: {
"theory": """El problema de diseño es convertir una representación externa y plana en estado interno
con invariantes. Cada pareja precio/tamaño se agrupa en `Level`; los niveles se separan por lado;
el constructor ordena bids descendentes y asks ascendentes.

Una vez construida esa frontera, las métricas de microestructura son métodos del objeto:
`depth` agrega tamaños, `imbalance` compone dos llamadas a `depth` y `microprice` usa el primer
nivel. El conocimiento funcional de las métricas es previo; aquí importa programar la API.""",
"technical": """`exchange/book.py`: `Level`, `OrderBook.__init__`, la factory
`OrderBook.from_snapshot`, `depth(side, levels)`, `imbalance(levels)` y `microprice`.

El notebook construye una versión del alumno desde un snapshot pequeño y termina aplicándola a
la primera fila real del CSV. Solo al final compara comportamiento con el `OrderBook` canónico;
no usa `Market` como caja negra.""",
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

Conecta todo lo anterior: recibe `Order` (L4), opera sobre `OrderBook` (L5), produce `Fill`
(L4). La separación PLAN → VALIDATE → COMMIT hace atómica una FOK fallida.""",
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
y equity. Es el andamiaje sobre el que se monta el `Backtest` en L10.""",
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

Medir bien exige separar dos benchmarks. El **parent arrival** es el mid del primer snapshot y
evalúa la decisión completa de empezar a operar. El **decision mid** de cada orden hija evalúa
solo su ejecución: comprar por encima o vender por debajo de ese mid produce slippage adverso.
No se mezclan ambas preguntas. Y cuidado con el **riesgo escondido**: un equity positivo con un
inventario enorme no es una buena estrategia, sino una apuesta direccional disfrazada.""",
"technical": """Subclase de `Strategy` parametrizada por umbral, usando `book.imbalance(3)`. La ruta
LIVE lee `final_equity`, `final_position` y `n_fills` de `BacktestResult`; el juez de slippage
usa el decision mid vigente cuando nace cada orden hija. La ruta REQUIRED consolida cálculos e
interpretación; dibujar `equity_curve` con matplotlib queda **OPTIONAL** y no se evalúa.
Comparar umbrales (más bajo = más operaciones = más inventario) cierra el bloque L1–L10: L10
aportó el contrato y el runner que aquí se someten a métricas honestas.""",
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
igual que cualquier otra — primera demostración del valor del framework de L10.

La predicción dinámica de volumen queda como profundización **OPTIONAL**: ningún contenido ni
assessment posterior la presupone; LIVE + REQUIRED se sostienen con slicing, TWAP, el perfil
VWAP estático y una comparación empírica honesta.""",
},
11: {
"theory": """El perfil fijo asume que hoy se parece a la media. Como prototipo aislado se puede
preguntar si el **flujo reciente informa** y comparar un perfil candidato con el baseline.
- **Ventana rolada**: predice el volumen del próximo intervalo como media de los últimos *k*.
- **Perfil candidato**: normaliza las predicciones en pesos para compararlas offline.
- **Factor de corrección**: calcula cuánto faltaría para volver al plan; no se conecta al runner.

Extensión opcional: predecir volumen con una **regresión** es el primer paso de ML aplicado;
la pendiente de mínimos cuadrados (cov/var) es lo que hace `LinearRegression` por dentro.""",
"technical": """Funciones auxiliares en stdlib: `rolling_mean`, normalización a perfil, `correction(
target_so_far, executed, remaining)`. Se estudian y validan por separado; la `VWAPStrategy`
canónica recibe una lista fija y no reestima pesos durante `Backtest`. Integrar esas piezas en
un controlador adaptativo queda fuera del alcance. La regresión a mano (`slope = cov/var`)
mantiene el curso sin dependencias y desmitifica el ML.""",
},
12: {
"theory": """El otro lado del mercado: el **market maker** cotiza bid y ask y gana el **spread**. Su
enemigo es el **inventario**: si el flujo es desequilibrado acumula posición justo cuando el
mercado va en su contra (**adverse selection**).

Aparece la **utilidad CARA** `-e^{-γW}` y el parámetro de **aversión al riesgo** γ. La primera
defensa es el **skew por inventario**: el *reservation price* = `mid - skew·inventario` baja
ambas cotizaciones cuando estás largo, para que te compren menos y te vendan más y vuelvas a
plano. CARA y la intuición de intensidad de fills forman un puente **LIVE** a γ/κ en
L14; la estrategia concreta y sus fórmulas no se exponen en L13.""",
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

- **Tiempo normalizado**: `τ = (T−t)/T`, por tanto `τ ∈ [0,1]`.
- **Reservation price**: `r = s − q·γ·σ²·τ` — el mid ajustado por inventario `q` y tiempo.
- **Optimal spread**: `d = γ·σ²·τ + (2/γ)·ln(1 + γ/κ)` — cuánto separas tus cotizaciones.

Detalle clave: el ajuste por inventario **se apaga al acercarse el cierre** (`t → T`).""",
"technical": """`exchange/strategies/avellaneda_stoikov.py` introduce por primera vez en L14
`AvellanedaStoikov(MarketMaker)`: parámetros `gamma`, `sigma`, `kappa`, `horizon`; sobrescribe
`reservation_price` y añade `optimal_spread`, y `quotes` cotiza simétrico en torno a `r`. El
reloj público `time` avanza el tiempo. Al ser subclase de `MarketMaker`, hereda `on_fill`/inventario y
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
código sin copiarlo, que es justo lo que harás con el paquete `exchange/` desde L4
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
patrón que en L10 se conecta al motor real. El alumno llega al framework con la herencia
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
