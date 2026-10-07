"""Métricas sobre registros: leer y componer, sin cambiar mercado ni cartera."""
from math import isfinite


def running_peaks(equity, initial_equity):
    # Ejercicio 1B: conserva el mayor pico visto en running_peaks, empezando en initial_equity; devuelve un pico por observación.
    peak = initial_equity
    peaks = []
    for value in equity:
        peak = max(peak, value)
        peaks.append(peak)
    return peaks


def drawdowns(equity, initial_equity=1000):
    # Ejercicio 1C: compón running_peaks para devolver pico menos equity en cada observación, sin modificar la curva.
    peaks = running_peaks(equity, initial_equity)
    return [peak-value for peak,value in zip(peaks,equity)]


def max_drawdown(equity, initial_equity=1000):
    # Ejercicio 1D: devuelve la mayor caída calculada por drawdowns; una curva vacía devuelve 0.0.
    return max(drawdowns(equity, initial_equity), default=0.0)


def weighted_price(fills):
    # Ejercicio 2A: pondera price por size en weighted_price; divide por cantidad confirmada y devuelve None sin fills.
    quantity = sum(fill.size for fill in fills)
    if quantity == 0:
        return None
    return sum(fill.price*fill.size for fill in fills)/quantity


def execution_cost_bps(fills, arrival_mid, side):
    # Ejercicio 2B: calcula execution_cost_bps frente al arrival previo, con signo buy/sell; conserva las guardias proporcionadas y separa fees.
    if not isfinite(arrival_mid) or arrival_mid <= 0 or side not in ('buy','sell'):
        raise ValueError('referencia positiva y lado válido')
    if any(fill.side != side for fill in fills):
        raise ValueError('agrupa fills del mismo lado')
    average = weighted_price(fills)
    if average is None:
        return None
    sign = 1 if side == 'buy' else -1
    return sign*(average-arrival_mid)/arrival_mid*10000


def max_inventory(positions):
    # Ejercicio 2C: devuelve el máximo valor absoluto de positions, o 0.0 si está vacío; mide inventario muestreado en BTC.
    return max((abs(position) for position in positions), default=0.0)


def capture_arrival(market):
    # Ejercicio 3B: completa capture_arrival y guarda arrival, pnl, pasos y n_fills del experimento original; separa equity de PnL.
    first = market.step()
    return first.mid if first is not None else None
