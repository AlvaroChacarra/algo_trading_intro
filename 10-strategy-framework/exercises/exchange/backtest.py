"""backtest.py — el runner que lo cablea todo.

Construido en L8-L9. Recorre el mercado, pasa cada libro a la estrategia,
ejecuta sus acciones contra el matching, actualiza el portfolio y registra
métricas. Es la pieza que demuestra el polimorfismo: el mismo `run()` funciona
con cualquier `Strategy`.

Modelo de simulación: replay de snapshots. En cada paso se reconstruye el libro
desde el snapshot, así que una orden se cruza contra la foto actual y el
remanente de una LIMIT solo descansa dentro de ese paso (las estrategias que
quieren persistencia re-cotizan en cada tick, como hace el market maker).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.portfolio import PositionTracker
from exchange.strategy import Cancel, NewOrder, Strategy
from exchange.trades import Fill


class Context:
    """Lo que la estrategia puede consultar del estado global."""

    def __init__(self, market: Market, portfolio: PositionTracker) -> None:
        self.market = market
        self.portfolio = portfolio

    @property
    def timestamp(self) -> int | None:
        return self.market.timestamp

    @property
    def mid(self) -> float | None:
        return self.market.book.mid if self.market.book else None

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

    def run(self) -> BacktestResult:
        ctx = Context(self.market, self.portfolio)
        result = BacktestResult()
        self.strategy.on_start(ctx)

        resting: dict[int, Order] = {}
        last_mid = 0.0

        while True:
            book = self.market.step()
            if book is None:
                break
            resting.clear()  # el libro se reconstruye: nada persiste entre pasos
            result.n_steps += 1
            if book.mid is not None:
                last_mid = book.mid

            for action in self.strategy.on_book_update(book):
                if isinstance(action, NewOrder):
                    fills = self.market.submit(action.order)
                    filled = sum(f.size for f in fills)
                    for f in fills:
                        self.portfolio.apply_fill(f)
                        self.strategy.on_fill(f)
                        result.fills.append(f)
                    remainder = action.order.size - filled
                    if remainder > 1e-12 and action.order.order_type is OrderType.LIMIT:
                        resting[action.order.id] = action.order
                elif isinstance(action, Cancel):
                    order = resting.pop(action.order_id, None)
                    if order is not None and order.price is not None:
                        book.reduce(order.side, order.price, order.size)

            result.equity_curve.append(self.portfolio.equity(last_mid))

        result.final_cash = self.portfolio.cash
        result.final_position = self.portfolio.position
        result.final_equity = self.portfolio.equity(last_mid)
        self.strategy.on_end(ctx)
        return result
