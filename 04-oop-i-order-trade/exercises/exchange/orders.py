"""orders.py — órdenes y lados construidos en L4.

La orden conserva el vocabulario conocido (buy/sell) y distingue las dos
formas que ya necesita el curso: una LIMIT con precio y una MARKET sin precio.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import count


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
        if self.order_type is OrderType.MARKET:
            self.price = None
        elif self.price is None:
            raise ValueError("una orden con precio límite necesita `price`")
        if self.size <= 0:
            raise ValueError("`size` debe ser positivo")

    def notional(self) -> float:
        """Valor en quote currency. Indefinido para market (precio = None)."""
        if self.price is None:
            raise ValueError("notional indefinido para una orden MARKET")
        return self.price * self.size

    def __repr__(self) -> str:
        px = "MKT" if self.price is None else f"{self.price:g}"
        return f"Order(#{self.id} {self.side.value} {self.size:g} {self.symbol} @ {px})"
