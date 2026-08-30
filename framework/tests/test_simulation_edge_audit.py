from __future__ import annotations

from dataclasses import FrozenInstanceError
import math
import random
import sys

import pytest

from exchange.simulation import MMSimulation, _representable_add
from exchange.strategies.market_maker import MarketMaker


def _maker(**kwargs) -> MarketMaker:
    return MarketMaker(
        "SIM", half_spread=0.0, inventory_skew=0.0, **kwargs
    )


def _assert_unconsumed(simulation: MMSimulation, strategy: MarketMaker) -> None:
    assert simulation._has_run is False
    assert not hasattr(strategy, "_exchange_mm_consumed")


class _AuditRng:
    def __init__(self, uniform=1.0, gaussian=0.0):
        self.uniform = uniform
        self.gaussian = gaussian
        self.random_calls = 0
        self.gauss_scales = []

    def random(self):
        self.random_calls += 1
        return self.uniform

    def gauss(self, mean, sigma):
        self.gauss_scales.append(sigma)
        return self.gaussian


def test_representable_add_rejects_one_unit_of_large_scale_effect_loss():
    with pytest.raises(OverflowError, match="not representable"):
        _representable_add(1e16, 100000001.0, "inventory")


def test_simulation_rejects_large_scale_inventory_effect_loss_before_fill():
    class ChangingSizeMaker(MarketMaker):
        def __init__(self):
            super().__init__(
                "SIM", quote_size=1e16, half_spread=0.0, inventory_skew=0.0
            )
            self.quote_calls = 0

        def quotes(self, book):
            self.quote_calls += 1
            self.quote_size = 1e16 if self.quote_calls == 1 else 100000001.0
            bid = math.ulp(0.0) if self.quote_calls == 1 else 1.0
            return bid, sys.float_info.max

    strategy = ChangingSizeMaker()
    simulation = MMSimulation(
        strategy, sigma=0.0, steps=2, A=1e308, kappa=1.0, seed=1
    )

    with pytest.raises(OverflowError, match="inventory change is not representable"):
        simulation.run()

    assert strategy.inventory == 1e16
    assert strategy.quote_calls == 2
    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True


def test_run_configuration_is_an_immutable_normalized_snapshot():
    simulation = MMSimulation(_maker(), steps=2)
    config = simulation._validate_runtime_parameters()

    assert (config.s0, config.sigma, config.steps, config.A, config.kappa) == (
        100.0, 0.5, 2, 1.0, 1.5,
    )
    with pytest.raises(FrozenInstanceError):
        config.A = 2.0


def test_preflight_rejects_a_mid_that_cannot_support_the_next_book_atomically():
    class CountingMaker(MarketMaker):
        def __init__(self):
            super().__init__("SIM", half_spread=0.0, inventory_skew=0.0)
            self.quote_calls = 0

        def quotes(self, book):
            self.quote_calls += 1
            return super().quotes(book)

    strategy = CountingMaker()
    simulation = MMSimulation(
        strategy, s0=0.51, sigma=0.1, steps=2, A=0.0, seed=0
    )
    rng_state = simulation.rng.getstate()

    with pytest.raises(OverflowError, match="next synthetic book"):
        simulation.run()

    _assert_unconsumed(simulation, strategy)
    assert strategy.quote_calls == 0
    assert simulation.rng.getstate() == rng_state


def test_terminal_mid_only_needs_to_remain_positive():
    simulation = MMSimulation(
        _maker(), s0=0.51, sigma=0.1, steps=2, A=0.0, seed=1
    )

    result = simulation.run()

    assert result.mid == pytest.approx([
        0.5146906500335741,
        0.4606292500220579,
    ])
    assert 0.0 < result.mid[-1] <= 0.5


def test_tape_preserves_the_rng_draw_order_and_commits_its_final_state():
    seed = 17
    steps = 3
    expected_rng = random.Random(seed)
    for _ in range(steps):
        expected_rng.random()
        expected_rng.random()
        expected_rng.gauss(0.0, 0.0)

    simulation = MMSimulation(
        _maker(), sigma=0.0, steps=steps, A=0.0, seed=seed
    )
    result = simulation.run()

    assert result.mid == [100.0] * steps
    assert simulation.rng.getstate() == expected_rng.getstate()


@pytest.mark.parametrize("draw", [math.nan, -0.1, 1.1, "0.5", True])
def test_custom_rng_uniform_draws_are_validated_atomically(draw):
    strategy = _maker()
    simulation = MMSimulation(strategy, sigma=0.0, steps=1, A=0.0)
    rng = _AuditRng(uniform=draw)
    simulation.rng = rng

    with pytest.raises(ValueError, match="uniform draw"):
        simulation.run()

    _assert_unconsumed(simulation, strategy)
    assert rng.random_calls == 0
    assert rng.gauss_scales == []


@pytest.mark.parametrize("draw", [math.nan, math.inf, "0.0", True])
def test_custom_rng_gaussian_draws_are_validated_atomically(draw):
    strategy = _maker()
    simulation = MMSimulation(strategy, sigma=0.0, steps=1, A=0.0)
    rng = _AuditRng(gaussian=draw)
    simulation.rng = rng

    with pytest.raises(ValueError, match="gaussian draw"):
        simulation.run()

    _assert_unconsumed(simulation, strategy)
    assert rng.random_calls == 0
    assert rng.gauss_scales == []


def test_random_subclass_overrides_are_not_bypassed_by_fast_preflight():
    class InvalidOverride(random.Random):
        def random(self):
            return 1.1

    strategy = _maker()
    simulation = MMSimulation(strategy, sigma=0.0, steps=1, A=0.0)
    simulation.rng = InvalidOverride(42)

    with pytest.raises(ValueError, match="within \\[0, 1\\]"):
        simulation.run()

    _assert_unconsumed(simulation, strategy)


def test_preflight_rejects_an_unrepresentable_synthetic_spread_atomically():
    strategy = _maker()
    simulation = MMSimulation(
        strategy, s0=1e308, sigma=0.0, steps=1, A=0.0, seed=0
    )
    rng_state = simulation.rng.getstate()

    with pytest.raises(OverflowError, match="synthetic-book"):
        simulation.run()

    _assert_unconsumed(simulation, strategy)
    assert simulation.rng.getstate() == rng_state


@pytest.mark.parametrize(
    ("sigma", "steps", "message"),
    [
        (math.ulp(0.0), 4, "underflows to zero"),
        (0.0, 100_001, "must not exceed 100000"),
        (0.0, 10**1000, "must not exceed 100000"),
    ],
)
def test_derived_numeric_configuration_fails_before_lifecycle(
    sigma, steps, message,
):
    strategy = _maker()
    simulation = MMSimulation(strategy, sigma=0.0, steps=1, A=0.0)
    simulation.sigma = sigma
    simulation.steps = steps
    rng_state = simulation.rng.getstate()

    with pytest.raises(ValueError, match=message):
        simulation.run()

    _assert_unconsumed(simulation, strategy)
    assert simulation.rng.getstate() == rng_state


@pytest.mark.parametrize("seed", [0, 8])
def test_nonfinite_or_negative_random_path_fails_in_preflight(seed):
    strategy = _maker()
    simulation = MMSimulation(
        strategy,
        s0=1e15,
        sigma=sys.float_info.max,
        steps=1,
        A=0.0,
        seed=seed,
    )
    rng_state = simulation.rng.getstate()

    with pytest.raises((OverflowError, ValueError)):
        simulation.run()

    _assert_unconsumed(simulation, strategy)
    assert simulation.rng.getstate() == rng_state


def test_strategy_validation_cannot_rewrite_simulation_configuration():
    class MutatesDuringValidation(MarketMaker):
        armed = False

        def _runtime_parameters(self):
            values = super()._runtime_parameters()
            if self.armed:
                self.simulation.steps = 10**1000
            return values

    strategy = MutatesDuringValidation(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    strategy.simulation = simulation
    strategy.armed = True
    rng_state = simulation.rng.getstate()

    with pytest.raises(RuntimeError, match="mutated simulation configuration"):
        simulation.run()

    assert simulation.steps == 1
    _assert_unconsumed(simulation, strategy)
    assert simulation.rng.getstate() == rng_state


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("inventory", "flat finite inventory"),
        ("time", "time zero"),
    ],
)
def test_strategy_validators_cannot_preload_fresh_feedback_state(field, message):
    class PreloadsFeedbackDuringValidation(MarketMaker):
        armed = False

        def __init__(self):
            super().__init__("SIM", half_spread=0.0, inventory_skew=0.0)
            self.time = 0

        def _runtime_parameters(self):
            values = super()._runtime_parameters()
            if self.armed:
                setattr(self, field, 1.0 if field == "inventory" else 1)
            return values

    strategy = PreloadsFeedbackDuringValidation()
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    strategy.armed = True

    with pytest.raises(ValueError, match=message):
        simulation.run()

    _assert_unconsumed(simulation, strategy)


def test_strategy_validation_may_cache_benign_internal_state():
    class CachesDuringValidation(MarketMaker):
        def __init__(self):
            super().__init__("SIM", half_spread=0.0, inventory_skew=0.0)
            self.validation_calls = 0

        def _runtime_parameters(self):
            values = super()._runtime_parameters()
            self.validation_calls += 1
            return values

    strategy = CachesDuringValidation()

    result = MMSimulation(strategy, sigma=0.0, steps=1, A=0.0).run()

    assert result.mid == [100.0]
    assert strategy.validation_calls > 0


def test_strategy_validation_cannot_forge_lifecycle_markers():
    class ForgesLifecycleDuringValidation(MarketMaker):
        armed = False

        def _runtime_parameters(self):
            values = super()._runtime_parameters()
            if self.armed:
                self.simulation._has_run = True
                self._exchange_mm_consumed = True
            return values

    strategy = ForgesLifecycleDuringValidation(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    strategy.simulation = simulation
    strategy.armed = True

    with pytest.raises(RuntimeError, match="mutated simulation lifecycle state"):
        simulation.run()

    _assert_unconsumed(simulation, strategy)


def test_strategy_validation_cannot_consume_the_run_rng():
    class ConsumesRngDuringValidation(MarketMaker):
        armed = False

        def _runtime_parameters(self):
            values = super()._runtime_parameters()
            if self.armed:
                self.simulation.rng.random()
            return values

    strategy = ConsumesRngDuringValidation(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(strategy, steps=1, A=0.0, seed=17)
    strategy.simulation = simulation
    strategy.armed = True
    rng_state = simulation.rng.getstate()

    with pytest.raises(RuntimeError, match="mutated simulation random state"):
        simulation.run()

    _assert_unconsumed(simulation, strategy)
    assert simulation.rng.getstate() == rng_state


def test_strategy_validation_cannot_replace_the_root_strategy():
    class ReplacesDuringValidation(MarketMaker):
        armed = False

        def _runtime_parameters(self):
            values = super()._runtime_parameters()
            if self.armed:
                self.simulation.strategy = self.replacement
            return values

    strategy = ReplacesDuringValidation(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    replacement = _maker()
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    strategy.simulation = simulation
    strategy.replacement = replacement
    strategy.armed = True

    with pytest.raises(RuntimeError, match="replaced simulation strategy"):
        simulation.run()

    assert simulation.strategy is strategy
    _assert_unconsumed(simulation, strategy)
    assert not hasattr(replacement, "_exchange_mm_consumed")


def test_quotes_callback_cannot_rewrite_simulation_configuration():
    class MutatesInsideQuotes(MarketMaker):
        def quotes(self, book):
            quotes = super().quotes(book)
            self.simulation.steps = 0
            return quotes

    strategy = MutatesInsideQuotes(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    strategy.simulation = simulation

    with pytest.raises(RuntimeError, match="mutated simulation configuration"):
        simulation.run()

    assert simulation.steps == 1
    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True


def test_quotes_callback_cannot_replace_the_root_strategy():
    class ReplacesInsideQuotes(MarketMaker):
        def quotes(self, book):
            quotes = super().quotes(book)
            self.simulation.strategy = self.replacement
            return quotes

    strategy = ReplacesInsideQuotes(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    replacement = _maker()
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    strategy.simulation = simulation
    strategy.replacement = replacement

    with pytest.raises(RuntimeError, match="replaced simulation strategy"):
        simulation.run()

    assert simulation.strategy is strategy
    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True
    assert not hasattr(replacement, "_exchange_mm_consumed")


def test_quotes_callback_cannot_replace_the_run_rng():
    class ReplacesRngInsideQuotes(MarketMaker):
        def quotes(self, book):
            quotes = super().quotes(book)
            self.simulation.rng = random.Random(999)
            return quotes

    strategy = ReplacesRngInsideQuotes(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    original_rng = simulation.rng
    strategy.simulation = simulation

    with pytest.raises(RuntimeError, match="replaced simulation random generator"):
        simulation.run()

    assert simulation.rng is original_rng
    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True


def test_quotes_callback_cannot_consume_the_committed_run_rng():
    class ConsumesRngInsideQuotes(MarketMaker):
        def quotes(self, book):
            quotes = super().quotes(book)
            self.simulation.rng.random()
            return quotes

    seed = 17
    expected_rng = random.Random(seed)
    expected_rng.random()
    expected_rng.random()
    expected_rng.gauss(0.0, 0.0)
    strategy = ConsumesRngInsideQuotes(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(
        strategy, sigma=0.0, steps=1, A=0.0, seed=seed
    )
    strategy.simulation = simulation

    with pytest.raises(RuntimeError, match="mutated simulation random state"):
        simulation.run()

    assert simulation.rng.getstate() == expected_rng.getstate()
    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True


def test_quotes_callback_cannot_mutate_custom_rng_attributes():
    class ConsumesTeachingRngInsideQuotes(MarketMaker):
        def quotes(self, book):
            quotes = super().quotes(book)
            self.simulation.rng.gauss(0.0, 99.0)
            return quotes

    strategy = ConsumesTeachingRngInsideQuotes(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(strategy, sigma=0.0, steps=1, A=0.0)
    rng = _AuditRng()
    simulation.rng = rng
    strategy.simulation = simulation

    with pytest.raises(RuntimeError, match="mutated simulation random state"):
        simulation.run()

    assert rng.gauss_scales == [0.0]
    assert rng.random_calls == 2
    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True


def test_quotes_callback_cannot_clear_committed_lifecycle_markers():
    class ClearsLifecycleInsideQuotes(MarketMaker):
        def quotes(self, book):
            quotes = super().quotes(book)
            self.simulation._has_run = False
            del self._exchange_mm_consumed
            return quotes

    strategy = ClearsLifecycleInsideQuotes(
        "SIM", half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(strategy, steps=1, A=0.0)
    strategy.simulation = simulation

    with pytest.raises(RuntimeError, match="mutated simulation lifecycle state"):
        simulation.run()

    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True


def test_fill_callback_cannot_silently_change_arrival_configuration():
    class MutatesOnFill(MarketMaker):
        def on_fill(self, fill):
            super().on_fill(fill)
            self.simulation.A = 0.0

    strategy = MutatesOnFill(
        "SIM", quote_size=1.0, half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(
        strategy, sigma=0.0, steps=1, A=1e308, kappa=0.0, seed=1
    )
    strategy.simulation = simulation

    with pytest.raises(RuntimeError, match="mutated simulation configuration"):
        simulation.run()

    assert simulation.A == 1e308
    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True


def test_fill_callback_cannot_clear_committed_lifecycle_markers():
    class ClearsLifecycleOnFill(MarketMaker):
        def on_fill(self, fill):
            super().on_fill(fill)
            self.simulation._has_run = False
            del self._exchange_mm_consumed

    strategy = ClearsLifecycleOnFill(
        "SIM", quote_size=1.0, half_spread=0.0, inventory_skew=0.0
    )
    simulation = MMSimulation(
        strategy, sigma=0.0, steps=1, A=1e308, kappa=0.0, seed=1
    )
    strategy.simulation = simulation

    with pytest.raises(RuntimeError, match="mutated simulation lifecycle state"):
        simulation.run()

    assert simulation._has_run is True
    assert strategy._exchange_mm_consumed is True
