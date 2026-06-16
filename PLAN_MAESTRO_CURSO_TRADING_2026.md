# Plan maestro — Curso de Trading Algorítmico 2026

> Versión "formato L1": el curso entero es **un solo proyecto que se construye clase a clase**,
> y cada clase sigue el formato pedagógico validado en la Clase 1.

---

## 1. Visión

15 clases de 40 min. El alumno **construye un paquete Python, `exchange/`** — un motor de
microestructura de mercado y un framework de estrategias modulares — y sobre él enchufa un
**VWAP**, un **market maker (Avellaneda-Stoikov)** y, al final, **su propia estrategia**.

El objetivo emocional: que el alumno **sienta que construye y aprende a la vez**, en una sola
historia continua, sin saltos. Aprende Python y algo trading simultáneamente, porque cada
concepto de programación aparece resolviendo un problema real de mercado.

---

## 2. Los 8 ingredientes del formato (principios pedagógicos)

Toda clase "L1-grade" cumple estos 8 puntos. Son innegociables:

1. **Un hilo único.** Cada clase elige UN objeto/idea concreto (el *hilo héroe*) y lo sigue de
   principio a fin: reto → simuladores → ejercicios → `.py`. En L1 fue `mid = (bid + ask) / 2`.
2. **Apertura como reto.** Se abre con un objetivo concreto que el alumno **aún no sabe hacer**;
   la clase es el viaje hasta lograrlo. Nada de "hoy veremos…".
3. **Presentación HTML interactiva** (Pyodide cuando hay código), diapositivas de **una sola
   idea**, con el **texto pegado a su simulador** (nunca hablar de X mientras se muestra Y),
   raíl de progreso en pipelines, **predice-antes-de-revelar** en los puntos clave, y
   **honestidad** sobre los límites de cada simplificación.
4. **Notebook de construcción** que **refleja el deck punto por punto y llega al clímax** que la
   presentación prometió. Validadores **plegados** (`source_hidden`) y soluciones en pestaña
   **desplegable** (`<details>`). Título y narrativa cuidados.
5. **Auxiliares** = drills extra + profundización/internals + el **puente** al problema de la
   clase siguiente.
6. **Un `.py` consolidado 1:1** con el núcleo del notebook: el alumno entiende que el código vive
   en archivos `.py`, no solo en celdas. Es el peldaño hacia la POO y el paquete.
7. **Mini-test A/B/C** (≈5 preguntas) al final del deck, con feedback inmediato: recall activo.
8. **Ganchos de continuidad.** Cada clase cierra plantando el dolor que resuelve la siguiente, y
   cada clase añade una pieza al paquete `exchange/` (la espina dorsal que crece).

**Tono:** directo, intuición antes que formalismo, mercado siempre (BTCUSDT), **código simple**
(alumnos iniciados — nada de abstracciones innecesarias). Fundamentos sin dependencias externas.

---

## 3. Las 3 capas de continuidad

Lo que hace que las 15 clases se sientan como **un curso, no 15 talleres**:

- **Macro-hilo (el artefacto):** el paquete `exchange/`. Cada clase añade un módulo que habla con
  los anteriores: `Order → OrderBook → MatchingEngine → Market → Strategy → Backtest → estrategias`.
- **Hilo héroe (por clase):** un objeto/idea concreto que se persigue toda la sesión.
- **El puente (entre clases):** cada cierre plantea la limitación que abre la siguiente clase.

### Cadena de puentes (la historia completa)
```
L1 calculo el mid, pero duplico variables por activo
  → L2 funciones sobre un libro… que todas reciben `book`
    → L3 `book` quiere ser un objeto: nace Order/Fill
      → L4 Orders sueltas: necesito un libro que las contenga + llevar la cuenta
        → L5 ya leo el libro real: ¿qué señal esconde? (imbalance)
          → L6 ¿y si MANDO una orden contra el libro? (matching, slippage)
            → L7 cruzar en un instante vs a lo largo del tiempo (el loop, PnL)
              → L8 mi estrategia es un `if` suelto: hazla modular (Strategy)
                → L9 ¿bate al benchmark o tuve suerte? (slippage vs arrival mid)
                  → L10 ejecutar una orden GRANDE sin mover el mercado (VWAP)
                    → L11 el perfil fijo falla si hoy es raro (volumen dinámico)
                      → L12 y si en vez de ejecutar, COTIZO (market making, inventario)
                        → L13 mi skew es heurístico: ¿el óptimo? (Avellaneda-Stoikov)
                          → L14 simular y elegir gamma; escribe TU estrategia
                            → L15 examen
```

---

## 4. Plantilla técnica por lección

```
NN-slug/
├── README.md                       # generado: teoría + técnico + ejercicios
├── CLAUDE.md                       # generado: guía de implementación
├── presentation/
│   ├── <slug>-interactive.html     # deck a medida (Pyodide) — full bespoke
│   └── guion.md                    # guion del profesor (custom)
├── exercises/
│   ├── exchange/                   # paquete acumulado (starter)        [L3+]
│   ├── NN_build_exercises.ipynb    # núcleo: refleja el deck, llega al clímax
│   ├── NN_auxiliary.ipynb          # drills + internals + puente
│   └── <script>.py                 # .py consolidado 1:1 con el núcleo
└── data/
```

**Producción:** el contenido vive en specs (`framework/_build/lessons_*.py` + `lessons_docs.py`);
`build_course.py` **autovalida cada ejercicio** y emite. Los decks y guiones a medida viven en
`framework/_build/custom/NN.html` y `NN_guion.md` y el generador los copia (no se sobreescriben).
**Decisión de calidad: las 15 llevan deck interactivo a medida nivel L1** (full bespoke).

**Estándar del deck (todas las clases):** Pyodide para ejecutar Python real; diapositivas de una
idea; raíl de progreso en pipelines; ≥1 momento *predice-antes-de-revelar*; notas de honestidad;
mini-test final; y **robustez**: las diapositivas explicativas funcionan aunque Pyodide falle
(aula sin wifi). Diseño compartido: `#09090b` / acento `#22d3ee` / bids `#4ade80` / asks
`#f87171`, Inter + JetBrains Mono, GSAP.

---

## 5. Blueprint de las 15 clases

Ficha por clase: **Reto · Hilo héroe · Pieza de `exchange/` · Simuladores · Núcleo (ejercicios) ·
Auxiliares · `.py` · Puente.**

### L1 · Python I — El modelo de datos  *(referencia, ya producida)*
- **Reto:** quiero que el ordenador calcule el `mid`; pero solo entiende 1s y 0s.
- **Hilo:** `mid = (bid + ask) / 2`.
- **Pieza:** (pre-paquete) order/snapshot como dicts.
- **Simuladores:** texto→bits · viaje tokens/AST/bytecode (real, `dis`) · compilar vs interpretar · editor en vivo · romper-código (fase del error) · rule builder.
- **Núcleo:** variables · spread/mid (tipos) · lista+indexing · for/acumulador · dict crear+acceder · if/elif · primer algoritmo (decide sobre mid).
- **Auxiliares:** notional · best_bid/ask · **multi-activo → POO** · ord/bin · dis.
- **`.py`:** `trading_snapshot.py` (funciones = ejercicios).
- **Puente:** añadir ETH duplica variables → objetos.

### L2 · Python II — El libro funcional
- **Reto:** mi script de BTC no escala a ETH sin duplicar todo.
- **Hilo:** el libro como lista, y las funciones que lo manosean (todas reciben `book`).
- **Pieza:** (pre-paquete) funciones `make_order`/`add_order`/`cancel_order`/`best_bid`/`imbalance`.
- **Simuladores:** libro vivo donde añades/cancelas órdenes y ves imbalance · "contador de duplicación" (cuántas funciones reciben `book`) · visual de estado compartido.
- **Núcleo:** make_order · add_order · cancel_order · best_bid/best_ask · imbalance · spread/mid por función.
- **Auxiliares:** total_notional · validación de side · reflexión "5 funciones, 1 book".
- **`.py`:** `order_book.py` (las funciones + un main que arma y mide un libro).
- **Puente:** todo recibe `book` → `book` quiere ser un objeto con métodos.

### L3 · OOP I — Order y Trade  *(PILOTO del nuevo formato)*
- **Reto:** 5 funciones manosean el mismo `book`; ¿y si el dato supiera operar consigo mismo?
- **Hilo:** el objeto `Order` (y `Fill`).
- **Pieza:** `exchange/orders.py`, `exchange/trades.py`.
- **Simuladores:** morph dict→clase animado · objeto `Order` interactivo (cambia campos → `notional`/`__repr__`) · signo del `cash_flow` (compra/venta) · "estado interno" (encapsulación).
- **Núcleo:** clase Order + `__init__` · método `notional` · `__repr__` · clase Fill · `cash_flow` · instanciar y operar juntas.
- **Auxiliares:** validar side (ValueError) · usar `exchange.orders` real · Side/OrderType como Enum.
- **`.py`:** `orders_demo.py` (define Order/Fill y un main que crea y describe órdenes).
- **Puente:** una orden y un fill sueltos; falta quién los contiene y lleva la cuenta.

### L4 · OOP II — OrderBook y PositionTracker
- **Reto:** tengo Orders sueltas; necesito un libro que las contenga y algo que lleve caja/posición.
- **Hilo:** composición — `OrderBook` contiene niveles; `PositionTracker` consume `Fill`.
- **Pieza:** `exchange/book.py`, `exchange/portfolio.py`.
- **Simuladores:** "objeto que contiene objetos" (book→niveles) · libro vivo con spread/mid/imbalance como métodos · PositionTracker comiendo Fills y actualizando equity.
- **Núcleo:** OrderBook init · best_bid/ask/spread/mid · imbalance · PositionTracker apply_fill · equity.
- **Auxiliares:** microprice · depth · `OrderBook.from_snapshot` real.
- **`.py`:** `book_demo.py` (construye un libro, lo mide, aplica fills, marca equity).
- **Puente:** el libro es una foto; ¿cómo lo leo de datos reales y qué señales esconde?

### L5 · Microestructura — Leer el libro  *(flagship)*
- **Reto:** 500 snapshots reales de BTC: ¿hacia dónde empuja el mercado antes de moverse?
- **Hilo:** el **imbalance** (y el microprice).
- **Pieza:** métricas en `book.py` + `Market.sample`.
- **Simuladores:** profundidad del LOB animada desde snapshots reales · medidor imbalance/microprice · "imbalance vs siguiente movimiento del mid" (predice-antes-de-revelar).
- **Núcleo:** Market.sample/step · spread/mid · imbalance(levels) · microprice · depth.
- **Auxiliares:** spread medio de la sesión · ¿predice el imbalance? (conteo).
- **`.py`:** `read_book.py` (carga el mercado y resume métricas de un snapshot).
- **Puente:** sé leer el libro; ¿qué pasa cuando MANDO una orden contra él?

### L6 · Órdenes y matching  *(flagship)*
- **Reto:** envío una market grande; ¿a qué precio se llena realmente?
- **Hilo:** una market order barriendo niveles (sus fills + precio efectivo).
- **Pieza:** `exchange/matching.py`.
- **Simuladores:** orden-contra-libro interactivo: pones limit/market/IOC/FOK, ves fills, el libro reacciona, y el slippage.
- **Núcleo:** market fill · limit + remanente · IOC · FOK · precio efectivo (VWAP de fills).
- **Auxiliares:** slippage vs tamaño · coste de cruzar N niveles.
- **`.py`:** `matching_demo.py` (cruza varios tipos contra un libro y muestra fills).
- **Puente:** cruzo una orden en UN instante; ¿y a lo largo del tiempo?

### L7 · El loop de simulación
- **Reto:** reproducir el día y llevar la cuenta de PnL.
- **Hilo:** la curva de equity en el tiempo.
- **Pieza:** `exchange/market.py` (Market loop).
- **Simuladores:** playback de snapshots con controles paso a paso · tracker de posición/equity que evoluciona.
- **Núcleo:** loop step (conteo) · submit en un paso · acumular posición · equity final.
- **Auxiliares:** schedule de participación a mano.
- **`.py`:** `replay.py` (recorre el mercado ejecutando y marcando equity).
- **Puente:** mi "estrategia" es un `if` suelto dentro del loop; ¿cómo la hago modular?

### L8 · El framework: Strategy + Backtest  *(flagship, pico arquitectónico)*
- **Reto:** quiero cambiar de estrategia sin reescribir el motor.
- **Hilo:** el contrato `Strategy` (polimorfismo).
- **Pieza:** `exchange/strategy.py`, `exchange/backtest.py`.
- **Simuladores:** "el enchufe" — intercambia estrategias en el mismo Backtest y ve resultados distintos · flujo animado `on_book_update → acciones → fills → on_fill`.
- **Núcleo:** subclase BuyOnce · Backtest.run · hook on_fill · SellOnce (polimorfismo).
- **Auxiliares:** estrategia con señal (imbalance) · comparar dos estrategias.
- **`.py`:** `my_strategy.py` (una subclase de Strategy + correrla con Backtest).
- **Puente:** tengo el enchufe; ¿una estrategia con señal de verdad y cómo la mido?

### L9 · Primera estrategia + métricas
- **Reto:** ¿mi estrategia bate al benchmark o tuve suerte?
- **Hilo:** el slippage vs el mid de llegada.
- **Pieza:** estrategia de imbalance + métricas sobre `BacktestResult`.
- **Simuladores:** curva de equity + línea de benchmark · slider de umbral (trade-off PnL/inventario) · "riesgo escondido" (equity alto con inventario alto).
- **Núcleo:** ImbalanceStrategy · medir (equity/pos/fills) · arrival mid · inventario como riesgo.
- **Auxiliares:** curva de equity (datos) · comparar umbrales.
- **`.py`:** `evaluate.py` (corre la estrategia y reporta métricas vs benchmark).
- **Puente:** ejecuté a lo bruto; ¿cómo ejecuto una orden GRANDE sin mover el mercado?

### L10 · VWAP I — Baselines  *(flagship)*
- **Reto:** vender 10 BTC sin hundir el precio.
- **Hilo:** el schedule de participación (TWAP vs VWAP).
- **Pieza:** `exchange/strategies/vwap.py`.
- **Simuladores:** trocear una orden grande a lo largo del día · perfil de volumen · comparar precio medio TWAP vs VWAP.
- **Núcleo:** pesos TWAP · VWAPStrategy run · perfil a medida · precio medio de ejecución.
- **Auxiliares:** el perfil se normaliza · cap de participación.
- **`.py`:** `run_vwap.py` (ejecuta un VWAP sobre el mercado y reporta el precio logrado).
- **Puente:** el perfil fijo asume que hoy = la media; ¿y si el flujo de hoy es raro?

### L11 · VWAP II — Volumen dinámico
- **Reto:** el volumen de hoy se desvía del perfil medio.
- **Hilo:** la predicción dinámica de volumen.
- **Pieza:** predicción + corrección sobre `VWAPStrategy`.
- **Simuladores:** predicción con ventana rolada · schedule estático vs dinámico · factor de corrección a tiempo.
- **Núcleo:** rolling_mean · predecir próximo volumen · perfil dinámico · factor de corrección.
- **Auxiliares:** regresión lineal a mano (puente ML).
- **`.py`:** `dynamic_vwap.py` (schedule que reacciona al flujo reciente).
- **Puente:** he sido el que EJECUTA; ¿y si soy el que COTIZA?

### L12 · Market making — Intro  *(flagship)*
- **Reto:** ganar el spread cotizando a dos lados sin que el inventario me hunda.
- **Hilo:** el inventario (y el skew).
- **Pieza:** `exchange/strategies/market_maker.py`, `exchange/simulation.py`.
- **Simuladores:** `MMSimulation` con senda de inventario + PnL · skew on/off · cotizaciones alrededor del mid.
- **Núcleo:** quotes · skew baja cotizaciones si largo · reservation price · simular el MM.
- **Auxiliares:** utilidad CARA · efecto de gamma.
- **`.py`:** `run_mm.py` (simula un market maker naive e imprime PnL/inventario).
- **Puente:** mi skew es heurístico; ¿cuál es el óptimo?

### L13 · Avellaneda-Stoikov I — El modelo
- **Reto:** ¿cuánto inclino y cuánto separo mis cotizaciones, de forma óptima?
- **Hilo:** el reservation price y el optimal spread.
- **Pieza:** `AvellanedaStoikov(MarketMaker)`.
- **Simuladores:** reservation price vs inventario/tiempo (sliders) · optimal spread vs gamma · A-S vs naive (cotizaciones).
- **Núcleo:** reservation price (signo) · optimal spread (positivo) · quotes A-S · el inventario inclina el centro.
- **Auxiliares:** el tiempo apaga el ajuste (decaimiento).
- **`.py`:** `avellaneda.py` (imprime r y spread óptimo para varios inventarios).
- **Puente:** tengo las fórmulas; ¿cómo se comportan al simular y qué hace gamma?

### L14 · Avellaneda-Stoikov II — Simulación  *(flagship)*
- **Reto:** simular el MM A-S y elegir gamma.
- **Hilo:** la senda de inventario según gamma.
- **Pieza:** barridos sobre `MMSimulation`.
- **Simuladores:** simulación completa (mid + inventario + PnL) · barrido de gamma · A-S vs naive · **escribe tu estrategia** (subclasea y enchufa).
- **Núcleo:** simular A-S · skew reduce inventario · gamma vs magnitud del reservation · subclase propia.
- **Auxiliares:** sensibilidad de parámetros.
- **`.py`:** `mm_sweep.py` (barre gamma y compara inventario/PnL).
- **Puente:** has construido el motor entero y tu propia estrategia → examen.

### L15 · Examen final
- Test de 40 min, 40 preguntas (A/B/C), +1 acierto / −0.5 fallo. Cubre todo el arco, incluido
  código del propio framework. Generador en `15-final-exam/generate_exam.py`.

---

## 6. Estándar de calidad y proceso de producción

- **Calidad:** las 15 con deck a medida nivel L1 (full bespoke). Notebook + auxiliares + `.py` +
  mini-test de la misma calidad en todas.
- **Autovalidación:** ningún ejercicio se publica sin pasar `build_course.py --check-only`.
- **Proceso:**
  1. Este plan aprobado.
  2. **Piloto: L3 (OOP I)** — primera clase con el formato completo tras L1; se revisa antes de seguir.
  3. Producción del resto en orden de bloque, reusando lo rescatable de `_archive_v1/` por lección.
- **Anexo:** bonos y RFQ quedan en `annex-bonds-rfq/` (material opcional, fuera del arco).

---

## 7. Riesgos y mitigación

- *Decks carísimos × 15* → reutilizar el andamiaje de L1 (Pyodide, estilos, patrones de
  simulador) como librería de componentes; pilotar L3 para medir esfuerzo real.
- *Romper la continuidad* → la cadena de puentes (§3) y el paquete acumulado son el control.
- *Sobre-ingeniería* → código simple para iniciados; el generador autovalida; las firmas del
  paquete están cerradas en `framework/exchange/`.
- *Pyodide en aula sin wifi* → las diapositivas explicativas deben funcionar sin Python; los
  simuladores en vivo son un plus, no la base.
