"""portfolio.py — seguimiento de caja, inventario y PnL.

Construido en L4 (OOP II). Continuación directa del `PositionTracker` de las
clases de fundamentos: mismo estado privado (`_cash`, `_position`), ahora
alimentado por objetos `Fill` en vez de dicts, y con métricas de PnL.
"""

from __future__ import annotations

from exchange.trades import Fill


class PositionTracker:
    def __init__(self, cash: float = 0.0) -> None:
        # El guión bajo marca 'estado interno': se toca con métodos, no a mano.
        self._cash = float(cash)
        self._position = 0.0
        self._fills: list[Fill] = []

    def apply_fill(self, fill: Fill) -> None:
        self._cash += fill.cash_flow()
        signed = fill.size if fill.side == "buy" else -fill.size
        self._position += signed
        self._fills.append(fill)

    @property
    def cash(self) -> float:
        return self._cash

    @property
    def position(self) -> float:
        return self._position

    @property
    def n_fills(self) -> int:
        return len(self._fills)

    def equity(self, mark_price: float) -> float:
        """Valor total: caja + inventario marcado a mercado."""
        return self._cash + self._position * mark_price

    def unrealized_pnl(self, mark_price: float) -> float:
        return self._position * mark_price

    def __repr__(self) -> str:
        return (f"PositionTracker(cash={self._cash:.2f}, "
                f"pos={self._position:.4f}, fills={self.n_fills})")
