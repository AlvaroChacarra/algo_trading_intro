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

from fractions import Fraction

from exchange.book import Level, OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.trades import Fill


class MatchingEngine:
    def __init__(self) -> None:
        """Create the stateless canonical matching engine."""

    def process(self, order: Order, book: OrderBook,
                timestamp: int | None = None) -> list[Fill]:
        """Cruza `order` contra `book` mediante un commit atómico."""
        if not isinstance(order, Order):
            raise TypeError("order must be an Order")
        if (isinstance(order.id, bool) or not isinstance(order.id, int)
                or order.id <= 0):
            raise ValueError("order id must be a positive integer")
        if (timestamp is not None
                and (isinstance(timestamp, bool)
                     or not isinstance(timestamp, int))):
            raise ValueError("timestamp must be an integer or None")

        # ``Order`` is intentionally mutable in the introductory lessons. Treat
        # it as an untrusted public-boundary value and reconstruct it before
        # looking at the book, so post-construction mutations cannot bypass its
        # numeric and enum invariants.
        order = Order(
            symbol=order.symbol,
            side=order.side,
            size=order.size,
            price=order.price,
            order_type=order.order_type,
            id=order.id,
        )
        if order.symbol != book.symbol:
            raise ValueError(
                f"symbol mismatch: order={order.symbol!r}, book={book.symbol!r}"
            )
        # Every mutation is first applied to a detached candidate. A numeric
        # representation failure (for example, subtracting 1 from 1e16) or an
        # unrepresentable resting remainder must leave the caller's book and
        # the returned fill ledger untouched.
        candidate = OrderBook(
            book.symbol,
            [Level(level.price, level.size) for level in book.bids],
            [Level(level.price, level.size) for level in book.asks],
        )
        opposite = candidate.asks if order.side is Side.BUY else candidate.bids

        # 1) Recorre el lado contrario acumulando lo que se podría cruzar.
        remaining = Fraction.from_float(order.size)
        planned: list[tuple[float, float]] = []  # (precio, tamaño)
        for lv in opposite:
            if remaining == 0:
                break
            if order.order_type is not OrderType.MARKET and not self._crosses(order, lv.price):
                break
            take_exact = min(remaining, Fraction.from_float(lv.size))
            take = float(take_exact)
            if Fraction.from_float(take) != take_exact:
                raise OverflowError("order remainder is not representable")
            planned.append((lv.price, take))
            remaining -= Fraction.from_float(take)

        # 2) FOK: si no se puede llenar entera, no se toca nada.
        if order.order_type is OrderType.FOK and remaining > 0:
            return []

        # 3) Aplica el cruce: consume liquidez y emite fills.
        fills: list[Fill] = []
        for price, take in planned:
            consumed_side = Side.SELL if order.side is Side.BUY else Side.BUY
            candidate.reduce(consumed_side, price, take)
            fill = Fill(order.id, order.symbol, order.side, price, take, timestamp)
            # A fill whose notional overflows or underflows cannot be booked by
            # the portfolio. Validate that economic effect before publishing
            # either fills or the candidate book.
            _ = fill.notional
            fills.append(fill)

        # 4) Remanente: una LIMIT descansa; MARKET/IOC se cancelan.
        if remaining > 0 and order.order_type is OrderType.LIMIT:
            resting_size = float(remaining)
            if Fraction.from_float(resting_size) != remaining:
                raise OverflowError("limit-order remainder is not representable")
            candidate.add_limit(order.side, order.price, resting_size)

        book.bids = candidate.bids
        book.asks = candidate.asks

        return fills

    @staticmethod
    def _crosses(order: Order, level_price: float) -> bool:
        if order.side is Side.BUY:
            return order.price >= level_price
        return order.price <= level_price
