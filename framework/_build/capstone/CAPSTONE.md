# 🏁 Capstone — Tu propio market maker

Has construido el motor entero: libro, matching, mercado, framework `Strategy`,
VWAP y market making con Avellaneda-Stoikov. **Ahora te toca a ti.**

El capstone es abierto: diseña un market maker que capture el spread **sin
acabar cargado de inventario**. Es exactamente el dilema real de un MM.

## Qué entregas

Un único archivo: **`exercises/mi_estrategia.py`**, con una clase `MiEstrategia`
que herede de `MarketMaker` o de `AvellanedaStoikov`. Nada más. Todo lo que
necesitas ya está en el paquete `exchange/` que tú mismo construiste.

## Cómo te corriges

```bash
cd exercises
python capstone_check.py
```

Ejecuta tu estrategia en **3 semillas reproducibles de práctica** (2026, 7, 314),
500 pasos cada una y una intensidad por horizonte pública `A=630`, y te da una
puntuación formativa desglosada más un **código
de resultado** copiable (`AT26-CAP-N…`). Es una huella para detectar errores de
copia, no una firma ni una acreditación.

> Esta puntuación **no es una nota oficial y no se agrega a los pesos
> 10/20/40/30 del contrato pedagógico**. Un uso evaluable exigiría una decisión
> docente explícita y reejecución controlada del archivo, nunca el código público.

## El baremo (público — optimiza contra él sin sorpresas)

Se promedian dos números sobre las 3 semillas:

- **`pnl`** — PnL final marcado a mercado. Más = mejor.
- **`inv`** — inventario máximo `|q|` alcanzado. Menos = mejor (es tu riesgo).

Puntuación formativa sobre 100, **rúbrica interna 30 / 40 / 30**:

| Componente | Peso | Fórmula | Satura en |
|---|---|---|---|
| **PnL** | 30 | `30 · min(pnl / 2.5, 1)` | pnl ≥ 2.5 |
| **Riesgo-ajustado** | 40 | `40 · min(ra / 1.4, 1)`, con `ra = pnl / (1 + 10·inv)` | ra ≥ 1.4 |
| **Control de inventario** | 30 | `30 · max(1 − inv / 0.30, 0)` | inv = 0 |

El corazón es la componente **riesgo-ajustada** (40 pts): ganar mucho cargándote
de inventario no vale — un movimiento del mid en tu contra te lo come. El baremo
premia el PnL **por unidad de riesgo**, que es de lo que va el market making.

Las referencias (`2.5`, `1.4`, `0.30`) son públicas y están en
`capstone_scoring.py`. No las toques: son el contrato de esta práctica.

## Ideas (todas del curso, todas legales)

- Ajusta `half_spread`: más ancho = más margen por vuelta, pero menos fills.
- Ajusta `inventory_skew`: más skew = vuelves a plano antes = menos riesgo.
- Parte de `AvellanedaStoikov` y ajusta `gamma` o tu lógica de inventario.
  `sigma` y `kappa` describen el entorno y deben coincidir con el simulador.
- Sobrescribe `quotes()` o `reservation_price()` con tu propia lógica.

La plantilla inicial está incompleta a propósito y **no obtiene puntuación**. Primero
debes implementar una decisión de inventario propia; una sonda pública comprueba
que, con inventario largo, bajas el centro de cotización y, con inventario corto,
lo subes. Una estrategia que siempre devuelve el mid no es elegible. Después
podrás compararla con los baselines públicos del curso.

## Reglas

- Solo se toca `mi_estrategia.py`. `capstone_check.py` y `capstone_scoring.py`
  son el contrato de la puntuación formativa: no se editan.
- Nada de mirar el futuro ni de hardcodear precios: tu estrategia solo ve el
  libro que le pasa el simulador, como cualquier `Strategy` del curso.
- El código es un autoinforme consistente, no una prueba de procedencia. Si el
  docente decide revisarlo, debe reejecutar `mi_estrategia.py`.
