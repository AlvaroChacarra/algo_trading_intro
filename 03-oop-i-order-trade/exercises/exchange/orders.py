"""orders.py — el objeto más básico del motor: una orden.

Construido en L3 (OOP I). Continuación directa del `Order` de las clases de
fundamentos: mismos campos (symbol, side, price, size), ahora con tipo de orden
y un id para poder cancelarla.

`Side` y `OrderType` heredan de `str` para que sigan comportándose como las
cadenas "buy"/"sell" que el alumno ya conoce de L1-L2, pero con la seguridad de
un Enum (no se puede escribir "byu" por error).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import count


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

    @property
    def opposite(self) -> "Side":
        return Side.SELL if self is Side.BUY else Side.BUY


class OrderType(str, Enum):
    LIMIT = "limit"    # descansa en el libro hasta cruzarse o cancelarse
    MARKET = "market"  # consume liquidez ya; sin precio límite
    IOC = "ioc"        # immediate-or-cancel: cruza lo que pueda, cancela el resto
    FOK = "fok"        # fill-or-kill: o se ejecuta entera o nada


_order_ids = count(1)


@dataclass
class Order:
    symbol: str
    side: Side
    size: float
    price: float | None = None              # None para órdenes MARKET
    order_type: OrderType = OrderType.LIMIT
    id: int = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        # normaliza strings -> Enum (acepta Order("BTCUSDT", "buy", ...))
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
