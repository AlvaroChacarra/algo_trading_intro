"""trades.py — el resultado de cruzar una orden: un fill.

Construido en L4 (OOP I). Hereda la idea de `Trade.cash_flow()` de las clases de
fundamentos: una compra resta caja, una venta la suma.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from exchange.orders import Side, _has_faithful_product


@dataclass(frozen=True)
class Fill:
    order_id: int
    symbol: str
    side: Side
    price: float
    size: float
    timestamp: int | None = None

    def __post_init__(self) -> None:
        if (isinstance(self.order_id, bool) or not isinstance(self.order_id, int)
                or self.order_id < 0):
            raise ValueError("fill order_id must be a non-negative integer")
        if (self.timestamp is not None
                and (isinstance(self.timestamp, bool)
                     or not isinstance(self.timestamp, int))):
            raise ValueError("fill timestamp must be an integer or None")
        if isinstance(self.price, bool) or isinstance(self.size, bool):
            raise ValueError("fill price and size must be numeric, not boolean")
        object.__setattr__(self, "side", Side(self.side))
        object.__setattr__(self, "price", float(self.price))
        object.__setattr__(self, "size", float(self.size))
        if not math.isfinite(self.price) or self.price <= 0:
            raise ValueError("fill price must be finite and positive")
        if not math.isfinite(self.size) or self.size <= 0:
            raise ValueError("fill size must be finite and positive")

    @property
    def notional(self) -> float:
        value = self.price * self.size
        if not math.isfinite(value) or value == 0.0:
            raise OverflowError("fill notional is non-finite or underflowed to zero")
        if not _has_faithful_product(value, self.price, self.size):
            raise OverflowError("fill notional is not faithfully representable")
        return value

    def cash_flow(self) -> float:
        """Compra = caja negativa, venta = caja positiva."""
        sign = -1.0 if self.side is Side.BUY else 1.0
        return sign * self.notional

    def __repr__(self) -> str:
        return (f"Fill(#{self.order_id} {self.side.value} "
                f"{self.size:g} @ {self.price:g})")
