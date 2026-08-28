"""market_maker.py — market making heurístico construido en L13.

`MarketMaker` cotiza bid y ask alrededor del mid con un skew lineal por
inventario: cuanto más largo está, más baja ambas cotizaciones para soltar.
La especialización de L14 vive en otro módulo para que el snapshot de L13 no
exponga antes de tiempo su clase ni sus fórmulas.
"""

from __future__ import annotations

from exchange.book import OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.strategy import Action, NewOrder, Strategy


class MarketMaker(Strategy):
    """Market maker naive: spread fijo + skew lineal por inventario."""

    half_spread: float
    inventory_skew: float

    def __init__(self, symbol: str, quote_size: float = 0.01,
                 half_spread: float = 5.0, inventory_skew: float = 2.0) -> None:
        self.symbol = symbol
        self.quote_size = quote_size
        self.half_spread = half_spread
        self.inventory_skew = inventory_skew
        self._inventory = 0.0

    @property
    def inventory(self) -> float:
        return self._inventory

    @inventory.setter
    def inventory(self, value: float) -> None:
        self._inventory = float(value)

    def reservation_price(self, mid: float) -> float:
        """Centro de las cotizaciones. Naive: mid desplazado por inventario."""
        return mid - self.inventory_skew * self.inventory

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
        self.inventory += fill.size if fill.side == "buy" else -fill.size
