"""backtest.py — el runner que lo cablea todo.

Construido en L10. Recorre el mercado, pasa cada libro a la estrategia,
ejecuta sus acciones contra el matching, actualiza el portfolio y registra
métricas. Es la pieza que demuestra el polimorfismo: el mismo `run()` funciona
con cualquier `Strategy`.

Modelo de simulación: replay de snapshots. En cada paso se reconstruye la
liquidez ajena desde el snapshot. El runner conserva por id el remanente exacto
de cada LIMIT propia, pero nunca lo mezcla con el libro agregado de liquidez
ajena. Al tick siguiente lo cruza contra la nueva foto y conserva solo lo que
siga abierto. Así dos órdenes propias no pueden ejecutarse entre sí y cancelar
una orden propia nunca altera la profundidad externa.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field, replace
from fractions import Fraction
import math
from typing import TypeAlias

from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.portfolio import PositionTracker
from exchange.strategy import Cancel, NewOrder, Strategy
from exchange.trades import Fill


_FillValues: TypeAlias = tuple[int, str, str, float, float, int | None]
_FillNode: TypeAlias = tuple[_FillValues, "_FillNode | None"]


class _FillLedger:
    """Persistent fill history with constant-time checkpoints and rollback.

    ``PositionTracker`` keeps its simple pedagogical list in standalone use.
    A ``Backtest`` substitutes this private compatible append/len container so
    it can detect and restore aliased callback mutations without copying or
    scanning every prior fill at every hook.
    """

    __slots__ = ("_tail", "_length")

    def __init__(self) -> None:
        self._tail: _FillNode | None = None
        self._length = 0

    def append(self, fill: Fill) -> None:
        values = (
            fill.order_id,
            str(fill.symbol),
            fill.side.value,
            fill.price,
            fill.size,
            fill.timestamp,
        )
        self._tail = (values, self._tail)
        self._length += 1

    def clear(self) -> None:
        """Discard history in O(1); a saved cursor can still restore it."""
        self._tail = None
        self._length = 0

    def __len__(self) -> int:
        return self._length

    def __iter__(self):
        # History is linked newest-first so materialising it is explicitly an
        # O(n) query, never an implicit callback-guard cost.
        reverse: list[_FillValues] = []
        node = self._tail
        while node is not None:
            if type(node) is not tuple or len(node) != 2:
                raise RuntimeError("fill ledger is structurally corrupted")
            values, previous = node
            if type(values) is not tuple or len(values) != 6:
                raise RuntimeError("fill ledger is structurally corrupted")
            reverse.append(values)
            node = previous
        for values in reversed(reverse):
            yield Fill(*values)

    def _checkpoint(self) -> tuple[_FillNode | None, int]:
        return self._tail, self._length

    def _matches(self, checkpoint: tuple[_FillNode | None, int]) -> bool:
        tail, length = checkpoint
        return (
            self._tail is tail
            and type(self._length) is int
            and self._length == length
        )

    def _restore(self, checkpoint: tuple[_FillNode | None, int]) -> None:
        self._tail, self._length = checkpoint


@dataclass(frozen=True)
class _MarketSnapshot:
    """Read-only, detached market state exposed through ``Context``."""

    symbol: str
    timestamp: int | None
    _book: object = field(repr=False)
    _snapshots: tuple[dict, ...] = field(repr=False)
    is_fresh: bool

    @classmethod
    def capture(cls, market: Market) -> "_MarketSnapshot":
        return cls(
            symbol=market.symbol,
            timestamp=market.timestamp,
            _book=deepcopy(market.book),
            _snapshots=tuple(market.snapshots),
            is_fresh=market.is_fresh,
        )

    @property
    def book(self):
        """Return a fresh copy so even nested mutations stay local."""
        return deepcopy(self._book)

    @property
    def snapshots(self) -> list[dict]:
        return deepcopy(list(self._snapshots))

    def __len__(self) -> int:
        return len(self._snapshots)


@dataclass(frozen=True)
class _PortfolioSnapshot:
    """Query-only portfolio state exposed through ``Context``."""

    cash: float
    position: float
    n_fills: int

    @classmethod
    def capture(cls, portfolio: PositionTracker) -> "_PortfolioSnapshot":
        return cls(portfolio.cash, portfolio.position, portfolio.n_fills)

    def equity(self, mark_price: float) -> float:
        if isinstance(mark_price, bool):
            raise ValueError("mark_price must be numeric, not boolean")
        mark_price = float(mark_price)
        if not math.isfinite(mark_price) or mark_price <= 0:
            raise ValueError("mark_price must be finite and positive")
        value = self.cash + self.position * mark_price
        if not math.isfinite(value):
            raise OverflowError("portfolio equity is non-finite")
        return value

    def unrealized_pnl(self, mark_price: float) -> float:
        if isinstance(mark_price, bool):
            raise ValueError("mark_price must be numeric, not boolean")
        mark_price = float(mark_price)
        if not math.isfinite(mark_price) or mark_price <= 0:
            raise ValueError("mark_price must be finite and positive")
        value = self.position * mark_price
        if not math.isfinite(value):
            raise OverflowError("unrealized PnL is non-finite")
        return value


@dataclass(frozen=True, init=False)
class Context:
    """Detached, read-only state that a lifecycle callback may inspect."""

    market: _MarketSnapshot
    portfolio: _PortfolioSnapshot

    def __init__(self, market: Market, portfolio: PositionTracker) -> None:
        object.__setattr__(self, "market", _MarketSnapshot.capture(market))
        object.__setattr__(self, "portfolio", _PortfolioSnapshot.capture(portfolio))

    @property
    def timestamp(self) -> int | None:
        return self.market.timestamp

    @property
    def mid(self) -> float | None:
        book = self.market.book
        return book.mid if book is not None else None

    @property
    def position(self) -> float:
        return self.portfolio.position


@dataclass
class BacktestResult:
    fills: list[Fill] = field(default_factory=list)
    equity_curve: list[float] = field(default_factory=list)
    final_cash: float = 0.0
    final_position: float = 0.0
    final_equity: float = 0.0
    n_steps: int = 0

    @property
    def n_fills(self) -> int:
        return len(self.fills)

    def __repr__(self) -> str:
        return (f"BacktestResult(steps={self.n_steps}, fills={self.n_fills}, "
                f"equity={self.final_equity:.2f}, pos={self.final_position:.4f})")


class Backtest:
    def __init__(self, market: Market, strategy: Strategy, cash: float = 0.0) -> None:
        self.market = market
        self.strategy = strategy
        self.portfolio = PositionTracker(cash=cash)
        self.portfolio._fills = _FillLedger()  # type: ignore[assignment]
        self._has_run = False

    def run(self) -> BacktestResult:
        """Consume exactly one fresh market and strategy lifecycle."""
        if self._has_run:
            raise RuntimeError("Backtest instances are single-use")
        if not self.market.is_fresh:
            raise ValueError("market must be fresh; call reset() before a new Backtest")
        if getattr(self.strategy, "_exchange_backtest_consumed", False):
            raise ValueError("strategy instance has already been consumed by a Backtest")
        self._has_run = True
        setattr(self.strategy, "_exchange_backtest_consumed", True)

        result = BacktestResult()

        def _strict_signature(value) -> object:
            """Fingerprint nested replay state without bool/number equality."""
            value_type = type(value)
            if isinstance(value, dict):
                return (
                    value_type,
                    tuple(
                        (_strict_signature(key), _strict_signature(item))
                        for key, item in value.items()
                    ),
                )
            if isinstance(value, (list, tuple)):
                return value_type, tuple(_strict_signature(item) for item in value)
            if isinstance(value, float):
                return value_type, value.hex()
            return value_type, value

        def market_checkpoint() -> dict[str, object]:
            market = self.market
            book = market.book
            return {
                "market_ref": market,
                "symbol": market.symbol,
                "snapshots_ref": market._snapshots,
                "depth": market._depth,
                "engine": market._engine,
                "index": market._i,
                "timestamp": market._timestamp,
                "book_ref": book,
                "book": deepcopy(book),
            }

        def _book_signature(book) -> object:
            if book is None:
                return None
            return (
                type(book),
                _strict_signature(book.symbol),
                type(book.bids),
                tuple(
                    (type(level), _strict_signature(level.price),
                     _strict_signature(level.size))
                    for level in book.bids
                ),
                type(book.asks),
                tuple(
                    (type(level), _strict_signature(level.price),
                     _strict_signature(level.size))
                    for level in book.asks
                ),
            )

        def market_changed(checkpoint: dict[str, object]) -> bool:
            return (
                self.market is not checkpoint["market_ref"]
                or _strict_signature(self.market.symbol)
                != _strict_signature(checkpoint["symbol"])
                or self.market._snapshots is not checkpoint["snapshots_ref"]
                or _strict_signature(self.market._depth)
                != _strict_signature(checkpoint["depth"])
                or self.market._engine is not checkpoint["engine"]
                or _strict_signature(self.market._i)
                != _strict_signature(checkpoint["index"])
                or _strict_signature(self.market._timestamp)
                != _strict_signature(checkpoint["timestamp"])
                or self.market.book is not checkpoint["book_ref"]
                or _book_signature(self.market.book) != _book_signature(checkpoint["book"])
            )

        def restore_market(checkpoint: dict[str, object]) -> None:
            market = checkpoint["market_ref"]
            market.symbol = checkpoint["symbol"]  # type: ignore[union-attr,assignment]
            market._snapshots = checkpoint["snapshots_ref"]  # type: ignore[union-attr,assignment]
            market._depth = checkpoint["depth"]  # type: ignore[union-attr,assignment]
            market._engine = checkpoint["engine"]  # type: ignore[union-attr,assignment]
            market._i = checkpoint["index"]  # type: ignore[union-attr,assignment]
            market._timestamp = checkpoint["timestamp"]  # type: ignore[union-attr,assignment]
            original_book = checkpoint["book_ref"]
            saved_book = checkpoint["book"]
            if original_book is not None and saved_book is not None:
                original_book.symbol = saved_book.symbol
                original_book.bids = deepcopy(saved_book.bids)
                original_book.asks = deepcopy(saved_book.asks)
            market.book = original_book  # type: ignore[union-attr,assignment]
            self.market = market  # type: ignore[assignment]

        def portfolio_checkpoint() -> dict[str, object]:
            portfolio = self.portfolio
            fills = portfolio._fills
            return {
                "portfolio_ref": portfolio,
                "cash": portfolio._cash,
                "position": portfolio._position,
                "fills_ref": fills,
                "fills_state": fills._checkpoint(),
            }

        def portfolio_changed(checkpoint: dict[str, object]) -> bool:
            return (
                self.portfolio is not checkpoint["portfolio_ref"]
                or _strict_signature(self.portfolio._cash)
                != _strict_signature(checkpoint["cash"])
                or _strict_signature(self.portfolio._position)
                != _strict_signature(checkpoint["position"])
                or self.portfolio._fills is not checkpoint["fills_ref"]
                or not self.portfolio._fills._matches(
                    checkpoint["fills_state"]
                )
            )

        def restore_portfolio(checkpoint: dict[str, object]) -> None:
            portfolio = checkpoint["portfolio_ref"]
            portfolio._cash = checkpoint["cash"]  # type: ignore[union-attr,assignment]
            portfolio._position = checkpoint["position"]  # type: ignore[union-attr,assignment]
            original_fills = checkpoint["fills_ref"]
            original_fills._restore(checkpoint["fills_state"])
            portfolio._fills = original_fills  # type: ignore[union-attr,assignment]
            self.portfolio = portfolio  # type: ignore[assignment]

        def invoke(callback, *args):
            """Run strategy code without granting authority over the ledger."""
            market_state = market_checkpoint()
            portfolio_state = portfolio_checkpoint()
            strategy_ref = self.strategy
            try:
                outcome = callback(*args)
            except Exception:
                restore_market(market_state)
                restore_portfolio(portfolio_state)
                self.strategy = strategy_ref
                raise
            try:
                changed_strategy = self.strategy is not strategy_ref
                changed_market = market_changed(market_state)
                changed_portfolio = portfolio_changed(portfolio_state)
            except Exception as inspection_error:
                restore_market(market_state)
                restore_portfolio(portfolio_state)
                self.strategy = strategy_ref
                raise RuntimeError(
                    "strategy callbacks corrupted the market or portfolio or strategy"
                ) from inspection_error
            if changed_portfolio or changed_market or changed_strategy:
                restore_market(market_state)
                restore_portfolio(portfolio_state)
                self.strategy = strategy_ref
                if changed_strategy:
                    target = "market or portfolio or strategy"
                else:
                    target = "market or portfolio" if changed_market else "portfolio"
                raise RuntimeError(f"strategy callbacks must not mutate the {target}")
            return outcome

        invoke(self.strategy.on_start, Context(self.market, self.portfolio))
        if not self.market.is_fresh:
            raise RuntimeError("strategy.on_start must not consume the market")

        resting: dict[int, Order] = {}
        last_mid: float | None = None

        def execute(order: Order) -> Order | None:
            """Execute one order and return only its still-resting remainder."""
            market_state = market_checkpoint()
            portfolio_state = portfolio_checkpoint()
            result_fill_count = len(result.fills)
            try:
                # Replay owns LIMIT remainders by id outside the aggregate
                # external book. Submit them as IOC for the crossing phase.
                crossing_order = (
                    replace(order, order_type=OrderType.IOC)
                    if order.order_type is OrderType.LIMIT
                    else order
                )
                fills = self.market.submit(crossing_order)
                filled = sum(
                    (Fraction.from_float(fill.size) for fill in fills),
                    Fraction(),
                )
                requested = Fraction.from_float(order.size)
                if filled > requested:
                    raise RuntimeError("matching produced fills larger than the order")
                remaining = requested - filled
                resting_size: float | None = None
                if order.order_type is OrderType.LIMIT and remaining > 0:
                    resting_size = float(remaining)
                    if Fraction.from_float(resting_size) != remaining:
                        raise OverflowError(
                            "limit-order remainder is not representable"
                        )

                for fill in fills:
                    self.portfolio.apply_fill(fill)
                    invoke(self.strategy.on_fill, deepcopy(fill))
                    result.fills.append(fill)

                if resting_size is not None:
                    return replace(order, size=resting_size)
                return None
            except Exception:
                restore_market(market_state)
                restore_portfolio(portfolio_state)
                del result.fills[result_fill_count:]
                raise

        def validate_actions(actions) -> list[NewOrder | Cancel]:
            """Materialize and validate a complete callback batch before effects."""
            try:
                batch = list(actions)
            except TypeError as exc:
                raise TypeError(
                    "on_book_update must return an iterable of actions"
                ) from exc

            projected_ids = set(resting)
            validated: list[NewOrder | Cancel] = []
            for action in batch:
                if isinstance(action, NewOrder):
                    if not isinstance(action.order, Order):
                        raise TypeError("NewOrder.order must be an Order")
                    if isinstance(action.order.id, bool) or not isinstance(
                        action.order.id, int
                    ):
                        raise TypeError("order id must be an integer")
                    order = Order(
                        symbol=action.order.symbol,
                        side=action.order.side,
                        size=action.order.size,
                        price=action.order.price,
                        order_type=action.order.order_type,
                        id=action.order.id,
                    )
                    if order.symbol != self.market.symbol:
                        raise ValueError(
                            f"symbol mismatch: order={order.symbol!r}, "
                            f"market={self.market.symbol!r}"
                        )
                    if last_mid is None:
                        raise ValueError(
                            "cannot submit orders before a two-sided mark is available"
                        )
                    if order.id in projected_ids:
                        raise ValueError(f"order id {order.id} is already resting")
                    projected_ids.add(order.id)
                    validated.append(NewOrder(order))
                elif isinstance(action, Cancel):
                    if isinstance(action.order_id, bool) or not isinstance(
                        action.order_id, int
                    ):
                        raise TypeError("cancel order id must be an integer")
                    projected_ids.discard(action.order_id)
                    validated.append(Cancel(action.order_id))
                else:
                    raise TypeError(
                        "strategy actions must be NewOrder or Cancel, "
                        f"not {type(action).__name__}"
                    )
            return validated

        def marked_equity() -> float:
            # Empty and initially one-sided markets are valid while the
            # portfolio is flat. Once a two-sided mid exists, its last value is
            # the explicit carry-forward mark for later one-sided snapshots.
            if last_mid is None:
                if self.portfolio.position != 0.0:
                    raise RuntimeError("a non-flat portfolio requires a valid mark")
                return self.portfolio.cash
            return self.portfolio.equity(last_mid)

        while True:
            book = self.market.step()
            if book is None:
                break
            result.n_steps += 1
            if book.mid is not None:
                last_mid = book.mid

            # The snapshot contains only external liquidity. Own resting limits
            # keep their identity in `resting` and may fill against the new tick.
            for order_id, order in list(resting.items()):
                remainder = execute(order)
                if remainder is None:
                    resting.pop(order_id)
                else:
                    resting[order_id] = remainder

            callback_book = deepcopy(book)
            actions = invoke(self.strategy.on_book_update, callback_book)
            # Iterables may defer arbitrary strategy code until iteration. Keep
            # materialisation and validation under the same mutation guard as
            # the callback that produced them.
            validated_actions = invoke(validate_actions, actions)
            for action in validated_actions:
                if isinstance(action, NewOrder):
                    remainder = execute(action.order)
                    if remainder is not None:
                        resting[action.order.id] = remainder
                else:
                    # Own remainders live only in the ownership ledger; the
                    # external snapshot book must remain untouched.
                    resting.pop(action.order_id, None)

            result.equity_curve.append(marked_equity())

        invoke(self.strategy.on_end, Context(self.market, self.portfolio))
        result.final_cash = self.portfolio.cash
        result.final_position = self.portfolio.position
        result.final_equity = marked_equity()
        return result
