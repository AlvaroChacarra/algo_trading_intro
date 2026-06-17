# Plan maestro — Curso de Trading Algorítmico 2026

> Versión "formato L1 · 6 fundamentos": el curso entero es **un solo proyecto que se construye
> clase a clase**, cada clase sigue el formato pedagógico validado en L1, y el bloque de código
> (Python + OOP) está bien cubierto antes de tocar el motor.

---

## 1. Visión

15 clases de 40 min. El alumno **construye un paquete Python, `exchange/`** — un motor de
microestructura de mercado y un framework de estrategias modulares — y sobre él enchufa un
**VWAP**, un **market maker (Avellaneda-Stoikov)** y, al final, **su propia estrategia**.

Objetivo emocional: que el alumno **sienta que construye y aprende a la vez**, en una sola
historia continua, sin saltos. Aprende Python y algo trading simultáneamente, porque cada
concepto de programación aparece resolviendo un problema real de mercado.

---

## 2. Los 8 ingredientes del formato (principios pedagógicos)

Toda clase "L1-grade" cumple estos 8 puntos. Son innegociables:

1. **Un hilo único** (el *hilo héroe*) que recorre la clase: reto → simuladores → ejercicios → `.py`.
2. **Apertura como reto**: un objetivo concreto que el alumno **aún no sabe hacer**.
3. **Presentación HTML interactiva** (Pyodide cuando hay código), diapositivas de **una idea**,
   texto **pegado a su simulador**, raíl de progreso, **predice-antes-de-revelar** y honestidad.
4. **Notebook de construcción** que **refleja el deck y llega al clímax**. Validadores **plegados**
   (`source_hidden`) y soluciones en **`<details>`** desplegable. Título y narrativa cuidados.
5. **Auxiliares** = drills + profundización/internals + el **puente** a la clase siguiente.
6. **Un `.py` consolidado 1:1** con el núcleo del notebook.
7. **Mini-test A/B/C** (≈5 preguntas) al final del deck, con feedback inmediato.
8. **Ganchos de continuidad**: cada clase planta el dolor de la siguiente; el paquete `exchange/` crece.

**Tono:** directo, intuición antes que formalismo, mercado siempre (BTCUSDT), **código simple**
(alumnos iniciados). Fundamentos sin dependencias externas.

---

## 3. Las 3 capas de continuidad

- **Macro-hilo (el artefacto):** el paquete `exchange/`. Cada clase añade un módulo que habla con
  los anteriores: `Order → OrderBook → MatchingEngine → Market → Strategy → Backtest → estrategias`.
- **Hilo héroe (por clase):** un objeto/idea concreto que se persigue toda la sesión.
- **El puente (entre clases):** cada cierre plantea la limitación que abre la siguiente.

### Cadena de puentes (la historia completa, 15 clases)
```
L1 calculo el mid, pero duplico variables por activo
 → L2 funciones sobre un libro… que TODAS reciben `book`
  → L3 mis funciones crecen: las meto en un módulo .py y lo importo… pero datos y funciones siguen sueltos
   → L4 juntar datos + funciones = un objeto: nacen Order y Fill
    → L5 Orders sueltas: necesito un libro que las contenga y llevar la cuenta (composición)
     → L6 tendré muchas estrategias que comparten esqueleto: herencia y polimorfismo (Strategy de juguete)
      → L7 ya leo el libro real: ¿qué señal esconde? (imbalance)
       → L8 ¿y si MANDO una orden contra el libro? (matching, slippage)
        → L9 cruzar en un instante vs a lo largo del tiempo (el loop, PnL)
         → L10 mi estrategia es un if suelto: hazla modular (Strategy real, reusando la herencia de L6)
          → L11 ¿bate al benchmark o tuve suerte? (slippage vs arrival mid)
           → L12 ejecutar una orden GRANDE sin mover el mercado (VWAP: baselines + dinámico)
            → L13 y si en vez de ejecutar, COTIZO (market making, inventario)
             → L14 mi skew es heurístico: el óptimo (Avellaneda-Stoikov: modelo + simulación) + escribe TU estrategia
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
│   ├── exchange/                   # paquete acumulado (starter)        [L4+]
│   ├── NN_build_exercises.ipynb    # núcleo: refleja el deck, llega al clímax
│   ├── NN_auxiliary.ipynb          # drills + internals + puente
│   └── <script>.py                 # .py consolidado 1:1 con el núcleo
└── data/
```

**Producción:** el contenido vive en specs (`framework/_build/lessons_*.py` + `lessons_docs.py`);
`build_course.py` **autovalida cada ejercicio** y emite. Los decks y guiones a medida viven en
`framework/_build/custom/NN.html` y `NN_guion.md` (el generador los copia, no se sobreescriben).
**Las 15 llevan deck interactivo a medida nivel L1** (full bespoke). Robustez: las diapositivas
explicativas funcionan aunque Pyodide falle (aula sin wifi).

Diseño compartido: `#09090b` / `#22d3ee` / bids `#4ade80` / asks `#f87171`, Inter + JetBrains
Mono, GSAP.

---

## 5. Blueprint de las 15 clases

Ficha: **Reto · Hilo héroe · Pieza · Simuladores · Núcleo · Auxiliares · `.py` · Puente.**

### BLOQUE A — Fundamentos de código (L1–L6): 3 Python + 3 OOP

#### L1 · Python I — De texto a máquina + modelo de datos  *(✅ producida, flagship)*
- **Reto:** quiero el `mid`; la máquina solo entiende 1s y 0s. · **Hilo:** `mid = (bid+ask)/2`.
- **Núcleo:** variables · spread/mid (tipos) · lista+indexing · for/acumulador · dict crear+acceder · if/elif · primer algoritmo.
- **`.py`:** `trading_snapshot.py`. · **Puente:** añadir ETH duplica variables → funciones (L2).

#### L2 · Python II — El libro funcional  *(✅ producida, flagship)*
- **Reto:** mi script no escala a ETH. · **Hilo:** el `book` y las funciones que lo manosean.
- **Núcleo:** make_order · add_order · cancel_order · best_bid/ask · imbalance · spread/mid (componer) · construye y lee el libro.
- **`.py`:** `order_book.py`. · **Puente:** todas las funciones reciben `book` → módulo y luego objeto.

#### L3 · Python III — Módulos: tu código se vuelve librería  *(🆕 nueva — cierra el agujero de `import`)*
- **Reto:** tus funciones del libro están sueltas en un notebook; ¿cómo las reutilizas en otro archivo sin copiar?
- **Hilo:** el módulo `order_book.py` que ya tienes, ahora **importable**.
- **Pieza:** (pre-paquete) tu primer módulo + manejo de errores. Sienta la estructura del paquete `exchange/`.
- **Simuladores:** "dos archivos" (módulo + script que lo importa) · `import` en vivo · `try/except` (best_bid sobre libro vacío) · qué es `if __name__ == "__main__"`.
- **Núcleo:** `import order_book` · `from order_book import imbalance` · usar varias funciones del módulo · `try/except` sobre una función · `__name__ == "__main__"` · (clímax) un `main.py` que importa el módulo, arma un libro y lo lee.
- **Auxiliares:** un paquete con `__init__.py` · lanzar un error propio (`raise`) · `import` con alias.
- **`.py`:** `order_book.py` (módulo) + `main.py` (lo importa). · **Puente:** el código ya es una librería, pero datos y funciones siguen separados → juntarlos = objetos (L4).

#### L4 · OOP I — Clases: Order y Fill  *(era L3; primer módulo del paquete)*
- **Reto:** datos y funciones van siempre juntos; ¿y si el dato supiera operar consigo mismo?
- **Hilo:** el objeto `Order` (y `Fill`). · **Pieza:** `exchange/orders.py`, `exchange/trades.py`.
- **Simuladores:** morph dict→clase · `Order` interactivo (campos → `notional`/`__repr__`) · signo del `cash_flow`.
- **Núcleo:** clase Order + `__init__`/`self` · método `notional` · `__repr__` · clase Fill · `cash_flow` · usarlas juntas.
- **Auxiliares:** validar side · `Order`/`Side` real del paquete · Enum.
- **`.py`:** `orders_demo.py`. · **Puente:** una orden suelta; falta quién la contiene y lleva la cuenta.

#### L5 · OOP II — Composición y encapsulación: OrderBook y PositionTracker  *(era L4)*
- **Reto:** tengo Orders sueltas; necesito un libro que las contenga y algo que lleve caja/posición.
- **Hilo:** composición — `OrderBook` contiene niveles; `PositionTracker` consume `Fill`.
- **Pieza:** `exchange/book.py`, `exchange/portfolio.py`.
- **Simuladores:** "objeto que contiene objetos" · libro vivo con métricas como métodos · PositionTracker comiendo Fills → equity.
- **Núcleo:** OrderBook init · best_bid/ask/spread/mid · imbalance · estado privado `_cash`/`_position` · apply_fill · equity.
- **Auxiliares:** microprice · depth · `@property`.
- **`.py`:** `book_demo.py`. · **Puente:** tendré muchas estrategias parecidas; ¿cómo no repetir código?

#### L6 · OOP III — Herencia, polimorfismo y ABC  *(🆕 nueva — cierra el agujero del framework)*
- **Reto:** vas a tener muchas estrategias que comparten esqueleto; ¿cómo evitas reescribirlo cada vez?
- **Hilo:** una familia `Strategy` **de juguete** (base + subclases) — la semilla del framework real de L10.
- **Pieza:** un `Strategy` base de juguete (aún fuera del paquete; en L10 se formaliza).
- **Simuladores:** herencia visual (base→hijas: heredan y sobrescriben) · `@abstractmethod` (no puedes instanciar la base incompleta) · **polimorfismo** (un bucle llama `.decide(book)` sobre una lista de estrategias distintas y cada una responde a su manera) · `super()`.
- **Núcleo:** clase base con método · subclase que hereda · override de un método · `@abstractmethod` (ABC) · polimorfismo (lista de objetos distintos, mismo método) · (clímax) 2-3 estrategias toy que deciden distinto bajo la misma interfaz.
- **Auxiliares:** `super().__init__` · `isinstance` · por qué la ABC evita instanciar incompleto.
- **`.py`:** `strategies_toy.py` (base + subclases + bucle polimórfico). · **Puente:** tienes el patrón estrategia; en L10 lo conectas al motor real.

### BLOQUE B — El motor (L7–L9)

#### L7 · Microestructura — Leer el libro  *(era L5, flagship)*
- **Reto:** 500 snapshots reales de BTC: ¿hacia dónde empuja? · **Hilo:** el imbalance (y microprice).
- **Pieza:** métricas en `book.py` + `Market.sample`.
- **Núcleo:** Market.sample/step · spread/mid · imbalance(levels) · microprice · depth.
- **Puente:** sé leer el libro; ¿qué pasa cuando MANDO una orden contra él?

#### L8 · Órdenes y matching  *(era L6, flagship)*
- **Reto:** market grande: ¿a qué precio se llena? · **Hilo:** una market barriendo niveles (fills + precio efectivo).
- **Pieza:** `exchange/matching.py`.
- **Núcleo:** market fill · limit + remanente · IOC · FOK · precio efectivo.
- **Puente:** cruzo en un instante; ¿y a lo largo del tiempo?

#### L9 · El loop de simulación  *(era L7)*
- **Reto:** reproducir el día y llevar el PnL. · **Hilo:** la curva de equity.
- **Pieza:** `exchange/market.py` (loop).
- **Núcleo:** loop step · submit · acumular posición · equity final.
- **Puente:** mi estrategia es un `if` suelto; ¿cómo la hago modular?

### BLOQUE C — El framework de estrategias (L10–L11)

#### L10 · Strategy + Backtest  *(era L8, flagship, pico arquitectónico)*
- **Reto:** cambiar de estrategia sin reescribir el motor. · **Hilo:** el contrato `Strategy` (polimorfismo — el que ya practicaron en L6).
- **Pieza:** `exchange/strategy.py`, `exchange/backtest.py`.
- **Núcleo:** subclase BuyOnce · Backtest.run · on_fill · SellOnce (polimorfismo).
- **Puente:** tengo el enchufe; ¿una estrategia con señal de verdad y cómo la mido?

#### L11 · Primera estrategia + métricas  *(era L9)*
- **Reto:** ¿bate al benchmark o tuve suerte? · **Hilo:** el slippage vs el mid de llegada.
- **Núcleo:** ImbalanceStrategy · medir · arrival mid · inventario como riesgo.
- **Puente:** ejecuté a lo bruto; ¿cómo ejecuto una orden GRANDE sin mover el mercado?

### BLOQUE D — Ejecución y market making (L12–L14)

#### L12 · VWAP — Ejecución (baselines + dinámico)  *(fusión de los antiguos L10+L11, flagship)*
- **Reto:** vender 10 BTC sin hundir el precio. · **Hilo:** el schedule de participación.
- **Pieza:** `exchange/strategies/vwap.py`.
- **Simuladores:** trocear orden grande · perfil de volumen · TWAP vs VWAP · predicción dinámica (ventana rolada) · estático vs dinámico.
- **Núcleo:** pesos TWAP · VWAPStrategy run · perfil a medida · precio medio · rolling prediction · perfil dinámico/corrección.
- **Auxiliares:** regresión a mano (puente ML) · cap de participación.
- **`.py`:** `run_vwap.py`. · **Puente:** he sido el que EJECUTA; ¿y si COTIZO?

#### L13 · Market making — Intro  *(era L12, flagship)*
- **Reto:** ganar el spread sin que el inventario me hunda. · **Hilo:** el inventario (y el skew).
- **Pieza:** `exchange/strategies/market_maker.py`, `exchange/simulation.py`.
- **Núcleo:** quotes · skew · reservation price · simular el MM.
- **Puente:** mi skew es heurístico; ¿el óptimo?

#### L14 · Avellaneda-Stoikov — modelo + simulación  *(fusión de los antiguos L13+L14, flagship)*
- **Reto:** cuánto inclino/separo, óptimo, y qué gamma elijo. · **Hilo:** reservation price + la senda de inventario.
- **Pieza:** `AvellanedaStoikov` + barridos sobre `MMSimulation`.
- **Simuladores:** reservation/optimal spread (sliders) · A-S vs naive · simulación completa · barrido de gamma · **escribe tu estrategia**.
- **Núcleo:** reservation price · optimal spread · A-S quotes · simular · gamma vs inventario · subclase propia.
- **Auxiliares:** decaimiento temporal · sensibilidad de parámetros.
- **`.py`:** `mm_sweep.py`. · **Puente:** motor entero + tu estrategia → examen.

### BLOQUE E — Cierre

#### L15 · Examen final
Test de 40 min, 40 preguntas (A/B/C), +1 acierto / −0.5 fallo. Cubre todo el arco, incluido
código del propio framework. Generador en `15-final-exam/generate_exam.py`.

---

## 6. Estándar de calidad y proceso de producción

- **Calidad:** las 15 con deck a medida nivel L1. Notebook + auxiliares + `.py` + mini-test en todas.
- **Autovalidación:** ningún ejercicio se publica sin pasar `build_course.py --check-only`.
- **Estado:** L1 y L2 **producidas a nivel flagship**. L3–L15 pendientes.
- **Proceso:**
  1. Este plan (6 fundamentos, 15 clases) aprobado.
  2. **Migración de numeración**: el motor/framework/VWAP/MM se desplazan (ver §5). Las carpetas y
     los specs del generador se renumeran al producir cada clase (L1/L2 no cambian).
  3. **Siguiente a producir: L3 (Python III — Módulos)**, la primera clase nueva, que convierte el
     `order_book.py` de L2 en un módulo importable.
  4. Después, L4–L6 (OOP) y el resto en orden, comprimiendo VWAP (L12) y A-S (L14) según §5.
- **Anexo:** bonos y RFQ en `annex-bonds-rfq/` (opcional, fuera del arco).

---

## 7. Riesgos y mitigación

- *Decks carísimos × 15* → reutilizar el andamiaje de L1/L2 (Pyodide, estilos, simuladores) como
  librería de componentes.
- *6 fundamentos retrasan el trading* → se compensa cerrando dos agujeros reales (módulos/`import`
  en L3, herencia/polimorfismo en L6) que antes explotaban más tarde; y comprimiendo VWAP y A-S,
  ya marcados como "calibrables".
- *Romper la continuidad* → la cadena de puentes (§3) y el paquete acumulado son el control.
- *Sobre-ingeniería* → código simple para iniciados; el generador autovalida; firmas cerradas en
  `framework/exchange/`.
- *Pyodide en aula sin wifi* → las diapositivas explicativas funcionan sin Python.
