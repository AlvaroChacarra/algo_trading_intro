# Introducción al Algo Trading con Python — ICAI 2026

Curso de 15 clases. **Toda la asignatura es un solo proyecto**: clase a clase construyes `exchange`, un motor de microestructura de mercado y un framework de estrategias, y sobre él enchufas un VWAP y un market maker. Acabas escribiendo tu propia estrategia.

Instructor: **Álvaro López Chacarra** · ICAI.

## Mapa del curso

| Bloque | Clases | Qué construyes |
|--------|--------|----------------|
| Fundamentos | 1–4 | Python y OOP → el modelo de datos (`Order`, `OrderBook`, `PositionTracker`) |
| Motor | 5–7 | Métricas del libro, matching de órdenes, loop de simulación |
| Framework | 8–9 | `Strategy` + `Backtest`: estrategias enchufables |
| VWAP | 10–11 | Ejecución por perfil de volumen |
| Market making | 12–14 | Cotizar, inventario y Avellaneda-Stoikov |
| Examen | 15 | Test final |

`annex-bonds-rfq/` contiene material opcional (bonos y RFQ) fuera del arco principal.

## Cada clase

1. **Presentación** (`presentation/*.html`) — la intuición y qué pieza añadimos hoy.
2. **Construcción** (`exercises/NN_build_exercises.ipynb`) — montas la pieza con validadores automáticos.
3. **Auxiliares** (`exercises/NN_auxiliary.ipynb`) — profundización opcional.

El paquete que vienes construyendo viaja contigo en `exercises/exchange/` (a partir de la clase 3).

## Instalación

```bash
git clone <repo> && cd algo_trading_intro
python -m venv .venv
# macOS/Linux:  source .venv/bin/activate
# Windows:      .\.venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

El núcleo de `exchange` es **solo librería estándar** — los notebooks corren sin dependencias externas (pandas/matplotlib solo para visualización opcional).

## Para el profesor

La implementación de referencia y las herramientas de generación están en `framework/`. Ver `CLAUDE.md` y `PLAN_MAESTRO_CURSO_TRADING_2026.md`.
