"""simulation.py — simulador de market making.

Construido en L13. El backtest de replay (market.py, L9) sirve para ejecución
(VWAP cruza market orders y siempre llena). Pero un market maker pone órdenes
límite y necesita un modelo de *cuándo le ejecutan*: cuanto más cerca del mid
cotiza, más probable es que le golpeen.

Modelo mínimo de llegada: la intensidad de órdenes a distancia `delta` del mid
es lambda(delta) = A * exp(-kappa * delta). L13 usa esta intuición para preparar
el parámetro kappa; L14 reutiliza el mismo entorno sin exponer su clase antes de
tiempo. El mid sigue un paseo aleatorio. ``sigma`` es la desviación típica del
cambio de precio durante la simulación completa; cada incremento usa
``sigma / sqrt(steps)`` para conservar esa volatilidad al cambiar la malla.
"""

from __future__ import annotations

import copy
from fractions import Fraction
import math
from numbers import Real
import random
from dataclasses import dataclass, field

from exchange.book import Level, OrderBook
from exchange.orders import Side
from exchange.strategies.market_maker import MarketMaker


_EFFECT_FIDELITY_DENOMINATOR = 10**12
_STOCHASTIC_ROUNDOFF_REL_TOL = 1e-8
# Preflight keeps one deterministic event per tick.  The course uses 500;
# this ceiling leaves ample room for experiments while bounding tape memory.
_MAX_SIMULATION_STEPS = 100_000
_SYNTHETIC_BOOK_HALF_SPREAD = 0.5


def _representable_add(current: float, delta: float, label: str) -> float:
    """Add a non-authoritative float delta without silently distorting it."""
    result = current + delta
    if not math.isfinite(result):
        raise OverflowError(f"simulation {label} would become non-finite")
    if delta == 0.0:
        faithful = result == current
    else:
        actual_exact = Fraction.from_float(result) - Fraction.from_float(current)
        expected_exact = Fraction.from_float(delta)
        faithful = (
            actual_exact != 0
            and (actual_exact > 0) == (expected_exact > 0)
            and abs(actual_exact - expected_exact)
            * _EFFECT_FIDELITY_DENOMINATOR
            <= abs(expected_exact)
        )
    if not faithful:
        raise OverflowError(f"simulation {label} change is not representable")
    return result


def _stochastic_add(current: float, delta: float) -> float:
    """Advance the non-authoritative random walk without swallowing a shock."""
    result = current + delta
    if not math.isfinite(result):
        raise OverflowError("simulation mid-price would become non-finite")
    if not math.isclose(
        result - current,
        delta,
        rel_tol=_STOCHASTIC_ROUNDOFF_REL_TOL,
        abs_tol=0.0,
    ):
        raise OverflowError("simulation mid-price change is not representable")
    return result


def _validated_uniform_draw(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"simulation {label} must be a real number, not boolean")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"simulation {label} must be finite and within [0, 1]")
    return value


def _validated_gaussian_draw(value) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(
            "simulation gaussian draw must be a real number, not boolean"
        )
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("simulation gaussian draw must be finite")
    return value


@dataclass(frozen=True)
class _RunConfig:
    """Validated scalar configuration frozen for one simulation run."""

    s0: float
    sigma: float
    steps: int
    steps_float: float
    A: float
    kappa: float
    step_sigma: float


@dataclass(frozen=True)
class _RunEvent:
    """One prevalidated stochastic tick and its synthetic-book endpoints."""

    book_bid: float
    book_ask: float
    bid_draw: float
    ask_draw: float
    price_change: float
    next_mid: float


@dataclass(frozen=True)
class _LifecycleCheckpoint:
    """Exact ownership markers expected around strategy-owned code."""

    has_run: bool
    marker_present: bool
    marker_value: object = None


@dataclass(frozen=True)
class _RngAttributeCheckpoint:
    """Identity-preserving snapshot of one explicit custom-RNG attribute."""

    name: str
    kind: str
    original: object
    snapshot: object


@dataclass(frozen=True)
class _RngCheckpoint:
    """Recoverable state for the run RNG around strategy-owned code."""

    has_state: bool
    state: object = None
    attributes: tuple[_RngAttributeCheckpoint, ...] = ()


@dataclass
class SimResult:
    mid: list[float] = field(default_factory=list)
    inventory: list[float] = field(default_factory=list)
    pnl: list[float] = field(default_factory=list)
    n_fills: int = 0
    _peak_inventory: float = field(default=0.0, repr=False)

    @property
    def final_pnl(self) -> float:
        return self.pnl[-1] if self.pnl else 0.0

    @property
    def max_inventory(self) -> float:
        return max(self._peak_inventory,
                   max((abs(q) for q in self.inventory), default=0.0))


class MMSimulation:
    """Simula un market maker contra un mid que hace un paseo aleatorio.

    ``sigma`` mide volatilidad de precio por horizonte completo (los ``steps``
    de esta ejecución), no volatilidad por paso. Así, si ``Z ~ N(0, 1)``, cada
    incremento es ``delta_S = sigma / sqrt(steps) * Z`` y la varianza terminal
    del paseo es ``sigma**2`` con independencia de la discretización. ``s0``
    debe superar el semispread de 0.5 del libro sintético para que su bid sea
    estrictamente positivo desde el primer paso. ``steps`` está limitado a
    100 000 porque el preflight conserva una cinta determinista por paso.
    """

    def __init__(self, strategy: MarketMaker, s0: float = 100.0, sigma: float = 0.5,
                 steps: int = 500, A: float = 1.0, kappa: float = 1.5,
                 seed: int = 42) -> None:
        if any(isinstance(value, bool) for value in (s0, sigma, A, kappa)):
            raise ValueError("simulation parameters must be numeric, not boolean")
        s0, sigma, A, kappa = map(float, (s0, sigma, A, kappa))
        if not math.isfinite(s0) or s0 <= _SYNTHETIC_BOOK_HALF_SPREAD:
            raise ValueError(
                "s0 must be finite and greater than the synthetic-book "
                f"half-spread ({_SYNTHETIC_BOOK_HALF_SPREAD})"
            )
        if not math.isfinite(sigma) or sigma < 0:
            raise ValueError("sigma must be finite and non-negative")
        if isinstance(steps, bool) or not isinstance(steps, int) or steps <= 0:
            raise ValueError("steps must be a positive integer")
        if steps > _MAX_SIMULATION_STEPS:
            raise ValueError(
                f"steps must not exceed {_MAX_SIMULATION_STEPS}"
            )
        if not math.isfinite(A) or A < 0:
            raise ValueError("A must be finite and non-negative")
        if not math.isfinite(kappa) or kappa < 0:
            raise ValueError("kappa must be finite and non-negative")
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("seed must be an integer")
        self.strategy = strategy
        self.s0 = s0
        self.sigma = sigma
        self.steps = steps
        self.A = A          # intensidad base de llegada de órdenes
        self.kappa = kappa  # cómo cae la intensidad con la distancia al mid
        self.rng = random.Random(seed)
        self._has_run = False

    def _validate_runtime_parameters(self) -> _RunConfig:
        if any(isinstance(value, bool) for value in (
                self.s0, self.sigma, self.A, self.kappa)):
            raise ValueError("simulation parameters must be numeric, not boolean")
        try:
            s0, sigma, A, kappa = map(
                float, (self.s0, self.sigma, self.A, self.kappa)
            )
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("simulation parameters must be numeric") from exc
        if not math.isfinite(s0) or s0 <= _SYNTHETIC_BOOK_HALF_SPREAD:
            raise ValueError(
                "s0 must be finite and greater than the synthetic-book "
                f"half-spread ({_SYNTHETIC_BOOK_HALF_SPREAD})"
            )
        if not math.isfinite(sigma) or sigma < 0:
            raise ValueError("sigma must be finite and non-negative")
        if (isinstance(self.steps, bool) or not isinstance(self.steps, int)
                or self.steps <= 0):
            raise ValueError("steps must be a positive integer")
        if self.steps > _MAX_SIMULATION_STEPS:
            raise ValueError(
                f"steps must not exceed {_MAX_SIMULATION_STEPS}"
            )
        if not math.isfinite(A) or A < 0:
            raise ValueError("A must be finite and non-negative")
        if not math.isfinite(kappa) or kappa < 0:
            raise ValueError("kappa must be finite and non-negative")
        try:
            steps_float = float(self.steps)
        except OverflowError as exc:
            raise ValueError("steps is too large for simulation arithmetic") from exc
        if not math.isfinite(steps_float):
            raise ValueError("steps is too large for simulation arithmetic")
        step_sigma = sigma / math.sqrt(steps_float)
        if not math.isfinite(step_sigma):
            raise ValueError("per-step volatility must stay finite")
        if sigma > 0.0 and step_sigma == 0.0:
            raise ValueError("per-step volatility underflows to zero")

        steps = int(self.steps)
        self.s0, self.sigma = s0, sigma
        self.steps = steps
        self.A, self.kappa = A, kappa
        return _RunConfig(
            s0=s0,
            sigma=sigma,
            steps=steps,
            steps_float=steps_float,
            A=A,
            kappa=kappa,
            step_sigma=step_sigma,
        )

    def _configuration_matches(self, config: _RunConfig) -> bool:
        """Whether callbacks left the normalized public configuration alone."""
        try:
            return (
                type(self.s0) is float and self.s0 == config.s0
                and type(self.sigma) is float and self.sigma == config.sigma
                and type(self.steps) is int and self.steps == config.steps
                and type(self.A) is float and self.A == config.A
                and type(self.kappa) is float and self.kappa == config.kappa
            )
        except Exception:
            return False

    def _restore_configuration(self, config: _RunConfig) -> None:
        self.s0 = config.s0
        self.sigma = config.sigma
        self.steps = config.steps
        self.A = config.A
        self.kappa = config.kappa

    @staticmethod
    def _rng_checkpoint(rng) -> _RngCheckpoint:
        getstate = getattr(rng, "getstate", None)
        setstate = getattr(rng, "setstate", None)
        has_state = callable(getstate) and callable(setstate)
        inspect_attributes = type(rng) is not random.Random and hasattr(
            rng, "__dict__"
        )
        try:
            state = copy.deepcopy(getstate()) if has_state else None
            # Exact ``Random`` keeps all state in getstate().  Subclasses and
            # teaching RNGs may keep override counters in ``__dict__`` too.
            attributes = tuple(
                _RngAttributeCheckpoint(
                    name=name,
                    kind=(
                        "list" if isinstance(value, list)
                        else "dict" if isinstance(value, dict)
                        else "set" if isinstance(value, set)
                        else "bytearray" if isinstance(value, bytearray)
                        else "value"
                    ),
                    original=value,
                    snapshot=copy.deepcopy(value),
                )
                for name, value in vars(rng).items()
            ) if inspect_attributes else ()
        except Exception as exc:
            raise ValueError(
                "simulation rng state must support an isolated checkpoint"
            ) from exc
        if not has_state and not inspect_attributes:
            raise ValueError(
                "simulation rng must expose recoverable state"
            )
        return _RngCheckpoint(
            has_state=has_state,
            state=state,
            attributes=attributes,
        )

    @staticmethod
    def _rng_matches(rng, checkpoint: _RngCheckpoint) -> bool:
        try:
            if checkpoint.has_state and rng.getstate() != checkpoint.state:
                return False
            if type(rng) is not random.Random and hasattr(rng, "__dict__"):
                observed = vars(rng)
                if set(observed) != {
                    attribute.name for attribute in checkpoint.attributes
                }:
                    return False
                for attribute in checkpoint.attributes:
                    value = observed[attribute.name]
                    if value is not attribute.original:
                        return False
                    if type(value) is not type(attribute.snapshot):
                        return False
                    if value != attribute.snapshot:
                        return False
            return True
        except Exception:
            return False

    @staticmethod
    def _restore_rng(rng, checkpoint: _RngCheckpoint) -> None:
        if checkpoint.has_state:
            rng.setstate(copy.deepcopy(checkpoint.state))
        if type(rng) is random.Random or not hasattr(rng, "__dict__"):
            return

        observed = vars(rng)
        expected_names = {
            attribute.name for attribute in checkpoint.attributes
        }
        for name in tuple(observed):
            if name not in expected_names:
                del observed[name]

        for attribute in checkpoint.attributes:
            original = attribute.original
            snapshot = copy.deepcopy(attribute.snapshot)
            if attribute.kind == "list":
                original.clear()
                original.extend(snapshot)
            elif attribute.kind == "dict":
                original.clear()
                original.update(snapshot)
            elif attribute.kind == "set":
                original.clear()
                original.update(snapshot)
            elif attribute.kind == "bytearray":
                original[:] = snapshot
            observed[attribute.name] = original

    @staticmethod
    def _lifecycle_checkpoint(strategy, has_run: bool) -> _LifecycleCheckpoint:
        marker_present = hasattr(strategy, "_exchange_mm_consumed")
        marker_value = (
            getattr(strategy, "_exchange_mm_consumed")
            if marker_present else None
        )
        return _LifecycleCheckpoint(has_run, marker_present, marker_value)

    def _lifecycle_matches(
        self, strategy, lifecycle: _LifecycleCheckpoint
    ) -> bool:
        if type(self._has_run) is not bool or self._has_run != lifecycle.has_run:
            return False
        marker_present = hasattr(strategy, "_exchange_mm_consumed")
        if marker_present != lifecycle.marker_present:
            return False
        if not marker_present:
            return True
        try:
            observed = getattr(strategy, "_exchange_mm_consumed")
            return (
                type(observed) is type(lifecycle.marker_value)
                and observed == lifecycle.marker_value
            )
        except Exception:
            return False

    def _restore_lifecycle(
        self, strategy, lifecycle: _LifecycleCheckpoint
    ) -> None:
        self._has_run = lifecycle.has_run
        marker_present = hasattr(strategy, "_exchange_mm_consumed")
        if lifecycle.marker_present:
            setattr(strategy, "_exchange_mm_consumed", lifecycle.marker_value)
        elif marker_present:
            delattr(strategy, "_exchange_mm_consumed")

    def _guard_violation(
        self,
        config: _RunConfig,
        strategy,
        rng,
        rng_checkpoint: _RngCheckpoint,
        lifecycle: _LifecycleCheckpoint,
    ) -> str | None:
        if self.strategy is not strategy:
            return "strategy callback replaced simulation strategy"
        if self.rng is not rng:
            return "strategy callback replaced simulation random generator"
        if not self._rng_matches(rng, rng_checkpoint):
            return "strategy callback mutated simulation random state"
        if not self._configuration_matches(config):
            return "strategy callback mutated simulation configuration"
        if not self._lifecycle_matches(strategy, lifecycle):
            return "strategy callback mutated simulation lifecycle state"
        return None

    def _restore_guarded_roots(
        self,
        config: _RunConfig,
        strategy,
        rng,
        rng_checkpoint: _RngCheckpoint,
        lifecycle: _LifecycleCheckpoint,
    ) -> None:
        self.strategy = strategy
        self.rng = rng
        self._restore_rng(rng, rng_checkpoint)
        self._restore_configuration(config)
        self._restore_lifecycle(strategy, lifecycle)

    def _assert_guard_intact(
        self,
        config: _RunConfig,
        strategy,
        rng,
        rng_checkpoint: _RngCheckpoint,
        lifecycle: _LifecycleCheckpoint,
    ) -> None:
        violation = self._guard_violation(
            config, strategy, rng, rng_checkpoint, lifecycle
        )
        if violation is not None:
            self._restore_guarded_roots(
                config, strategy, rng, rng_checkpoint, lifecycle
            )
            raise RuntimeError(violation)

    def _invoke_with_configuration_guard(
        self,
        config: _RunConfig,
        strategy,
        rng,
        rng_checkpoint: _RngCheckpoint,
        lifecycle: _LifecycleCheckpoint,
        callback,
        *args,
    ):
        """Invoke strategy-owned code without letting it rewrite this run."""
        try:
            outcome = callback(*args)
        except Exception as exc:
            violation = self._guard_violation(
                config, strategy, rng, rng_checkpoint, lifecycle
            )
            if violation is not None:
                self._restore_guarded_roots(
                    config, strategy, rng, rng_checkpoint, lifecycle
                )
                raise RuntimeError(violation) from exc
            raise
        self._assert_guard_intact(
            config, strategy, rng, rng_checkpoint, lifecycle
        )
        return outcome

    @staticmethod
    def _synthetic_book_prices(mid: float) -> tuple[float, float]:
        bid = _representable_add(
            mid, -_SYNTHETIC_BOOK_HALF_SPREAD, "synthetic-book bid"
        )
        ask = _representable_add(
            mid, _SYNTHETIC_BOOK_HALF_SPREAD, "synthetic-book ask"
        )
        if bid <= 0.0:
            raise OverflowError(
                "simulated mid cannot support a positive synthetic-book bid"
            )
        return bid, ask

    def _preflight_tape(
        self, config: _RunConfig
    ) -> tuple[tuple[_RunEvent, ...], object | None, object]:
        """Build the deterministic path without advancing the owned RNG."""
        rng = self.rng
        if not callable(getattr(rng, "random", None)) or not callable(
            getattr(rng, "gauss", None)
        ):
            raise ValueError("simulation rng must provide random() and gauss()")
        if type(rng) is random.Random:
            rng_start_state = rng.getstate()
            preview_rng = random.Random()
            preview_rng.setstate(rng_start_state)
            custom_checkpoint = None
        else:
            custom_checkpoint = self._rng_checkpoint(rng)
            preview_rng = rng
        mid = config.s0
        events: list[_RunEvent] = []

        try:
            for index in range(config.steps):
                book_bid, book_ask = self._synthetic_book_prices(mid)
                bid_draw = _validated_uniform_draw(
                    preview_rng.random(), "bid uniform draw"
                )
                ask_draw = _validated_uniform_draw(
                    preview_rng.random(), "ask uniform draw"
                )
                price_change = _validated_gaussian_draw(
                    preview_rng.gauss(0.0, config.step_sigma)
                )
                next_mid = _stochastic_add(mid, price_change)
                if next_mid <= 0.0:
                    raise OverflowError(
                        "simulated mid must stay finite and positive"
                    )
                if (index + 1 < config.steps
                        and next_mid <= _SYNTHETIC_BOOK_HALF_SPREAD):
                    raise OverflowError(
                        "simulated mid cannot support the next synthetic book"
                    )
                events.append(_RunEvent(
                    book_bid=book_bid,
                    book_ask=book_ask,
                    bid_draw=bid_draw,
                    ask_draw=ask_draw,
                    price_change=price_change,
                    next_mid=next_mid,
                ))
                mid = next_mid
            rng_final_state = (
                preview_rng.getstate() if type(rng) is random.Random else None
            )
        finally:
            if custom_checkpoint is not None:
                self._restore_rng(rng, custom_checkpoint)
        return tuple(events), rng_final_state, rng

    @staticmethod
    def _commit_custom_rng(
        rng, tape: tuple[_RunEvent, ...], config: _RunConfig
    ) -> None:
        """Advance an injectable teaching RNG only after lifecycle commit."""
        for event in tape:
            observed = (
                _validated_uniform_draw(rng.random(), "bid uniform draw"),
                _validated_uniform_draw(rng.random(), "ask uniform draw"),
                _validated_gaussian_draw(
                    rng.gauss(0.0, config.step_sigma)
                ),
            )
            if observed != (
                event.bid_draw, event.ask_draw, event.price_change
            ):
                raise RuntimeError("simulation rng changed after preflight")

    def _assert_inventory_sync(self, expected: float, strategy=None) -> None:
        strategy = self.strategy if strategy is None else strategy
        if isinstance(strategy.inventory, bool):
            raise RuntimeError("strategy inventory is not a finite number")
        try:
            observed = float(strategy.inventory)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RuntimeError("strategy inventory is not a finite number") from exc
        if not math.isfinite(observed) or observed != expected:
            raise RuntimeError(
                "strategy must keep inventory synchronized with the simulation ledger"
            )

    def _assert_model_contract(self, config: _RunConfig, strategy=None) -> None:
        strategy = self.strategy if strategy is None else strategy
        # L14 teaches one horizon-level sigma and one arrival kappa. Letting the
        # strategy and simulator silently use different values changes the model.
        # The marker avoids importing the L14 class from the L13 package snapshot.
        if getattr(strategy, "simulation_contract", None) == "sigma-horizon-kappa":
            if strategy.horizon != config.steps:
                raise ValueError("AvellanedaStoikov horizon must equal simulation steps")
            if strategy.sigma != config.sigma:
                raise ValueError("strategy sigma must equal simulation sigma")
            if strategy.kappa != config.kappa:
                raise ValueError("strategy kappa must equal simulation kappa")

    @staticmethod
    def _fill_probability(delta: float, config: _RunConfig) -> float:
        """Prob. de que una cotización a distancia `delta` del mid se ejecute."""
        if not math.isfinite(delta):
            raise ValueError("quote distance must be finite")
        if delta < 0:                       # cotización marketable -> seguro
            return 1.0
        # ``A * exp(-kappa*delta)`` is an arrival intensity per full horizon.
        # Convert it to the probability of at least one arrival in one of the
        # ``steps`` intervals, keeping behavior stable when the grid changes.
        intensity = config.A * math.exp(-config.kappa * delta)
        return -math.expm1(-intensity / config.steps_float)

    def _fill_prob(self, delta: float) -> float:
        """Compatibility helper using a freshly validated public config."""
        return self._fill_probability(delta, self._validate_runtime_parameters())

    def run(self) -> SimResult:
        """Run once from a fresh, flat strategy state.

        A simulation owns one stochastic lifecycle. Reusing it, or supplying a
        strategy with preloaded inventory/time, would desynchronise the local
        cash ledger from the strategy feedback state, so both cases fail closed.
        """
        config = self._validate_runtime_parameters()
        if self._has_run:
            raise RuntimeError("MMSimulation instances are single-use")
        strategy = self.strategy
        if getattr(strategy, "_exchange_mm_consumed", False):
            raise ValueError("strategy instance has already been consumed by MMSimulation")
        tape, rng_final_state, rng = self._preflight_tape(config)
        pre_rng_checkpoint = self._rng_checkpoint(rng)
        pre_lifecycle = self._lifecycle_checkpoint(strategy, self._has_run)

        def assert_fresh_strategy_state() -> None:
            try:
                initial_inventory = float(strategy.inventory)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    "strategy must start with flat finite inventory"
                ) from exc
            if not math.isfinite(initial_inventory) or initial_inventory != 0.0:
                raise ValueError("strategy must start with flat finite inventory")
            if hasattr(strategy, "time") and strategy.time != 0:
                raise ValueError("strategy must start at time zero")

        def validate_fresh_strategy() -> None:
            assert_fresh_strategy_state()
            validate_strategy = getattr(strategy, "_runtime_parameters", None)
            if callable(validate_strategy):
                validate_strategy()
            validate_model = getattr(strategy, "_model_parameters", None)
            if callable(validate_model):
                validate_model()
            self._assert_model_contract(config, strategy)
            # Runtime/model validators are strategy-owned extension points.
            # They may cache benign internal data, but must not preload the
            # feedback state after the first freshness check.
            assert_fresh_strategy_state()

        self._invoke_with_configuration_guard(
            config,
            strategy,
            rng,
            pre_rng_checkpoint,
            pre_lifecycle,
            validate_fresh_strategy,
        )
        self._has_run = True
        setattr(strategy, "_exchange_mm_consumed", True)
        committed_lifecycle = self._lifecycle_checkpoint(
            strategy, self._has_run
        )
        if rng_final_state is not None:
            rng.setstate(rng_final_state)
        else:
            self._commit_custom_rng(rng, tape, config)
        committed_rng_checkpoint = self._rng_checkpoint(rng)
        mid = config.s0
        cash, inventory = 0.0, 0.0
        res = SimResult()
        self._assert_inventory_sync(inventory, strategy)

        for event in tape:
            self._assert_inventory_sync(inventory, strategy)
            # libro mínimo de un nivel a cada lado, centrado en el mid actual
            book = OrderBook(strategy.symbol,
                             [Level(event.book_bid, 1.0)],
                             [Level(event.book_ask, 1.0)])
            bid_px, ask_px = self._invoke_with_configuration_guard(
                config,
                strategy,
                rng,
                committed_rng_checkpoint,
                committed_lifecycle,
                strategy.quotes,
                book,
            )
            self._assert_inventory_sync(inventory, strategy)
            if isinstance(bid_px, bool) or isinstance(ask_px, bool):
                raise ValueError("strategy quotes must be numeric, not boolean")
            bid_px, ask_px = float(bid_px), float(ask_px)
            if not all(math.isfinite(px) and px > 0 for px in (bid_px, ask_px)):
                raise ValueError("strategy quotes must be finite and positive")
            if bid_px > ask_px:
                raise ValueError("strategy bid quote cannot exceed ask quote")
            if isinstance(strategy.quote_size, bool):
                raise ValueError("strategy quote_size must be numeric, not boolean")
            quote_size = float(strategy.quote_size)
            if not math.isfinite(quote_size) or quote_size <= 0:
                raise ValueError("strategy quote_size must be finite and positive")

            # ¿nos golpean el bid? (alguien vende contra nuestra compra)
            if event.bid_draw < self._fill_probability(mid - bid_px, config):
                notional = bid_px * quote_size
                if not math.isfinite(notional) or notional == 0.0:
                    raise OverflowError("simulation fill notional is not representable")
                next_cash = _representable_add(cash, -notional, "cash")
                next_inventory = _representable_add(
                    inventory, quote_size, "inventory"
                )
                self._invoke_with_configuration_guard(
                    config,
                    strategy,
                    rng,
                    committed_rng_checkpoint,
                    committed_lifecycle,
                    strategy.on_fill,
                    _hit(strategy.symbol, Side.BUY, bid_px, quote_size),
                )
                self._assert_inventory_sync(next_inventory, strategy)
                cash, inventory = next_cash, next_inventory
                res._peak_inventory = max(res._peak_inventory, abs(inventory))
                res.n_fills += 1
            # ¿nos golpean el ask? (alguien compra contra nuestra venta)
            if event.ask_draw < self._fill_probability(ask_px - mid, config):
                notional = ask_px * quote_size
                if not math.isfinite(notional) or notional == 0.0:
                    raise OverflowError("simulation fill notional is not representable")
                next_cash = _representable_add(cash, notional, "cash")
                next_inventory = _representable_add(
                    inventory, -quote_size, "inventory"
                )
                self._invoke_with_configuration_guard(
                    config,
                    strategy,
                    rng,
                    committed_rng_checkpoint,
                    committed_lifecycle,
                    strategy.on_fill,
                    _hit(strategy.symbol, Side.SELL, ask_px, quote_size),
                )
                self._assert_inventory_sync(next_inventory, strategy)
                cash, inventory = next_cash, next_inventory
                res._peak_inventory = max(res._peak_inventory, abs(inventory))
                res.n_fills += 1

            if hasattr(strategy, "time"):
                strategy.time += 1
            self._assert_guard_intact(
                config,
                strategy,
                rng,
                committed_rng_checkpoint,
                committed_lifecycle,
            )
            self._assert_inventory_sync(inventory, strategy)

            mid = event.next_mid
            marked_pnl = cash + inventory * mid
            if not all(math.isfinite(value) for value in (cash, inventory, marked_pnl)):
                raise OverflowError("simulation ledger became non-finite")
            res.mid.append(mid)
            res.inventory.append(inventory)
            res.pnl.append(marked_pnl)  # PnL marcado a mercado

        self._assert_inventory_sync(inventory, strategy)
        self._assert_guard_intact(
            config,
            strategy,
            rng,
            committed_rng_checkpoint,
            committed_lifecycle,
        )
        return res


def _hit(symbol, side, price, size):
    from exchange.trades import Fill
    return Fill(0, symbol, side, price, size)
