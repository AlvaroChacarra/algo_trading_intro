"""Simulador proporcionado para research en L13–L14.

Horizonte 1; sigma por horizonte; llegadas sintéticas, sin comisiones, cola,
impacto ni latencia. No comprueba respuestas ni puntúa estrategias.
"""
import math
import random


class MakerBase:
    def __init__(self, half_spread=0.6, skew=2.0, size=0.1):
        if not all(math.isfinite(x) for x in (half_spread, skew, size)) or half_spread < 0 or size <= 0:
            raise ValueError('parámetros de maker fuera de dominio')
        self.half_spread = half_spread
        self.skew = skew
        self.size = size
        self.inventory = 0.0

    def reservation_price(self, mid, tau):
        raise NotImplementedError('define el centro en tu subclase')

    def quotes(self, mid, tau):
        center = self.reservation_price(mid, tau)
        return center - self.half_spread, center + self.half_spread


class SimulationRecords(list):
    """Pares (PnL, posición) al cierre y máximo observado después de cada fill."""
    def __init__(self):
        super().__init__()
        self.max_inventory = 0.0

    @property
    def final_pnl(self):
        return self[-1][0] if self else 0.0


def simulate(maker, seed=42, steps=500, sigma=0.5, intensity=50.0, kappa=1.5):
    if not isinstance(steps, int) or steps <= 0 or not all(math.isfinite(x) for x in (sigma, intensity, kappa)) or sigma < 0 or intensity < 0 or kappa <= 0:
        raise ValueError('parámetros de simulación fuera de dominio')
    rng = random.Random(seed)
    maker.inventory = 0.0
    cash = 0.0
    mid = 100.0
    dt = 1.0 / steps
    records = SimulationRecords()
    for step in range(steps):
        bid, ask = maker.quotes(mid, 1 - step * dt)
        if not 0 < bid <= ask or not all(math.isfinite(x) for x in (bid, ask)):
            raise ValueError('cotizaciones inválidas')
        for side, price, distance in [('buy', bid, mid - bid), ('sell', ask, ask - mid)]:
            probability = 1.0 if distance < 0 else -math.expm1(-intensity * math.exp(-kappa * distance) * dt)
            if rng.random() < probability:
                signed_size = maker.size if side == 'buy' else -maker.size
                cash -= price * signed_size
                maker.inventory += signed_size
                records.max_inventory = max(records.max_inventory, abs(maker.inventory))
        mid += rng.gauss(0, sigma * math.sqrt(dt))
        if not math.isfinite(mid) or mid <= 0:
            raise ValueError('trayectoria fuera del dominio de precios positivos')
        records.append((cash + maker.inventory * mid, maker.inventory))
    return records
