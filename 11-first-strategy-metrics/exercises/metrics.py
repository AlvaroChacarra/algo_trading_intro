"""Métricas sobre registros: leer y componer, sin cambiar mercado ni cartera."""
from math import isfinite


def running_peaks(equity, initial_equity):
    # TODO · Ejercicio 1B: conserva el mayor pico visto en running_peaks, empezando en initial_equity; devuelve un pico por observación.
    raise NotImplementedError('Completa 1B en metrics.py.')


def drawdowns(equity, initial_equity=1000):
    # TODO · Ejercicio 1C: compón running_peaks para devolver pico menos equity en cada observación, sin modificar la curva.
    raise NotImplementedError('Completa 1C en metrics.py.')


def max_drawdown(equity, initial_equity=1000):
    # TODO · Ejercicio 1D: devuelve la mayor caída calculada por drawdowns; una curva vacía devuelve 0.0.
    raise NotImplementedError('Completa 1D en metrics.py.')


def weighted_price(fills):
    # TODO · Ejercicio 2A: pondera price por size en weighted_price; divide por cantidad confirmada y devuelve None sin fills.
    raise NotImplementedError('Completa 2A en metrics.py.')


def execution_cost_bps(fills, arrival_mid, side):
    if not isfinite(arrival_mid) or arrival_mid <= 0 or side not in ('buy','sell'):
        raise ValueError('referencia positiva y lado válido')
    if any(fill.side != side for fill in fills):
        raise ValueError('agrupa fills del mismo lado')
    # TODO · Ejercicio 2B: calcula execution_cost_bps frente al arrival previo, con signo buy/sell; conserva las guardias proporcionadas y separa fees.
    raise NotImplementedError('Completa 2B en metrics.py.')


def max_inventory(positions):
    # TODO · Ejercicio 2C: devuelve el máximo valor absoluto de positions, o 0.0 si está vacío; mide inventario muestreado en BTC.
    raise NotImplementedError('Completa 2C en metrics.py.')


def capture_arrival(market):
    # TODO · Ejercicio 3B: completa capture_arrival y guarda arrival, pnl, pasos y n_fills del experimento original; separa equity de PnL.
    raise NotImplementedError('Completa 3B en metrics.py.')
