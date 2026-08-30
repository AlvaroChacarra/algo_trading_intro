"""avellaneda_stoikov.py — especialización de market making de L14.

Este módulo aparece por primera vez en el snapshot de L14. Hereda el contrato
público de `MarketMaker` y sustituye el skew heurístico por reservation price y
optimal spread.
"""

from __future__ import annotations

import math

from exchange.book import OrderBook
from exchange.strategy import Action
from exchange.strategies.market_maker import MarketMaker


def _stable_product(*values: float) -> float:
    """Multiply non-negative finite values without intermediate overflow."""
    mantissa, exponent = 1.0, 0
    for value in values:
        if value == 0.0:
            return 0.0
        part, part_exponent = math.frexp(value)
        mantissa *= part
        exponent += part_exponent
        mantissa, adjustment = math.frexp(mantissa)
        exponent += adjustment
    try:
        return math.ldexp(mantissa, exponent)
    except OverflowError:
        return math.inf


class AvellanedaStoikov(MarketMaker):
    """Market making óptimo (Avellaneda & Stoikov, 2008).

    Convención dimensional del curso:

    - ``tau = clip((H - t) / H, 0, 1)`` es tiempo restante normalizado.
    - ``sigma`` es ``sigma_H``, la desviación típica del cambio de precio durante
      el horizonte completo ``H``; por tanto ``sigma_H**2 * tau`` es la varianza
      de precio restante.
    - ``gamma`` y ``kappa`` se expresan en inversas de precio; ``q`` cuenta
      unidades de inventario del modelo.

    Con esa convención, ambos términos devuelven unidades de precio:

    reservation_price:  r = s - q * gamma * sigma_H^2 * tau
    optimal_spread:      d = gamma * sigma_H^2 * tau
                             + (2/gamma) * ln(1 + gamma/kappa)
    """

    simulation_contract = "sigma-horizon-kappa"

    def __init__(self, symbol: str, quote_size: float = 0.01,
                 gamma: float = 0.1, sigma: float = 0.5,
                 kappa: float = 1.5, horizon: int = 500) -> None:
        if any(isinstance(value, bool) for value in (
                quote_size, gamma, sigma, kappa)):
            raise ValueError("model parameters must be numeric, not boolean")
        gamma, sigma, kappa = float(gamma), float(sigma), float(kappa)
        if not math.isfinite(gamma) or gamma <= 0:
            raise ValueError("gamma must be finite and positive")
        if not math.isfinite(sigma) or sigma < 0:
            raise ValueError("sigma must be finite and non-negative")
        if not math.isfinite(kappa) or kappa <= 0:
            raise ValueError("kappa must be finite and positive")
        if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
            raise ValueError("horizon must be a positive integer")
        super().__init__(symbol, quote_size=quote_size)
        self.gamma = gamma
        self.sigma = sigma
        self.kappa = kappa
        self.horizon = horizon
        self._t = 0

    @property
    def time(self) -> int:
        return self._t

    @time.setter
    def time(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("time must be an integer")
        self._t = value

    def _model_parameters(self) -> tuple[float, float, float, int]:
        self._runtime_parameters()
        if any(isinstance(value, bool) for value in (
                self.gamma, self.sigma, self.kappa)):
            raise ValueError("model parameters must be numeric, not boolean")
        try:
            gamma, sigma, kappa = map(
                float, (self.gamma, self.sigma, self.kappa)
            )
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("model parameters must be numeric") from exc
        if not math.isfinite(gamma) or gamma <= 0:
            raise ValueError("gamma must be finite and positive")
        if not math.isfinite(sigma) or sigma < 0:
            raise ValueError("sigma must be finite and non-negative")
        if not math.isfinite(kappa) or kappa <= 0:
            raise ValueError("kappa must be finite and positive")
        if (isinstance(self.horizon, bool)
                or not isinstance(self.horizon, int) or self.horizon <= 0):
            raise ValueError("horizon must be a positive integer")
        return gamma, sigma, kappa, self.horizon

    def _time_left(self) -> float:
        _, _, _, horizon = self._model_parameters()
        return min(1.0, max(0.0, (horizon - self.time) / horizon))

    def reservation_price(self, mid: float) -> float:
        if isinstance(mid, bool):
            raise ValueError("mid must be numeric, not boolean")
        mid = float(mid)
        if not math.isfinite(mid) or mid <= 0:
            raise ValueError("mid must be finite and positive")
        gamma, sigma, _, _ = self._model_parameters()
        tau = self._time_left()
        if self.inventory == 0.0 or tau == 0.0:
            inventory_shift = 0.0
        else:
            inventory_shift = math.copysign(
                _stable_product(
                    abs(self.inventory), gamma, sigma, sigma, tau
                ),
                self.inventory,
            )
        reservation = mid - inventory_shift
        if not math.isfinite(reservation):
            raise OverflowError("reservation price is non-finite")
        return reservation

    def optimal_spread(self) -> float:
        gamma, sigma, kappa, _ = self._model_parameters()
        tau = self._time_left()
        ratio = gamma / kappa
        if ratio == 0.0:
            # The quotient can underflow although the risk-neutral limit is
            # finite and well defined.
            liquidity_half_spread = 1.0 / kappa
        elif math.isinf(ratio):
            # ``gamma / kappa`` can overflow while its logarithm remains
            # finite. Evaluate log(1 + gamma/kappa) in log space instead.
            log_ratio = (
                math.log(gamma)
                - math.log(kappa)
                + math.log1p(kappa / gamma)
            )
            liquidity_half_spread = log_ratio / gamma
        elif ratio < 0.5:
            # log1p(x)/x is well conditioned near zero; dividing by kappa
            # avoids losing a subnormal gamma in a second division.
            liquidity_half_spread = (math.log1p(ratio) / ratio) / kappa
        else:
            liquidity_half_spread = math.log1p(ratio) / gamma

        risk_spread = _stable_product(
            gamma, sigma, sigma, tau
        )
        spread = risk_spread + 2 * liquidity_half_spread
        if not math.isfinite(spread) or spread <= 0:
            raise OverflowError("optimal spread is non-finite or non-positive")
        return spread

    def quotes(self, book: OrderBook) -> tuple[float, float]:
        if book.mid is None:
            raise ValueError("quotes require a two-sided order book")
        r = self.reservation_price(book.mid)
        half = self.optimal_spread() / 2
        return r - half, r + half

    def on_book_update(self, book: OrderBook) -> list[Action]:
        actions = super().on_book_update(book)
        self.time += 1
        return actions
