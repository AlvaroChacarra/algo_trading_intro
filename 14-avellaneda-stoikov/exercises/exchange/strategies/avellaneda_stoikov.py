"""avellaneda_stoikov.py — especialización de market making de L14.

Este módulo aparece por primera vez en el snapshot de L14. Hereda el contrato
público de `MarketMaker` y sustituye el skew heurístico por reservation price y
optimal spread.
"""

from __future__ import annotations

import math

from exchange.book import OrderBook
from exchange.strategy import Action
from exchange.strategies.market_maker import MarketMaker


class AvellanedaStoikov(MarketMaker):
    """Market making óptimo (Avellaneda & Stoikov, 2008).

    tau = (T - t) / T is normalized to [0, 1].
    reservation_price:  r = s - q * gamma * sigma^2 * tau
    optimal_spread:     d = gamma * sigma^2 * tau + (2/gamma) * ln(1 + gamma/kappa)
    """

    def __init__(self, symbol: str, quote_size: float = 0.01,
                 gamma: float = 0.1, sigma: float = 10.0,
                 kappa: float = 1.5, horizon: int = 500) -> None:
        super().__init__(symbol, quote_size=quote_size)
        self.gamma = gamma
        self.sigma = sigma
        self.kappa = kappa
        self.horizon = horizon
        self._t = 0

    @property
    def time(self) -> int:
        return self._t

    @time.setter
    def time(self, value: int) -> None:
        self._t = int(value)

    def _time_left(self) -> float:
        return max(0.0, (self.horizon - self.time) / self.horizon)

    def reservation_price(self, mid: float) -> float:
        tau = self._time_left()
        return mid - self.inventory * self.gamma * self.sigma ** 2 * tau

    def optimal_spread(self) -> float:
        tau = self._time_left()
        return (self.gamma * self.sigma ** 2 * tau
                + (2 / self.gamma) * math.log(1 + self.gamma / self.kappa))

    def quotes(self, book: OrderBook) -> tuple[float, float]:
        r = self.reservation_price(book.mid)
        half = self.optimal_spread() / 2
        return r - half, r + half

    def on_book_update(self, book: OrderBook) -> list[Action]:
        actions = super().on_book_update(book)
        self.time += 1
        return actions
