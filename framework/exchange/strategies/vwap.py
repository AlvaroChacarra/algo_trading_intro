"""vwap.py — ejecución VWAP sobre el framework.

Construido en L12. Reparte una cantidad objetivo a lo largo de la sesión
siguiendo un perfil de volumen: en cada tick envía un trozo (market order)
proporcional al volumen esperado de ese intervalo.

La estrategia canónica consume un perfil fijo durante toda la ejecución
(baseline TWAP / perfil medio). Los ejercicios OPTIONAL permiten estimar y
comparar perfiles candidatos fuera de la estrategia, pero no implementan una
actualización adaptativa online.
"""

from __future__ import annotations

from fractions import Fraction
import math

from exchange.book import OrderBook
from exchange.orders import Order, OrderType, Side
from exchange.strategy import Action, NewOrder, Strategy
from exchange.trades import Fill


# A decimal parent near the top of the binary64 range can accumulate slightly
# more than 1e-12 relative error when its much smaller executed component is
# recovered from ``parent - remaining`` (for example 1e308 - 1e300).  Keep the
# guard relative to the effect, rather than the parent, but allow that bounded
# representation error.  Effects rounded to zero and material one-unit losses
# are still rejected below.
_EFFECT_FIDELITY_DENOMINATOR = 10**11


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


class VWAPStrategy(Strategy):
    def __init__(self, symbol: str, side: Side, total_size: float,
                 horizon: int, profile: list[float] | None = None) -> None:
        self.symbol = symbol
        self.side = Side(side)
        if isinstance(total_size, bool):
            raise ValueError("total_size must be numeric, not boolean")
        self.total_size = float(total_size)
        if not math.isfinite(self.total_size) or self.total_size <= 0:
            raise ValueError("total_size must be finite and positive")
        if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
            raise ValueError("horizon must be a positive integer")
        self.horizon = horizon
        # Sin perfil -> pesos uniformes (TWAP). Con perfil -> VWAP. Se copia y
        # normaliza para que una mutación posterior del caller no cambie el plan.
        if profile is not None and any(isinstance(x, bool) for x in profile):
            raise ValueError("profile weights must be numeric, not boolean")
        weights = [1.0] * horizon if profile is None else [float(x) for x in profile]
        if len(weights) != horizon:
            raise ValueError("profile length must equal horizon")
        if any(not math.isfinite(x) or x < 0 for x in weights):
            raise ValueError("profile weights must be finite and non-negative")
        weight_sum = sum(weights)
        if not math.isfinite(weight_sum) or weight_sum <= 0:
            raise ValueError("profile weights must have a positive sum")
        self.profile = [x / weight_sum for x in weights]
        self._t = 0
        self._executed = 0.0

    def _runtime_parameters(self) -> tuple[float, int, list[float]]:
        if isinstance(self.total_size, bool):
            raise ValueError("total_size must be numeric, not boolean")
        try:
            total_size = float(self.total_size)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("total_size must be numeric") from exc
        if not math.isfinite(total_size) or total_size <= 0:
            raise ValueError("total_size must be finite and positive")
        if (isinstance(self.horizon, bool)
                or not isinstance(self.horizon, int) or self.horizon <= 0):
            raise ValueError("horizon must be a positive integer")
        if not isinstance(self.profile, (list, tuple)):
            raise ValueError("profile must be a sequence of weights")
        if len(self.profile) != self.horizon:
            raise ValueError("profile length must equal horizon")
        if any(isinstance(weight, bool) for weight in self.profile):
            raise ValueError("profile weights must be numeric, not boolean")
        try:
            profile = [float(weight) for weight in self.profile]
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("profile weights must be numeric") from exc
        if any(not math.isfinite(weight) or weight < 0 for weight in profile):
            raise ValueError("profile weights must be finite and non-negative")
        if not math.isclose(math.fsum(profile), 1.0, rel_tol=1e-12, abs_tol=0.0):
            raise ValueError("profile weights must remain normalized")
        if (isinstance(self._t, bool) or not isinstance(self._t, int)
                or self._t < 0):
            raise ValueError("execution clock must be a non-negative integer")
        if (isinstance(self._executed, bool)
                or not isinstance(self._executed, (int, float))
                or not math.isfinite(float(self._executed))
                or not 0.0 <= float(self._executed) <= total_size):
            raise ValueError("executed quantity must be finite and within parent")
        return total_size, self.horizon, profile

    def on_book_update(self, book: OrderBook) -> list[Action]:
        total_size, horizon, profile = self._runtime_parameters()
        try:
            side = Side(self.side)
        except (TypeError, ValueError) as exc:
            raise ValueError("side must remain a valid Side") from exc
        if self._executed >= total_size:
            return []
        # The schedule is cumulative: if a previous market slice was only
        # partially filled, the next tick retries the shortfall instead of
        # pretending that submitted quantity was executed.
        if self._t < horizon:
            target = (total_size if self._t == horizon - 1 else
                      total_size * math.fsum(profile[:self._t + 1]))
            self._t += 1
        else:
            # If the final scheduled slice was only partially filled, keep
            # retrying the exact parent residual on later market updates.
            target = total_size
        slice_size = min(
            max(0.0, target - self._executed),
            total_size - self._executed,
        )
        if slice_size <= 0.0:
            return []
        return [NewOrder(Order(self.symbol, side, slice_size,
                               order_type=OrderType.MARKET))]

    def on_fill(self, fill: Fill) -> None:
        """Advance execution progress only from actual fills."""
        total_size, _, _ = self._runtime_parameters()
        try:
            side = Side(self.side)
        except (TypeError, ValueError) as exc:
            raise ValueError("side must remain a valid Side") from exc
        if fill.symbol == self.symbol and fill.side is side:
            remaining = total_size - self._executed
            if fill.size > remaining:
                raise ValueError("fill exceeds remaining parent quantity")
            next_executed = self._executed + fill.size
            if not _has_faithful_effect(
                self._executed, next_executed, fill.size
            ):
                raise OverflowError("fill progress is not representable")
            next_remaining = total_size - next_executed
            if next_remaining < 0.0:
                raise OverflowError("remaining parent quantity is not representable")
            if next_remaining == 0.0:
                faithful_partition = (
                    Fraction.from_float(next_executed)
                    == Fraction.from_float(total_size)
                )
            else:
                # Check both sides of total = executed + remaining.  Measuring
                # only against the large parent can hide a whole-unit error in
                # the smaller component and make the final retry over-execute.
                faithful_partition = (
                    _has_faithful_effect(
                        total_size, next_remaining, -next_executed
                    )
                    and _has_faithful_effect(
                        total_size, next_executed, -next_remaining
                    )
                )
            if not faithful_partition:
                raise OverflowError("remaining parent quantity is not representable")
            self._executed = next_executed
