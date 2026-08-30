"""Contrato dimensional y límites de Avellaneda–Stoikov y su simulación."""

import math
import sys

import pytest

from exchange.simulation import MMSimulation
from exchange.strategies import AvellanedaStoikov, MarketMaker


@pytest.mark.parametrize("bad", [True, False])
def test_as_rejects_boolean_model_parameters_and_state(bad):
    for field in ("quote_size", "gamma", "sigma", "kappa"):
        with pytest.raises(ValueError, match="boolean"):
            AvellanedaStoikov("SIM", horizon=10, **{field: bad})
    maker = AvellanedaStoikov("SIM", horizon=10)
    with pytest.raises(ValueError, match="integer"):
        maker.time = bad
    with pytest.raises(ValueError, match="boolean"):
        maker.reservation_price(bad)


@pytest.mark.parametrize("bad", [1.5, math.nan, math.inf, -math.inf])
def test_as_time_rejects_non_integer_values_instead_of_truncating(bad):
    maker = AvellanedaStoikov("SIM", horizon=10)
    with pytest.raises(ValueError, match="integer"):
        maker.time = bad


@pytest.mark.parametrize(
    "field,bad",
    [
        ("gamma", True),
        ("gamma", math.nan),
        ("sigma", True),
        ("sigma", math.inf),
        ("kappa", True),
        ("kappa", 0.0),
        ("horizon", True),
        ("horizon", 0),
    ],
)
def test_as_revalidates_mutable_public_configuration(field, bad):
    maker = AvellanedaStoikov("SIM", horizon=10)
    setattr(maker, field, bad)
    with pytest.raises(ValueError):
        maker.optimal_spread()


def test_remaining_variance_has_one_dimensional_convention():
    """sigma_H**2 * tau es la varianza restante que consumen r y d."""
    mm = AvellanedaStoikov("SIM", gamma=0.2, sigma=3.0,
                           kappa=0.4, horizon=100)
    mm.inventory = 2.0
    mm.time = 25

    tau = 0.75
    remaining_variance = 3.0**2 * tau
    liquidity_spread = (2 / 0.2) * math.log1p(0.2 / 0.4)

    assert mm.reservation_price(100.0) == pytest.approx(
        100.0 - 2.0 * 0.2 * remaining_variance
    )
    assert mm.optimal_spread() == pytest.approx(
        0.2 * remaining_variance + liquidity_spread
    )


def test_formula_is_invariant_to_time_grid_at_equal_normalized_time():
    coarse = AvellanedaStoikov("SIM", gamma=0.3, sigma=1.2,
                               kappa=1.1, horizon=100)
    fine = AvellanedaStoikov("SIM", gamma=0.3, sigma=1.2,
                             kappa=1.1, horizon=400)
    for mm, time in ((coarse, 25), (fine, 100)):
        mm.inventory = 1.5
        mm.time = time

    assert coarse.reservation_price(50.0) == pytest.approx(
        fine.reservation_price(50.0)
    )
    assert coarse.optimal_spread() == pytest.approx(fine.optimal_spread())


def test_time_is_clipped_and_terminal_risk_term_switches_off():
    mm = AvellanedaStoikov("SIM", gamma=0.5, sigma=2.0,
                           kappa=1.5, horizon=100)
    mm.inventory = 1.0

    mm.time = -10
    assert mm.reservation_price(100.0) == pytest.approx(98.0)

    mm.time = 150
    terminal_spread = (2 / mm.gamma) * math.log1p(mm.gamma / mm.kappa)
    assert mm.reservation_price(100.0) == pytest.approx(100.0)
    assert mm.optimal_spread() == pytest.approx(terminal_spread)


def test_risk_neutral_spread_limit_is_two_over_kappa():
    gamma = 1e-10
    kappa = 1.5
    mm = AvellanedaStoikov("SIM", gamma=gamma, sigma=0.0,
                           kappa=kappa, horizon=10)
    assert mm.optimal_spread() == pytest.approx(2 / kappa, rel=1e-10)


def test_tiny_positive_gamma_uses_the_finite_risk_neutral_limit():
    mm = AvellanedaStoikov("SIM", gamma=1e-309, sigma=0.0,
                           kappa=1.5, horizon=10)
    assert math.isfinite(mm.optimal_spread())
    assert mm.optimal_spread() == pytest.approx(2 / 1.5, rel=1e-12)


def test_liquidity_term_handles_overflowing_and_underflowing_ratios():
    smallest = math.ulp(0.0)

    overflowing_ratio = AvellanedaStoikov(
        "SIM", gamma=1.0, sigma=0.0, kappa=smallest, horizon=10
    )
    assert overflowing_ratio.optimal_spread() == pytest.approx(
        -2.0 * math.log(smallest), rel=1e-12
    )

    underflowing_ratio = AvellanedaStoikov(
        "SIM", gamma=smallest, sigma=0.0,
        kappa=sys.float_info.max, horizon=10,
    )
    spread = underflowing_ratio.optimal_spread()
    assert math.isfinite(spread) and spread > 0.0
    assert math.isclose(
        spread, 2.0 / sys.float_info.max, rel_tol=1e-12, abs_tol=0.0
    )


class _RecordingRng:
    def __init__(self):
        self.gauss_scales = []

    def random(self):
        return 1.0  # ``random < fill_probability`` is false, even at probability 1.

    def gauss(self, mean, sigma):
        assert mean == 0
        self.gauss_scales.append(sigma)
        return 0.0


def test_simulation_scales_each_increment_by_sqrt_horizon():
    sim = MMSimulation(MarketMaker("SIM"), sigma=2.0, steps=16)
    recorder = _RecordingRng()
    sim.rng = recorder

    sim.run()

    assert recorder.gauss_scales == pytest.approx([0.5] * 16)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"gamma": 0.0}, "gamma"),
        ({"gamma": math.nan}, "gamma"),
        ({"sigma": -0.1}, "sigma"),
        ({"sigma": math.inf}, "sigma"),
        ({"kappa": 0.0}, "kappa"),
        ({"kappa": math.nan}, "kappa"),
        ({"horizon": 0}, "horizon"),
    ],
)
def test_as_rejects_parameters_outside_model_domain(kwargs, message):
    with pytest.raises(ValueError, match=message):
        AvellanedaStoikov("SIM", **kwargs)


def test_simulation_rejects_invalid_horizon_volatility_contract():
    strategy = MarketMaker("SIM")
    with pytest.raises(ValueError, match="sigma"):
        MMSimulation(strategy, sigma=-0.1)
    with pytest.raises(ValueError, match="steps"):
        MMSimulation(strategy, steps=0)
    with pytest.raises(ValueError, match="sigma"):
        MMSimulation(strategy, sigma=math.nan)


@pytest.mark.parametrize(
    ("strategy_kwargs", "simulation_kwargs", "message"),
    [
        ({"horizon": 10}, {"steps": 40}, "horizon"),
        ({"horizon": 10, "sigma": 2.0}, {"steps": 10, "sigma": 0.5}, "sigma"),
        ({"horizon": 10, "kappa": 0.4}, {"steps": 10, "kappa": 1.5}, "kappa"),
    ],
)
def test_as_simulation_requires_one_shared_model_contract(
    strategy_kwargs, simulation_kwargs, message,
):
    strategy = AvellanedaStoikov("SIM", **strategy_kwargs)
    with pytest.raises(ValueError, match=message):
        MMSimulation(strategy, **simulation_kwargs).run()
