# Plan maestro — Curso de Trading Algorítmico 2026

## 1. Visión

Curso de 15 clases de 40 minutos. **Toda la asignatura es un solo proyecto que crece clase a clase**: el alumno construye un paquete Python, `exchange/`, que es un **motor de microestructura de mercado** y un **framework de estrategias modulares**, y sobre él enchufa un **VWAP**, un **market maker** (Avellaneda-Stoikov) y, al final, su propia estrategia.

La gracia: aprende Python y algo trading **a la vez, construyendo**. Cada clase añade una pieza que habla con las anteriores (Order → Book → Matching → Market → Strategy → Backtest), así que el alumno *ve cómo los objetos se entrelazan*.

Tono: directo, sin paja, intuición antes que formalismo, ejemplos de mercado siempre (BTCUSDT), código **simple** (los alumnos son iniciados — nada de abstracciones innecesarias).

## 2. La columna vertebral: `exchange/`

Implementación de referencia en `framework/exchange/` (fuente de verdad, con `smoke_test.py`). Cada clase entrega un **snapshot acumulado** del paquete en `NN-slug/exercises/exchange/`: lo construido hasta la clase anterior, listo para añadir la pieza de hoy.

```
exchange/
├── orders.py      Order, Side, OrderType            (L3)
├── trades.py      Fill                               (L3)
├── book.py        OrderBook, Level (+ métricas)      (L4 / L5)
├── portfolio.py   PositionTracker                    (L4)
├── matching.py    MatchingEngine                     (L6)
├── market.py      Market (replay + Market.sample)    (L7)
├── strategy.py    Strategy (ABC) + NewOrder/Cancel   (L8)
├── backtest.py    Backtest + BacktestResult          (L8)
├── simulation.py  MMSimulation (intensidad de fills) (L14)
└── strategies/    VWAPStrategy, MarketMaker, AvellanedaStoikov (L10-L14)
```

**El contrato que lo hace modular** (clase 8, el corazón del curso):

```python
class Strategy(ABC):
    @abstractmethod
    def on_book_update(self, book) -> list[Action]: ...   # NewOrder | Cancel
    def on_fill(self, fill): ...
```

El mismo `Backtest(market, strategy).run()` corre con cualquier estrategia. Cambiar de VWAP a market maker es una línea. `Market.sample()` da 500 snapshots reales de BTCUSDT sin configurar rutas.

## 3. Syllabus (15 clases, un arco)

**Fundamentos — el modelo de datos**
1. **Python I** — vars, tipos, listas, dicts, for, if, funciones → order/snapshot como dicts.
2. **Python II** — funciones que construyen y modifican un libro → add/cancel/imbalance. *Surge el dolor que pide OOP.*
3. **OOP I** — clase, métodos, `__repr__`, encapsulación → `Order`, `Fill`.
4. **OOP II** — composición y estado privado → `OrderBook` (contiene niveles) + `PositionTracker`.

**El motor de microestructura**
5. **Leer el libro** — spread, mid, imbalance, microprice, depth sobre snapshots reales.
6. **Órdenes y matching** — `MatchingEngine`: market/limit/IOC/FOK, fills parciales.
7. **El loop de simulación** — `Market`: reproducir snapshots, ejecutar en el tiempo, llevar la cuenta.

**El framework de estrategias**
8. **Strategy + Backtest** — interfaz abstracta + runner. Polimorfismo (pico arquitectónico).
9. **Primera estrategia + métricas** — señal de imbalance, PnL/slippage vs benchmark. Checkpoint integrador.

**VWAP** (profundidad calibrable)
10. **VWAP I** — perfil de volumen, TWAP vs VWAP → `VWAPStrategy`.
11. **VWAP II** — predicción dinámica de volumen, factor de corrección. *(extensión ML opcional aquí).*

**Market making** (profundidad calibrable)
12. **MM intro** — cotizar a dos lados, inventario, adverse selection, skew → `MarketMaker`.
13. **Avellaneda-Stoikov I** — reservation price, optimal spread (fórmulas, intuición).
14. **Avellaneda-Stoikov II** — `MMSimulation`, control de inventario, barridos de γ.

**Cierre**
15. **Examen final** — test de 40 min, 40 preguntas (A/B/C), +1 acierto / −0.5 fallo. Cubre todo el curso, incluido código del propio framework.

## 4. Estructura por lección

```
NN-slug/
├── README.md                       # objetivo + qué pieza se añade
├── CLAUDE.md                       # guía de implementación
├── presentation/<slug>-interactive.html + guion.md
├── exercises/
│   ├── exchange/                   # paquete acumulado (starter)  [L3+]
│   ├── NN_build_exercises.ipynb    # construir la pieza
│   └── NN_auxiliary.ipynb          # profundización opcional
└── data/
```

**Patrón por ejercicio:** enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida. **Tiers:** Núcleo (1-3, en clase), Si vamos bien (resto), Auxiliares (cuaderno aparte).

**Presentación HTML:** 3 bloques (~5-7 min) + hero + cierre. Diseño compartido: fondo `#09090b`, acento `#22d3ee`, bids `#4ade80`, asks `#f87171`, Inter + JetBrains Mono, GSAP.

## 5. El contenido vive en el generador

Para mantener consistencia, las lecciones L1-L14 se generan desde specs:

```
framework/_build/
├── lessons_foundations.py / lessons_engine.py / lessons_strategies.py   # specs
├── nbgen.py            # builders notebook + HTML
└── build_course.py     # autovalida y emite
```

`python framework/_build/build_course.py --check-only` ejecuta solución+validador de **cada** ejercicio (garantiza que todo el código del curso corre). Sin `--check-only`, regenera las carpetas. **Para editar una lección, edita su spec y regenera** — no edites a mano los notebooks generados.

## 6. Datos

- Snapshots BTCUSDT sintéticos reproducibles (`seed=42`), empaquetados en `exchange/_data/` y disponibles vía `Market.sample()`. Copia compartida en `data/`.
- Cero llamadas a APIs externas. El core de `exchange` es solo stdlib.

## 7. Decisiones tomadas

- Vibe coding eliminado como clase (las horas se dedican a construir).
- Bonos y RFQ fuera del arco principal → `annex-bonds-rfq/` (material opcional).
- Pipeline ML (antigua L6-L7) conservado como extensión/auxiliar, no como bloque principal.
- Un solo examen (L15). Continuidad por starter acumulativo.
- Código simple para iniciados; foundations sin imports de terceros.

## 8. Riesgos y mitigación

- *Meter demasiado por clase* → una pieza del motor por sesión.
- *Técnico demasiado pronto* → intuición primero, fórmula después (A-S sin derivar la HJB).
- *Romper la continuidad* → el paquete acumulado y el contrato `Strategy` son el hilo.
- *Sobre-ingeniería* → el generador autovalida; las firmas se cierran en `framework/exchange/` antes de tocar lecciones.
