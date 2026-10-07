"""L12: alcanzar una cantidad acumulada, contando operaciones confirmadas.

Cada orden es MARKET: el residual sin liquidez caduca en ese snapshot.
En el siguiente paso se intenta recuperar el retraso respecto al schedule.
El runner confirma los fills antes de pedir la siguiente decisión.
"""
from __future__ import annotations

from math import isfinite
from exchange.book import OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.strategy import Action, NewOrder, Strategy
from exchange.trades import Fill


class VWAPStrategy(Strategy):
    def __init__(self, symbol: str, side: Side, total_size: float,
                 horizon: int, profile: list[float] | None = None) -> None:
        if not isinstance(horizon, int) or horizon <= 0:
            raise ValueError("horizon debe ser un entero positivo")
        if not isfinite(total_size) or total_size <= 0:
            raise ValueError("total_size debe ser finito y positivo")
        weights = [1.0] * horizon if profile is None else list(profile)
        if (len(weights) != horizon or
                not all(isfinite(w) and w >= 0 for w in weights) or
                not isfinite(sum(weights)) or sum(weights) <= 0):
            raise ValueError("profile necesita horizon pesos finitos no negativos y suma positiva")
        self.symbol = symbol
        self.side = Side(side)
        self.total_size = total_size
        self.horizon = horizon
        total = sum(weights)
        self.profile = [w / total for w in weights]
        self._t = 0
        self._executed = 0.0
        self._scheduled = 0.0
        self._pending: dict[int, float] = {}

    def on_start(self, ctx) -> None:
        self._t = 0
        self._executed = 0.0
        self._scheduled = 0.0
        self._pending.clear()

    @property
    def executed(self) -> float:
        return self._executed

    @property
    def remaining(self) -> float:
        return max(0.0, self.total_size - self._executed)

    def on_book_update(self, book: OrderBook) -> list[Action]:
        self._pending.clear()  # las MARKET anteriores ya finalizaron
        if self._t >= self.horizon or self.remaining <= 1e-12:
            return []
        self._scheduled += self.total_size * self.profile[self._t]
        self._t += 1
        target = self.total_size if self._t == self.horizon else self._scheduled
        size = min(max(0.0, target - self._executed), self.remaining)
        if size <= 1e-12:
            return []
        order = Order(self.symbol, self.side, size, order_type=OrderType.MARKET)
        self._pending[order.id] = size
        return [NewOrder(order)]

    def on_fill(self, fill: Fill) -> None:
        pending = self._pending.get(fill.order_id, 0.0)
        if (fill.symbol != self.symbol or fill.side != self.side or
                fill.size > pending + 1e-12 or fill.size > self.remaining + 1e-12):
            raise ValueError("fill no corresponde a la cantidad pendiente de esta estrategia")
        self._pending[fill.order_id] = max(0.0, pending - fill.size)
        self._executed += fill.size
