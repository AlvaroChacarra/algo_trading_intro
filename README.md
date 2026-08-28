# Introducción al Algo Trading con Python — ICAI 2026

Curso de 15 clases. **Toda la asignatura es un solo proyecto**: clase a clase construyes `exchange`, un motor de microestructura de mercado y un framework de estrategias, y sobre él enchufas un VWAP y un market maker. Acabas escribiendo tu propia estrategia.

Instructor: **Álvaro López Chacarra** · ICAI.

## Empieza aquí

Abre **[la web del curso](https://alvarochacarra.github.io/algo_trading_intro/)** desde cualquier dispositivo. Los documentos interactivos se consultan directamente; cada notebook tiene una versión web renderizada y un botón **Ejecutar** para probarlo en JupyterLite sin instalar Python.

## Mapa del curso

| Bloque | Clases | Qué construyes | Pieza de `exchange` |
|--------|--------|----------------|---------------------|
| **FOUNDATIONS** | 1–6 | De dato, cálculo y decisión a objetos compuestos y una familia de estrategias | `orders`, `trades`, `book`, `portfolio` |
| **ENGINE** | 7–10 | Leer el libro, ejecutar órdenes, coordinar el mercado y enchufar estrategias | `matching`, `market`, `strategy`, `backtest` |
| **STRATEGIES** | 11–14 | Medir con honestidad, ejecutar con VWAP y controlar inventario al hacer mercado | `strategies/vwap`, `strategies/market_maker`, `simulation` |
| **ASSESSMENT** | 15 | Integración final de Python, motor, ejecución y market making | — |

A mitad de camino, tras la clase 6, hay un **[checkpoint](06-oop-iii-inheritance/checkpoint.html)** (20 preguntas de L1-L6) para comprobar la base antes de tocar el motor. El curso se corona con el **[capstone](14-avellaneda-stoikov/CAPSTONE.md)**: tu propio market maker, con baremo público y leaderboard.

## Cada clase

1. **Documento interactivo** (`presentation/*-doc.html`) — una fuente con dos recorridos en L1–L14: `?mode=aula` usa escenas y teclado sin scroll del body; `?mode=estudio` ofrece LIVE + REQUIRED y permite abrir OPTIONAL de forma explícita. En móvil se usa el fallback vertical.
2. **Construcción** (`exercises/NN_build_exercises.ipynb`) — montas la pieza del día con validadores automáticos. Cada ejercicio está decidido como 🟢 LIVE, 🔵 REQUIRED o 🟣 OPTIONAL en `pedagogy/exercise_routes.yml`.
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
pedagogy/                 grafo, superficies de API, rutas, carga y blueprint
framework/                 implementación de referencia y generador del curso
15-final-exam/             examen, checkpoint y banco de preguntas
annex-bonds-rfq/           material opcional (bonos y RFQ), fuera del arco principal
```

## Para el profesor

Todo el material se **genera** desde specs en `framework/_build/` — no se editan los notebooks ni los docs a mano. La gobernanza vive en [`AGENTS.md`](AGENTS.md), el contrato ejecutable en `pedagogy/` y la guía para mantener el runtime en [`docs/learning-runtime-authoring.md`](docs/learning-runtime-authoring.md). Añade `?profe=1` a la URL de cualquier documento para abrir el cajón con el guion.
