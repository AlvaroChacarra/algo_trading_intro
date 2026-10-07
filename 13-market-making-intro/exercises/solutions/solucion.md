# L13 · Solución de consulta

Copia el bloque del archivo que quieras completar en su archivo local. Conserva research_support.py y las bases incluidas. Cada encargo aparece inmediatamente antes del código que lo resuelve.

| Apartado | Archivo / símbolo |
| --- | --- |
| 1A | maker.py:fixed_quotes |
| 1B | main.py:practice |
| 1C | main.py:practice |
| 1D | main.py:practice |
| 2A | maker.py:StudentMarketMaker.reservation_price |
| 2B | main.py:practice |
| 2C | main.py:practice |
| 2D | main.py:practice |
| 2E | main.py:practice |
| 3A | main.py:practice |
| 3B | main.py:practice |
| 4A | main.py:practice |
| 4B | main.py:cara_utility |
| 4C | main.py:practice |
| 5A | opcionales.py:practice |
| 5B | opcionales.py:practice |
| 5C | opcionales.py:practice |

## `maker.py`

```python
"""Dos quotes y una clase de market making: precios, no fills."""
from research_support import MakerBase


def fixed_quotes(center, half_spread):
    # Ejercicio 1A: completa fixed_quotes(center, half_spread): devuelve bid como center menos half_spread y ask como center más half_spread; conserva un ancho total de dos medios spreads.
    return center - half_spread, center + half_spread


class StudentMarketMaker(MakerBase):
    def reservation_price(self, mid, tau):
        # Ejercicio 2A: completa StudentMarketMaker.reservation_price(mid, tau): resta self.skew por self.inventory al mid; conserva tau en la firma aunque el skew fijo no lo utilice.
        return mid - self.skew * self.inventory

    # Proporcionado: conserva ancho y usa el centro del mismo objeto.
    def spread(self, tau):
        return 2 * self.half_spread

    def quotes(self, mid, tau):
        center = self.reservation_price(mid, tau)
        return fixed_quotes(center, self.spread(tau) / 2)
```

## `main.py`

```python
"""L13: ofrece precios, confirma fills y observa inventario."""
import math
from maker import fixed_quotes, StudentMarketMaker
from models import Fill
from portfolio import PositionTracker
from research_support import simulate

STEPS = ('1A', '1B', '1C', '1D', '2A', '2B', '2C', '2D', '2E', '3A', '3B', '4A', '4B', '4C')


def cara_utility(wealth, gamma):
    # Ejercicio 4B: completa cara_utility(wealth, gamma) con -math.exp(-gamma * wealth); compara U(5) y U(10) con gamma=0.1, distinguiendo utilidad de dinero.
    return -math.exp(-gamma * wealth)


def practice(through=None):
    print("Tu puesto: compra a bid, vende a ask; una quote aún no cambia la cuenta.")
    bid, ask = fixed_quotes(100, 0.6)
    # Observación 1A
    print(f'quotes: {bid:.2f} / {ask:.2f}; ancho: {ask-bid:.2f}')
    if through == '1A': return locals()

    # Ejercicio 1B: crea tracker = PositionTracker() y aplica Fill("buy", bid, 0.1) al bid calculado; contabiliza únicamente esta compra confirmada.
    tracker = PositionTracker()
    tracker.apply_fill(Fill('buy', bid, 0.1))
    # Observación 1B
    print(f'compra | caja {tracker.cash:.2f} | q {tracker.position:.1f} | mark 100 | equity {tracker.equity(100):.2f}')
    if through == '1B': return locals()

    # Ejercicio 1C: guarda marked_equity consultando tracker.equity(99), sin aplicar otro fill ni cambiar caja o posición; predice qué columnas cambian.
    marked_equity = tracker.equity(99)
    # Observación 1C
    print(f'mark nuevo | caja {tracker.cash:.2f} | q {tracker.position:.1f} | mark 99 | equity {marked_equity:.2f}')
    if through == '1C': return locals()

    # Ejercicio 1D: aplica Fill("sell", ask, 0.1) a la misma tracker; este ejemplo confirma una venta al ask original, con quotes fijas y sin costes.
    tracker.apply_fill(Fill('sell', ask, 0.1))
    # Observación 1D
    print(f'venta | caja {tracker.cash:.2f} | q {tracker.position:.1f} | mark 100 | equity {tracker.equity(100):.2f}')
    if through == '1D': return locals()

    maker = StudentMarketMaker(half_spread=0.6, skew=2.0, size=0.1)
    maker.inventory = 0.3
    mbid, mask = maker.quotes(100, 1)
    # Observación 2A
    print(f'centro {maker.reservation_price(100, 1):.2f}; quotes {mbid:.2f} / {mask:.2f}')
    if through == '2A': return locals()

    # Ejercicio 2B: consulta flat_quotes con maker.inventory = 0 y long_quotes con maker.inventory = 0.3; compara el centro y el ancho sin modificar half_spread.
    maker.inventory = 0
    flat_quotes = maker.quotes(100, 1)
    maker.inventory = 0.3
    long_quotes = maker.quotes(100, 1)
    # Observación 2B
    print(f'q 0: {flat_quotes[0]:.2f} / {flat_quotes[1]:.2f}; q 0.3: {long_quotes[0]:.2f} / {long_quotes[1]:.2f}')
    print(f'ancho antes {flat_quotes[1]-flat_quotes[0]:.2f}; después {long_quotes[1]-long_quotes[0]:.2f}')
    if through == '2B': return locals()

    # Ejercicio 2C: crea wide_position con half_spread=0.5 y skew=1, fija inventory=2 y guarda variant_quotes para mid=100 y tau=1; anuncia el cambio de parámetros.
    wide_position = StudentMarketMaker(half_spread=0.5, skew=1)
    wide_position.inventory = 2
    variant_quotes = wide_position.quotes(100, 1)
    # Observación 2C
    print('variante q=2:', variant_quotes)
    if through == '2C': return locals()

    # Ejercicio 2D: fija maker.inventory = -0.3 y guarda short_quotes con mid=100 y tau=1; predice hacia dónde se moverán ambas quotes.
    maker.inventory = -0.3
    short_quotes = maker.quotes(100, 1)
    # Observación 2D
    print(f'corto: {short_quotes[0]:.2f} / {short_quotes[1]:.2f}')
    if through == '2D': return locals()

    # Ejercicio 2E: crea partial_tracker, compra 0.1 al bid y vende solo 0.04 al ask; guarda partial_equity a mark 100 y explica qué riesgo queda abierto.
    partial_tracker = PositionTracker()
    partial_tracker.apply_fill(Fill('buy', bid, 0.1))
    partial_tracker.apply_fill(Fill('sell', ask, 0.04))
    partial_equity = partial_tracker.equity(100)
    # Observación 2E
    print(f'parcial: q {partial_tracker.position:.2f}; equity {partial_equity:.3f}')
    if through == '2E': return locals()

    # Ejercicio 3A: crea simulation_maker = StudentMarketMaker() y guarda records = simulate(simulation_maker, seed=2026, sigma=0.5, steps=500); el simulador debe consumir tu clase.
    simulation_maker = StudentMarketMaker()
    records = simulate(simulation_maker, seed=2026, sigma=0.5, steps=500)
    # Observación 3A
    print(f'cierre propio: pnl {records.final_pnl:.4f}; máximo q {records.max_inventory:.3f}; pasos {len(records)}')
    if through == '3A': return locals()

    # Ejercicio 3B: guarda terminal_q desde el último registro de records y max_q desde records.max_inventory; explica por qué el máximo absoluto no es la posición final.
    terminal_q = records[-1][1]
    max_q = records.max_inventory
    # Observación 3B
    print(f'riesgo observado: final {terminal_q:.3f}; máximo {max_q:.3f}')
    if through == '3B': return locals()

    # Ejercicio 4A: calcula shock_sd para sigma=2 y cuatro pasos de igual duración; suma sus varianzas independientes en total_variance y explica por qué no sumas desviaciones.
    shock_sd = 2 / 4**0.5
    total_variance = 4 * shock_sd**2
    # Observación 4A
    print('shock sd:', shock_sd, '; varianza del horizonte:', total_variance)
    if through == '4A': return locals()

    # Observación 4B
    print(f'U(5): {cara_utility(5, 0.1):.6f}; U(10): {cara_utility(10, 0.1):.6f}')
    if through == '4B': return locals()

    # Ejercicio 4C: con A=1 y kappa=1.5, calcula lambda_near a distancia 0.2 y lambda_far a distancia 1.0; predice qué ocurre al mantener la tasa y reducir dt a la mitad.
    A, kappa = 1.0, 1.5
    lambda_near = A * math.exp(-kappa * 0.2)
    lambda_far = A * math.exp(-kappa * 1.0)
    # Observación 4C
    print(f'intensidad cerca: {lambda_near:.6f}; lejos: {lambda_far:.6f}')
    if through == '4C': return locals()

    return locals()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="L13: sigue los apartados del enunciado.")
    parser.add_argument("--through", choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## `opcionales.py`

```python
"""OPTIONAL: variantes separadas de la práctica requerida."""
import math
from maker import StudentMarketMaker

STEPS = ("5A", "5B", "5C")

def practice(through=None):
    # Ejercicio 5A: OPTIONAL: crea negative = StudentMarketMaker(), fija inventory=-0.5 y guarda negative_quotes para mid=100 y tau=1.
    negative = StudentMarketMaker()
    negative.inventory = -0.5
    negative_quotes = negative.quotes(100, 1)
    # Observación 5A
    print('inventario -0.5:', negative_quotes)
    if through == '5A': return locals()

    # Ejercicio 5B: OPTIONAL: fija negative.inventory=0.5 y guarda positive_quotes; calcula same_width comparando ambos anchos con tolerancia 1e-9.
    negative.inventory = 0.5
    positive_quotes = negative.quotes(100, 1)
    same_width = abs((positive_quotes[1]-positive_quotes[0])-(negative_quotes[1]-negative_quotes[0])) < 1e-9
    # Observación 5B
    print('inventario +0.5:', positive_quotes, '; mismo ancho:', same_width)
    if through == '5B': return locals()

    # Ejercicio 5C: OPTIONAL: calcula rate con A=50, kappa=1.5 y distancia 0.2; conviértela en probability por paso mediante 1 - exp(-rate / 500).
    rate = 50 * math.exp(-1.5 * 0.2)
    probability = 1 - math.exp(-rate / 500)
    # Observación 5C
    print(f'tasa {rate:.3f}; probabilidad {probability:.5f}')
    if through == '5C': return locals()

    return locals()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="L13: sigue los apartados del enunciado.")
    parser.add_argument("--through", choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## `models.py`

```python
"""Una ejecución confirmada: datos y comportamiento en una misma clase."""
from math import isfinite


class Fill:
    def __init__(self, side, price, size):
        # Validación proporcionada; no necesitas modificarla.
        valid_numbers = all(isfinite(x) and x > 0 for x in (price, size))
        if side not in ('buy', 'sell') or not valid_numbers:
            raise ValueError('fill requiere lado válido y valores positivos finitos')
        self.side = side
        self.price = price
        self.size = size

    def cash_flow(self):
        sign = -1 if self.side == 'buy' else 1
        return sign * self.price * self.size

    def __repr__(self):
        return f'Fill({self.side} {self.size} @ {self.price})'
```

## `portfolio.py`

```python
"""La cartera conserva estado; Fill proporciona el flujo de cada ejecución."""


class PositionTracker:
    def __init__(self, cash=0.0):
        # Ejercicio 1.a
        self.cash = cash
        self.position = 0.0

    def apply_fill(self, fill):
        # Ejercicio 2.a: usar el comportamiento del Fill de L4.
        self.cash += fill.cash_flow()
        if fill.side == 'buy':
            self.position += fill.size
        else:
            self.position -= fill.size

    def equity(self, mark):
        # Ejercicio 3.a: consultar, sin cambiar atributos.
        return self.cash + self.position * mark
```

## Respuestas y decisiones por apartado

**1A** · 99.40 / 100.60; ancho 1.20. Son precios ofrecidos, todavía no fills.

**1B** · Caja −9.94, q +0.1, equity 0.06 a mark 100. La compra cambia caja y posición.

**1C** · Equity −0.04; caja −9.94 y q +0.1 se conservan. Revalorar no genera una venta.

**1D** · Caja/equity 0.12 y q 0. Esa vuelta exige ambos fills a las quotes fijas; no es un beneficio garantizado.

**2A** · Con q=0.3, centro 99.40 y quotes 98.80 / 100.00. Hereda parámetros de MakerBase y sobrescribe el centro; quotes reutiliza fixed_quotes. tau queda disponible para la clase hija de L14.

**2B** · 99.40/100.60 frente a 98.80/100.00, ancho 1.20 en ambos. El centro baja 0.60; el ancho permanece.

**2C** · 97.50 / 98.50; centro 98 y ancho 1. Es una variante explícita, no el caso inicial.

**2D** · 100.00 / 101.20. Estar corto eleva ambos precios: el bid invita a comprar y el ask intenta frenar nuevas ventas. No garantiza liquidación.

**2E** · q 0.06 y equity 0.084. Se realizó solo parte de la vuelta; la valoración depende del mark mientras quede posición.

**3A** · cierre propio: pnl 2.2878; máximo q 0.400; pasos 500. Una semilla reproducible no garantiza rentabilidad ni menor riesgo para cada otra regla. simulate reinicia inventory y actualiza su propia caja; no llama a PositionTracker ni a ResearchBacktest.

**3B** · El máximo absoluto se observa después de cada fill, incluso si dos fills del mismo paso se compensan. terminal_q describe el cierre y puede ser menor. PnL incluye valoración de inventario abierto, no solo vueltas cerradas.

**4A** · shock_sd=1 y total_variance=4. Para dt=1/4, desviación sigma×sqrt(dt); al sumar cuatro varianzas recuperas sigma², con independencia de los shocks.

**4B** · U(5)=−0.606531 y U(10)=−0.367879: mayor riqueza tiene mayor utilidad. Para gamma=0.5, la opción segura W=0 puntúa −1 y la lotería −1/+1 puntúa −1.127626; misma media, distinta preferencia. Utilidad es una puntuación, no euros; comparar dentro del mismo gamma.

**4C** · Tasas 0.740818 y 0.223130 por horizonte. Más distancia reduce la tasa; no son probabilidades. Transferencia: p=1−exp(−lambda×dt), p_fina=1−exp(−lambda×dt/2). Disminuye, pero no es exactamente p/2. Lambda tiene unidades de 1/tiempo y puede superar 1; p está entre 0 y 1. No cambia el centro ni el ancho.

**5A** · 100.40 / 101.60. Usa la misma clase terminada; no hay una segunda implementación del maker.

**5B** · 98.40 / 99.60 y same_width=True. La corrección tiene signo opuesto y conserva ancho 1.20.

**5C** · Tasa 37.041 por horizonte; probabilidad 0.07140 por paso. El simulador admite como máximo un fill por lado y paso; al cruzar el mid fuerza probabilidad 1, una simplificación explícita.
