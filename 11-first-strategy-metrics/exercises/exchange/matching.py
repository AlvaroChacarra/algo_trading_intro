"""matching.py — cómo se cruzan las órdenes contra el libro.

Construido en L8. Aquí el mercado deja de ser una foto y pasa a tener dinámica:
una orden entra, consume liquidez del lado contrario y genera fills.

Tipos soportados:
    MARKET -> cruza al precio que haga falta hasta llenarse o agotar el libro.
    LIMIT  -> cruza solo a precios igual o mejores que el límite; el resto descansa.
    IOC    -> como LIMIT pero el remanente se cancela (no descansa).
    FOK    -> o se llena entera o no se ejecuta nada.
"""

from __future__ import annotations

from exchange.book import OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.trades import Fill

_EPS = 1e-12


class MatchingEngine:
    def __init__(self) -> None:
        """Create the stateless canonical matching engine."""

    def process(self, order: Order, book: OrderBook,
                timestamp: int | None = None) -> list[Fill]:
        """Cruza `order` contra `book`. Muta el libro y devuelve los fills."""
        opposite = book.asks if order.side is Side.BUY else book.bids

        # 1) Recorre el lado contrario acumulando lo que se podría cruzar.
        remaining = order.size
        planned: list[tuple[float, float]] = []  # (precio, tamaño)
        for lv in opposite:
            if remaining <= _EPS:
                break
            if order.order_type is not OrderType.MARKET and not self._crosses(order, lv.price):
                break
            take = min(remaining, lv.size)
            planned.append((lv.price, take))
            remaining -= take

        filled = order.size - remaining

        # 2) FOK: si no se puede llenar entera, no se toca nada.
        if order.order_type is OrderType.FOK and filled < order.size - _EPS:
            return []

        # 3) Aplica el cruce: consume liquidez y emite fills.
        fills: list[Fill] = []
        for price, take in planned:
            consumed_side = Side.SELL if order.side is Side.BUY else Side.BUY
            book.reduce(consumed_side, price, take)
            fills.append(Fill(order.id, order.symbol, order.side, price, take, timestamp))

        # 4) Remanente: una LIMIT descansa; MARKET/IOC se cancelan.
        if remaining > _EPS and order.order_type is OrderType.LIMIT:
            book.add_limit(order.side, order.price, remaining)

        return fills

    @staticmethod
    def _crosses(order: Order, level_price: float) -> bool:
        if order.side is Side.BUY:
            return order.price >= level_price
        return order.price <= level_price
