# Introducción al Algo Trading con Python — ICAI 2026

Curso de 15 clases. **Toda la asignatura es un solo proyecto**: clase a clase construyes `exchange`, un motor de microestructura de mercado y un framework de estrategias, y sobre él enchufas un VWAP y un market maker. Acabas escribiendo tu propia estrategia.

Instructor: **Álvaro López Chacarra** · ICAI.

## Empieza aquí

Abre **[la web del curso](https://alvarochacarra.github.io/algo_trading_intro/)** desde cualquier dispositivo. Los documentos interactivos se consultan directamente y cada notebook tiene una versión web renderizada; el progreso se guarda en el propio navegador.

## Mapa del curso

| Bloque | Clases | Qué construyes | Pieza de `exchange` |
|--------|--------|----------------|---------------------|
| **Fundamentos** | 1–3 | Python: modelo de datos, funciones sobre el libro, módulos | `order_book.py` |
| **POO** | 4–6 | Clases: `Order`/`Fill`, `OrderBook`/`PositionTracker`, herencia y la familia `Strategy` | `orders`, `book`, `portfolio` |
| **El motor** | 7–9 | Leer el libro (imbalance, microprice, depth), matching de órdenes, loop de simulación | `matching`, `market` |
| **El framework** | 10–11 | `Strategy` + `Backtest` enchufables; métricas honestas de una estrategia | `strategy`, `backtest` |
| **Ejecución** | 12 | VWAP: trocear siguiendo el perfil de volumen | `strategies/vwap` |
| **Market making** | 13–14 | Cotizar e inventario; Avellaneda-Stoikov + **tu capstone** | `strategies/market_maker`, `simulation` |
| **Cierre** | 15 | Examen final (40 preguntas) | — |

A mitad de camino, tras la clase 6, hay un **[checkpoint](06-oop-iii-inheritance/checkpoint.html)** (20 preguntas de L1-L6) para comprobar la base antes de tocar el motor. El curso se corona con el **[capstone](14-avellaneda-stoikov/CAPSTONE.md)**: tu propio market maker, con baremo público y leaderboard.

## Cada clase

1. **Documento interactivo** (`presentation/*-doc.html`) — la teoría como página que se recorre con scroll: scrollytelling, simuladores con datos reales del motor, y un quiz de diagnóstico. Autocontenido y sin internet.
2. **Construcción** (`exercises/NN_build_exercises.ipynb`) — montas la pieza del día con validadores automáticos. Cada ejercicio marca su nivel: 🟢 núcleo · 🔵 si vamos bien · 🟣 bonus.
3. **El gimnasio** (`exercises/NN_auxiliary.ipynb`) — drills cortos de primitivas de Python con datos de mercado, un calentamiento que recicla la clase anterior y un ejercicio de transferencia que lleva la idea a otro dominio.

El paquete que vienes construyendo viaja contigo en `exercises/exchange/` (a partir de la clase 4).

### Corrígete desde la terminal

```bash
python check_my_work.py 4        # cuántos validadores pasan en la clase 4
python check_my_work.py 4 --aux  # el gimnasio
python check_my_work.py all      # todo el curso de un vistazo
```

## Instalación

```bash
git clone <repo> && cd algo_trading_intro
python -m venv .venv
# macOS/Linux:  source .venv/bin/activate
# Windows:      .\.venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

El núcleo de `exchange` es **solo librería estándar** — el motor y todos los validadores corren sin dependencias externas. Jupyter es lo único que necesitas para los cuadernos; `requirements-dev.txt` añade `pytest` y `playwright` para las herramientas del profesor.

## Estructura del repositorio

```
index.html                 mapa del curso (progreso local)
NN-.../                     una carpeta por clase
  presentation/            documento interactivo + guion del profe
  exercises/               notebooks + el paquete exchange/ acumulado
data/                      dataset de snapshots del libro (ver data/README.md)
framework/                 implementación de referencia y generador del curso
15-final-exam/             examen, checkpoint y banco de preguntas
annex-bonds-rfq/           material opcional (bonos y RFQ), fuera del arco principal
```

## Para el profesor

Todo el material se **genera** desde specs en `framework/_build/` — no se editan los notebooks ni los docs a mano. Ver **[`CLAUDE.md`](CLAUDE.md)** (cómo funciona el generador y cómo tocar el curso) y **[`PLAN_MAESTRO_CURSO_TRADING_2026.md`](PLAN_MAESTRO_CURSO_TRADING_2026.md)** (diseño pedagógico). Añade `?profe=1` a la URL de cualquier documento para abrir el cajón con el guion.
