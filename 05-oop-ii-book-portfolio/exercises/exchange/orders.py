"""orders.py — órdenes y lados construidos en L4.

La orden conserva el vocabulario conocido (buy/sell) y distingue las dos
formas que ya necesita el curso: una LIMIT con precio y una MARKET sin precio.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import count
import math


_EFFECT_FIDELITY_DENOMINATOR = 10**12


def _within_fidelity(actual: Fraction, expected: Fraction) -> bool:
    """Compare exact numeric effects with a relative-only 1e-12 bound."""
    if expected == 0:
        return actual == 0
    if actual == 0 or (actual > 0) != (expected > 0):
        return False
    error = abs(actual - expected)
    return error * _EFFECT_FIDELITY_DENOMINATOR <= abs(expected)


def _has_faithful_product(result: float, *factors: float) -> bool:
    """Whether a stored float faithfully represents a product of floats."""
    if not math.isfinite(result) or not all(
        math.isfinite(factor) for factor in factors
    ):
        return False
    expected_exact = Fraction(1)
    for factor in factors:
        expected_exact *= Fraction.from_float(factor)
    return _within_fidelity(Fraction.from_float(result), expected_exact)


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"    # descansa en el libro hasta cruzarse o cancelarse
    MARKET = "market"  # consume liquidez ya; sin precio límite


_order_ids = count(1)


@dataclass
class Order:
    symbol: str
    side: Side
    size: float
    price: float | None = None
    order_type: OrderType = OrderType.LIMIT
    id: int = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.side = Side(self.side)
        self.order_type = OrderType(self.order_type)
        if self.id is None:
            self.id = next(_order_ids)
        elif isinstance(self.id, bool) or not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("`id` must be a positive integer")
        if isinstance(self.size, bool):
            raise ValueError("`size` debe ser numérico, no booleano")
        self.size = float(self.size)
        if not math.isfinite(self.size) or self.size <= 0:
            raise ValueError("`size` debe ser finito y positivo")
        if self.order_type is OrderType.MARKET:
            if isinstance(self.price, bool):
                raise ValueError("`price` debe ser numérico, no booleano")
            self.price = None
        elif self.price is None:
            raise ValueError("una orden con precio límite necesita `price`")
        else:
            if isinstance(self.price, bool):
                raise ValueError("`price` debe ser numérico, no booleano")
            self.price = float(self.price)
            if not math.isfinite(self.price) or self.price <= 0:
                raise ValueError("`price` debe ser finito y positivo")

    def notional(self) -> float:
        """Valor en quote currency. Indefinido para market (precio = None)."""
        if self.price is None:
            raise ValueError("notional indefinido para una orden MARKET")
        value = self.price * self.size
        if not math.isfinite(value) or value == 0.0:
            raise OverflowError("order notional is non-finite or underflowed to zero")
        if not _has_faithful_product(value, self.price, self.size):
            raise OverflowError("order notional is not faithfully representable")
        return value

    def __repr__(self) -> str:
        px = "MKT" if self.price is None else f"{self.price:g}"
        return f"Order(#{self.id} {self.side.value} {self.size:g} {self.symbol} @ {px})"
