"""simulation.py — simulador de market making.

Construido en L14. El backtest de replay (market.py, L9) sirve para ejecución
(VWAP cruza market orders y siempre llena). Pero un market maker pone órdenes
límite y necesita un modelo de *cuándo le ejecutan*: cuanto más cerca del mid
cotiza, más probable es que le golpeen.

Modelo (Avellaneda-Stoikov): la intensidad de llegada de órdenes a distancia
`delta` del mid es lambda(delta) = A * exp(-kappa * delta). El mid sigue un
paseo aleatorio. Es el entorno mínimo para ver moverse inventario y PnL.
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
    mid: list[float] = field(default_factory=list)
    inventory: list[float] = field(default_factory=list)
    pnl: list[float] = field(default_factory=list)

    @property
    def final_pnl(self) -> float:
        return self.pnl[-1] if self.pnl else 0.0

    @property
    def max_inventory(self) -> float:
        return max((abs(q) for q in self.inventory), default=0.0)


class MMSimulation:
    """Simula un market maker contra un mid que hace un paseo aleatorio."""

    def __init__(self, strategy: MarketMaker, s0: float = 100.0, sigma: float = 0.5,
                 steps: int = 500, A: float = 1.0, kappa: float = 1.5,
                 seed: int = 42) -> None:
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
        return min(1.0, self.A * math.exp(-self.kappa * delta))

    def run(self) -> SimResult:
        mid = self.s0
        cash, inventory = 0.0, 0.0
        res = SimResult()

        for _ in range(self.steps):
            # libro mínimo de un nivel a cada lado, centrado en el mid actual
            book = OrderBook(self.strategy.symbol,
                             [Level(mid - 0.5, 1.0)], [Level(mid + 0.5, 1.0)])
            bid_px, ask_px = self.strategy.quotes(book)

            # ¿nos golpean el bid? (alguien vende contra nuestra compra)
            if self.rng.random() < self._fill_prob(mid - bid_px):
                cash -= bid_px * self.strategy.quote_size
                inventory += self.strategy.quote_size
                self.strategy.on_fill(_hit(self.strategy.symbol, Side.BUY,
                                           bid_px, self.strategy.quote_size))
            # ¿nos golpean el ask? (alguien compra contra nuestra venta)
            if self.rng.random() < self._fill_prob(ask_px - mid):
                cash += ask_px * self.strategy.quote_size
                inventory -= self.strategy.quote_size
                self.strategy.on_fill(_hit(self.strategy.symbol, Side.SELL,
                                           ask_px, self.strategy.quote_size))

            if hasattr(self.strategy, "_t"):
                self.strategy._t += 1

            mid += self.rng.gauss(0, self.sigma)  # paseo aleatorio
            res.mid.append(mid)
            res.inventory.append(inventory)
            res.pnl.append(cash + inventory * mid)  # PnL marcado a mercado

        return res


def _hit(symbol, side, price, size):
    from exchange.trades import Fill
    return Fill(0, symbol, side, price, size)
