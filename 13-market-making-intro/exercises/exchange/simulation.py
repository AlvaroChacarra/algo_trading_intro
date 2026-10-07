"""simulation.py — simulador de market making.

Construido en L13. El backtest de replay (market.py, L9) sirve para ejecución
(VWAP cruza órdenes MARKET hasta la liquidez disponible). Pero un market maker pone órdenes
límite y necesita un modelo de *cuándo le ejecutan*: cuanto más cerca del mid
cotiza, más probable es que le golpeen.

Modelo mínimo de llegada: la intensidad de órdenes a distancia `delta` del mid
es lambda(delta) = A * exp(-kappa * delta). L13 usa esta intuición para preparar
el parámetro kappa; L14 reutiliza el mismo entorno sin exponer su clase antes de
tiempo. El mid sigue un paseo aleatorio.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from exchange.book import Level, OrderBook
from exchange.orders import Side
from exchange.strategies.market_maker import MarketMaker


@dataclass
class SimResult:
    """Las curvas guardan un punto al cierre de cada paso, después del shock.

    `inventory_peak` también registra estados intermedios tras cada fill: una
    compra y una venta en el mismo paso pueden dejar posición final cero sin
    que el máximo alcanzado fuese cero. El orden del modelo es compra y venta;
    no hay un movimiento de precio entre esos dos eventos.
    """

    mid: list[float] = field(default_factory=list)
    inventory: list[float] = field(default_factory=list)
    pnl: list[float] = field(default_factory=list)
    inventory_peak: float = 0.0

    @property
    def final_pnl(self) -> float:
        return self.pnl[-1] if self.pnl else 0.0

    @property
    def max_inventory(self) -> float:
        """Máximo inventario absoluto, incluidos los estados entre fills."""
        return max(self.inventory_peak,
                   max((abs(q) for q in self.inventory), default=0.0))


class MMSimulation:
    """Horizonte normalizado a 1: sigma es volatilidad de todo el horizonte.

    A es intensidad por horizonte; dt=1/steps. Cada lado admite como máximo
    un fill por paso, con probabilidad 1-exp(-lambda*dt). Es una aproximación
    por intervalos, sin colas, impacto ni una réplica completa de A–S.
    Para comparar con A–S usa su misma sigma y horizon=steps.
    """

    def __init__(self, strategy: MarketMaker, s0: float = 100.0, sigma: float = 0.5,
                 steps: int = 500, A: float = 50.0, kappa: float = 1.5,
                 seed: int = 42) -> None:
        if not isinstance(steps, int) or steps <= 0:
            raise ValueError("steps debe ser un entero positivo")
        if not all(math.isfinite(x) for x in (s0, sigma, A, kappa)):
            raise ValueError("parámetros de simulación no finitos")
        if s0 <= 0.5 or sigma < 0 or A < 0 or kappa <= 0:
            raise ValueError("s0 > 0.5, sigma/A >= 0 y kappa > 0 requeridos")
        self.dt = 1.0 / steps
        self.seed = seed
        self.strategy = strategy
        self.s0 = s0
        self.sigma = sigma
        self.steps = steps
        self.A = A          # intensidad base de llegada de órdenes
        self.kappa = kappa  # cómo cae la intensidad con la distancia al mid
        self.rng = random.Random(seed)

    def _fill_prob(self, delta: float) -> float:
        """Prob. de que una cotización a distancia `delta` del mid se ejecute."""
        if delta < 0:                       # cotización marketable -> seguro
            return 1.0
        intensity = self.A * math.exp(-self.kappa * delta)
        return -math.expm1(-intensity * self.dt)

    def run(self) -> SimResult:
        self.rng = random.Random(self.seed)
        self.strategy.inventory = 0.0
        if hasattr(self.strategy, "time"):
            self.strategy.time = 0
        mid = self.s0
        cash, inventory = 0.0, 0.0
        res = SimResult()

        for _ in range(self.steps):
            # libro mínimo de un nivel a cada lado, centrado en el mid actual
            book = OrderBook(self.strategy.symbol,
                             [Level(mid - 0.5, 1.0)], [Level(mid + 0.5, 1.0)])
            bid_px, ask_px = self.strategy.quotes(book)
            if not all(math.isfinite(p) and p > 0 for p in (bid_px, ask_px)) or bid_px > ask_px:
                raise ValueError("quotes deben ser positivas, finitas y bid <= ask")

            # ¿nos golpean el bid? (alguien vende contra nuestra compra)
            if self.rng.random() < self._fill_prob(mid - bid_px):
                cash -= bid_px * self.strategy.quote_size
                inventory += self.strategy.quote_size
                res.inventory_peak = max(res.inventory_peak, abs(inventory))
                self.strategy.on_fill(_hit(self.strategy.symbol, Side.BUY,
                                           bid_px, self.strategy.quote_size))
            # ¿nos golpean el ask? (alguien compra contra nuestra venta)
            if self.rng.random() < self._fill_prob(ask_px - mid):
                cash += ask_px * self.strategy.quote_size
                inventory -= self.strategy.quote_size
                res.inventory_peak = max(res.inventory_peak, abs(inventory))
                self.strategy.on_fill(_hit(self.strategy.symbol, Side.SELL,
                                           ask_px, self.strategy.quote_size))

            if hasattr(self.strategy, "time"):
                self.strategy.time += 1

            mid += self.rng.gauss(0, self.sigma * math.sqrt(self.dt))  # paseo aleatorio
            if not math.isfinite(mid) or mid <= 0.5:
                raise ValueError("trayectoria fuera del dominio de precios positivos del simulador")
            res.mid.append(mid)
            res.inventory.append(inventory)
            res.pnl.append(cash + inventory * mid)  # PnL marcado a mercado

        return res


def _hit(symbol, side, price, size):
    from exchange.trades import Fill
    return Fill(0, symbol, side, price, size)
