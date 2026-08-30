"""market_maker.py — market making heurístico construido en L13.

`MarketMaker` cotiza bid y ask alrededor del mid con un skew lineal por
inventario: cuanto más largo está, más baja ambas cotizaciones para soltar.
La especialización de L14 vive en otro módulo para que el snapshot de L13 no
exponga antes de tiempo su clase ni sus fórmulas.
"""

from __future__ import annotations

from fractions import Fraction
import math

from exchange.book import OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.strategy import Action, NewOrder, Strategy


_EFFECT_FIDELITY_DENOMINATOR = 10**12


def _has_faithful_effect(before: float, after: float, expected: float) -> bool:
    """Compare the exact stored-state difference to the expected effect."""
    if (not math.isfinite(before) or not math.isfinite(after)
            or not math.isfinite(expected) or expected == 0.0):
        return False
    actual_exact = Fraction.from_float(after) - Fraction.from_float(before)
    expected_exact = Fraction.from_float(expected)
    if actual_exact == 0 or (actual_exact > 0) != (expected_exact > 0):
        return False
    error = abs(actual_exact - expected_exact)
    return error * _EFFECT_FIDELITY_DENOMINATOR <= abs(expected_exact)


class MarketMaker(Strategy):
    """Market maker naive: spread fijo + skew lineal por inventario."""

    half_spread: float
    inventory_skew: float

    def __init__(self, symbol: str, quote_size: float = 0.01,
                 half_spread: float = 5.0, inventory_skew: float = 2.0) -> None:
        if any(isinstance(value, bool) for value in (
                quote_size, half_spread, inventory_skew)):
            raise ValueError("market-maker parameters must be numeric, not boolean")
        quote_size = float(quote_size)
        half_spread = float(half_spread)
        inventory_skew = float(inventory_skew)
        if not math.isfinite(quote_size) or quote_size <= 0:
            raise ValueError("quote_size must be finite and positive")
        if not math.isfinite(half_spread) or half_spread < 0:
            raise ValueError("half_spread must be finite and non-negative")
        if not math.isfinite(inventory_skew):
            raise ValueError("inventory_skew must be finite")
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
        if isinstance(value, bool):
            raise ValueError("inventory must be numeric, not boolean")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("inventory must be finite")
        self._inventory = value

    def _runtime_parameters(self) -> tuple[float, float, float]:
        values = (self.quote_size, self.half_spread, self.inventory_skew)
        if any(isinstance(value, bool) for value in values):
            raise ValueError("market-maker parameters must be numeric, not boolean")
        try:
            quote_size, half_spread, inventory_skew = map(float, values)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("market-maker parameters must be numeric") from exc
        if not math.isfinite(quote_size) or quote_size <= 0:
            raise ValueError("quote_size must be finite and positive")
        if not math.isfinite(half_spread) or half_spread < 0:
            raise ValueError("half_spread must be finite and non-negative")
        if not math.isfinite(inventory_skew):
            raise ValueError("inventory_skew must be finite")
        return quote_size, half_spread, inventory_skew

    def reservation_price(self, mid: float) -> float:
        """Centro de las cotizaciones. Naive: mid desplazado por inventario."""
        if isinstance(mid, bool):
            raise ValueError("mid must be numeric, not boolean")
        mid = float(mid)
        if not math.isfinite(mid) or mid <= 0:
            raise ValueError("mid must be finite and positive")
        _, _, inventory_skew = self._runtime_parameters()
        value = mid - inventory_skew * self.inventory
        if not math.isfinite(value):
            raise OverflowError("reservation price is non-finite")
        return value

    def quotes(self, book: OrderBook) -> tuple[float, float]:
        _, half_spread, _ = self._runtime_parameters()
        r = self.reservation_price(book.mid)
        return r - half_spread, r + half_spread

    def on_book_update(self, book: OrderBook) -> list[Action]:
        quote_size, _, _ = self._runtime_parameters()
        if book.mid is None:
            return []
        bid_px, ask_px = self.quotes(book)
        return [
            NewOrder(Order(self.symbol, Side.BUY, quote_size, price=bid_px,
                           order_type=OrderType.LIMIT)),
            NewOrder(Order(self.symbol, Side.SELL, quote_size, price=ask_px,
                           order_type=OrderType.LIMIT)),
        ]

    def on_fill(self, fill) -> None:
        self._runtime_parameters()
        signed = fill.size if fill.side == "buy" else -fill.size
        next_inventory = self.inventory + signed
        if not math.isfinite(next_inventory):
            raise OverflowError("fill would make strategy inventory non-finite")
        if not _has_faithful_effect(
            self.inventory, next_inventory, signed
        ):
            raise OverflowError("fill inventory change is not representable")
        self.inventory = next_inventory
