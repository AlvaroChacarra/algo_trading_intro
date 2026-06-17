"""vwap.py — ejecución VWAP sobre el framework.

Construido en L10-L11. Reparte una cantidad objetivo a lo largo de la sesión
siguiendo un perfil de volumen: en cada tick envía un trozo (market order)
proporcional al volumen esperado de ese intervalo.

L10: perfil estático (baseline TWAP / perfil medio).
L11: el perfil se puede predecir de forma dinámica (extensión ML).
"""

from __future__ import annotations

from exchange.book import OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.strategy import Action, NewOrder, Strategy


class VWAPStrategy(Strategy):
    def __init__(self, symbol: str, side: Side, total_size: float,
                 horizon: int, profile: list[float] | None = None) -> None:
        self.symbol = symbol
        self.side = Side(side)
        self.total_size = total_size
        self.horizon = horizon
        # Sin perfil -> pesos uniformes (TWAP). Con perfil -> VWAP.
        self.profile = profile or [1.0 / horizon] * horizon
        self._t = 0
        self._executed = 0.0

    def on_book_update(self, book: OrderBook) -> list[Action]:
        if self._t >= self.horizon or self._executed >= self.total_size - 1e-12:
            return []
        weight = self.profile[self._t] / sum(self.profile)
        slice_size = min(self.total_size * weight, self.total_size - self._executed)
        self._t += 1
        if slice_size <= 1e-12:
            return []
        self._executed += slice_size
        return [NewOrder(Order(self.symbol, self.side, slice_size,
                               order_type=OrderType.MARKET))]
