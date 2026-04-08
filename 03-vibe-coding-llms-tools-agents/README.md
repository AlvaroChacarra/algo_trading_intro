# Clase 3 — Vibe Coding: LLMs, Tools y Agentes

## Objetivo
Entender como trabaja un LLM, que diferencia hay entre un LLM y un agente, y aprender a evaluar codigo generado por IA usando patrones de Python que el alumno no conocia hasta ahora.

## Pregunta central
"Escribiste ~60 lineas de clases a mano. ¿Y si un LLM las genera a partir de una descripcion en espanol?"

## Estructura de la sesion

| Fase | Duracion | Contenido |
|---|---|---|
| Presentacion | 20 min | Token generation, LLM vs Agente, confianza |
| Notebook | 15 min | Evaluar codigo IA, try/except, type hints, @property, comprehensions |
| Ejercicios | Restante + casa | 10 ejercicios en 3 tiers |

## Conceptos nuevos de Python
- `try / except` — capturar errores sin crashear
- Type hints — `def f(x: int) -> str`
- `@property` — acceso controlado a estado interno
- List comprehensions — `[x for x in items if cond]`
- Decoradores — el patron detras de `@property`

## Referencia rapida

```python
# try/except
try:
    result = price / size
except ZeroDivisionError:
    result = 0.0

# type hints
def notional(price: float, size: float) -> float:
    return price * size

# @property
class Tracker:
    def __init__(self):
        self._cash = 0.0

    @property
    def cash(self) -> float:
        return self._cash

# list comprehension
buys = [t for t in trades if t.side == "buy"]

# decorator pattern
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

## Continuidad
- **Desde L2:** Order, Trade, PositionTracker → el codigo que la IA "regenera"
- **Hacia L4:** Python + OOP + IA → listos para datos reales de mercado (BTC microestructura)
