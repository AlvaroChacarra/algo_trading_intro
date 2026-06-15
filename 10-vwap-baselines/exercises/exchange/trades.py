"""trades.py — el resultado de cruzar una orden: un fill.

Construido en L3 (OOP I). Hereda la idea de `Trade.cash_flow()` de las clases de
fundamentos: una compra resta caja, una venta la suma.
"""

from __future__ import annotations

from dataclasses import dataclass

from exchange.orders import Side


@dataclass
class Fill:
    order_id: int
    symbol: str
    side: Side
    price: float
    size: float
    timestamp: int | None = None

    def __post_init__(self) -> None:
        self.side = Side(self.side)

    @property
    def notional(self) -> float:
        return self.price * self.size

    def cash_flow(self) -> float:
        """Compra = caja negativa, venta = caja positiva."""
        sign = -1.0 if self.side is Side.BUY else 1.0
        return sign * self.price * self.size

    def __repr__(self) -> str:
        return (f"Fill(#{self.order_id} {self.side.value} "
                f"{self.size:g} @ {self.price:g})")
