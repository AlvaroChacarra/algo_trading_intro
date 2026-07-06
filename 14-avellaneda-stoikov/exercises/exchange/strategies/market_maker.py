"""market_maker.py — market making sobre el framework.

Construido en L13-L14.

L13 (MarketMaker): cotiza bid y ask alrededor del mid con un skew lineal por
inventario — cuanto más largo estás, más bajas las cotizaciones para soltar.

L14 (AvellanedaStoikov): sustituye el skew heurístico por el reservation
price y el optimal spread del modelo de Avellaneda-Stoikov, que salen de
maximizar utilidad CARA bajo riesgo de inventario.
"""

from __future__ import annotations

import math

from exchange.book import OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.strategy import Action, NewOrder, Strategy


class MarketMaker(Strategy):
    """Market maker naive: spread fijo + skew lineal por inventario."""

    def __init__(self, symbol: str, quote_size: float = 0.01,
                 half_spread: float = 5.0, inventory_skew: float = 2.0) -> None:
        self.symbol = symbol
        self.quote_size = quote_size
        self.half_spread = half_spread
        self.inventory_skew = inventory_skew
        self._inventory = 0.0

    def reservation_price(self, mid: float) -> float:
        """Centro de las cotizaciones. Naive: mid desplazado por inventario."""
        return mid - self.inventory_skew * self._inventory

    def quotes(self, book: OrderBook) -> tuple[float, float]:
        r = self.reservation_price(book.mid)
        return r - self.half_spread, r + self.half_spread

    def on_book_update(self, book: OrderBook) -> list[Action]:
        if book.mid is None:
            return []
        bid_px, ask_px = self.quotes(book)
        return [
            NewOrder(Order(self.symbol, Side.BUY, self.quote_size, price=bid_px,
                           order_type=OrderType.LIMIT)),
            NewOrder(Order(self.symbol, Side.SELL, self.quote_size, price=ask_px,
                           order_type=OrderType.LIMIT)),
        ]

    def on_fill(self, fill) -> None:
        self._inventory += fill.size if fill.side == "buy" else -fill.size


class AvellanedaStoikov(MarketMaker):
    """Market making óptimo (Avellaneda & Stoikov, 2008).

    reservation_price:  r = s - q * gamma * sigma^2 * (T - t)
    optimal_spread:     d = gamma * sigma^2 * (T - t) + (2/gamma) * ln(1 + gamma/kappa)
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

    def _time_left(self) -> float:
        return max(0.0, (self.horizon - self._t) / self.horizon)

    def reservation_price(self, mid: float) -> float:
        tau = self._time_left()
        return mid - self._inventory * self.gamma * self.sigma ** 2 * tau

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
        self._t += 1
        return actions
