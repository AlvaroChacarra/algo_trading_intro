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

Ejecuta tu estrategia en **3 semillas oficiales** (2026, 7, 314), 500 pasos cada
una, y te da la nota desglosada más un **código de resultado** copiable
(`AT26-CAP-N…`) que envías al profe o al leaderboard.

## El baremo (público — optimiza contra él sin sorpresas)

Se promedian dos números sobre las 3 semillas:

- **`pnl`** — PnL final marcado a mercado. Más = mejor.
- **`inv`** — inventario máximo `|q|` alcanzado. Menos = mejor (es tu riesgo).

Nota sobre 100, **rúbrica 30 / 40 / 30**:

| Componente | Peso | Fórmula | Satura en |
|---|---|---|---|
| **PnL** | 30 | `30 · min(pnl / 2.5, 1)` | pnl ≥ 2.5 |
| **Riesgo-ajustado** | 40 | `40 · min(ra / 1.4, 1)`, con `ra = pnl / (1 + 10·inv)` | ra ≥ 1.4 |
| **Control de inventario** | 30 | `30 · max(1 − inv / 0.30, 0)` | inv = 0 |

El corazón es la componente **riesgo-ajustada** (40 pts): ganar mucho cargándote
de inventario no vale — un movimiento del mid en tu contra te lo come. El baremo
premia el PnL **por unidad de riesgo**, que es de lo que va el market making.

Las referencias (`2.5`, `1.4`, `0.30`) son públicas y están en
`capstone_scoring.py`. No las toques: son el contrato de la nota.

## Ideas (todas del curso, todas legales)

- Ajusta `half_spread`: más ancho = más margen por vuelta, pero menos fills.
- Ajusta `inventory_skew`: más skew = vuelves a plano antes = menos riesgo.
- Parte de `AvellanedaStoikov` y tunéa `gamma` / `sigma` / `kappa`.
- Sobrescribe `quotes()` o `reservation_price()` con tu propia lógica.

Un market maker naive bien ajustado ya roza los 90 puntos. ¿Puedes con él?

## Reglas

- Solo se toca `mi_estrategia.py`. `capstone_check.py` y `capstone_scoring.py`
  son el contrato de la nota: no se editan.
- Nada de mirar el futuro ni de hardcodear precios: tu estrategia solo ve el
  libro que le pasa el simulador, como cualquier `Strategy` del curso.
- El profe puede reejecutar tu `mi_estrategia.py`: el código de resultado tiene
  que cuadrar con lo que produce tu archivo.
