"""portfolio.py — seguimiento de caja, inventario y PnL.

Construido en L5 (OOP II). Continuación directa del `PositionTracker` de las
clases de fundamentos: mismo estado privado (`_cash`, `_position`), ahora
alimentado por objetos `Fill` en vez de dicts, y con métricas de PnL.
"""

from __future__ import annotations

from fractions import Fraction
import math

from exchange.trades import Fill


_EFFECT_FIDELITY_DENOMINATOR = 10**12


def _has_faithful_effect(before: float, after: float, expected: float) -> bool:
    """Compare the exact difference of two stored states to an effect."""
    if (not math.isfinite(before) or not math.isfinite(after)
            or not math.isfinite(expected) or expected == 0.0):
        return False
    actual_exact = Fraction.from_float(after) - Fraction.from_float(before)
    expected_exact = Fraction.from_float(expected)
    if actual_exact == 0 or (actual_exact > 0) != (expected_exact > 0):
        return False
    error = abs(actual_exact - expected_exact)
    return error * _EFFECT_FIDELITY_DENOMINATOR <= abs(expected_exact)


class PositionTracker:
    def __init__(self, cash: float = 0.0) -> None:
        # El guión bajo marca 'estado interno': se toca con métodos, no a mano.
        if isinstance(cash, bool):
            raise ValueError("cash must be numeric, not boolean")
        self._cash = float(cash)
        if not math.isfinite(self._cash):
            raise ValueError("cash must be finite")
        self._position = 0.0
        self._fills: list[Fill] = []

    def apply_fill(self, fill: Fill) -> None:
        cash_flow = fill.cash_flow()
        next_cash = self._cash + cash_flow
        signed = fill.size if fill.side == "buy" else -fill.size
        next_position = self._position + signed
        if not math.isfinite(next_cash) or not math.isfinite(next_position):
            raise OverflowError("fill would make portfolio state non-finite")
        # Both deltas are non-zero by Fill's contract. Reject a swallowed or
        # materially distorted addition before committing any ledger state.
        if (not _has_faithful_effect(self._cash, next_cash, cash_flow)
                or not _has_faithful_effect(
                    self._position, next_position, signed
                )):
            raise OverflowError("fill state change is not representable")
        self._cash = next_cash
        self._position = next_position
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
        if isinstance(mark_price, bool):
            raise ValueError("mark_price must be numeric, not boolean")
        mark_price = float(mark_price)
        if not math.isfinite(mark_price) or mark_price <= 0:
            raise ValueError("mark_price must be finite and positive")
        value = self._cash + self._position * mark_price
        if not math.isfinite(value):
            raise OverflowError("portfolio equity is non-finite")
        return value

    def unrealized_pnl(self, mark_price: float) -> float:
        if isinstance(mark_price, bool):
            raise ValueError("mark_price must be numeric, not boolean")
        mark_price = float(mark_price)
        if not math.isfinite(mark_price) or mark_price <= 0:
            raise ValueError("mark_price must be finite and positive")
        value = self._position * mark_price
        if not math.isfinite(value):
            raise OverflowError("unrealized PnL is non-finite")
        return value

    def __repr__(self) -> str:
        return (f"PositionTracker(cash={self._cash:.2f}, "
                f"pos={self._position:.4f}, fills={self.n_fills})")
