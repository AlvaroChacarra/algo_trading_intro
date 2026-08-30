"""Adversarial regressions for Backtest ownership and numeric effects."""

from copy import copy
from fractions import Fraction

import pytest

from exchange.backtest import Backtest
from exchange.market import Market
from exchange.orders import Order, OrderType, Side
from exchange.strategies.market_maker import MarketMaker
from exchange.strategies.vwap import VWAPStrategy
from exchange.strategy import NewOrder, Strategy
from exchange.trades import Fill


def _one_row_market() -> Market:
    return Market(
        "X",
        [{
            "timestamp": 1,
            "bid_price_1": 99.0,
            "bid_size_1": 1.0,
            "ask_price_1": 101.0,
            "ask_size_1": 1.0,
        }],
        depth=1,
    )


class _NoopStrategy(Strategy):
    def on_book_update(self, book):
        return []


def test_shallow_root_replacement_is_rejected_and_original_aliases_restored():
    class RootSwapper(Strategy):
        def __init__(self):
            self.backtest = None

        def on_book_update(self, book):
            self.backtest.market = copy(self.backtest.market)
            self.backtest.portfolio = copy(self.backtest.portfolio)
            return []

    market = _one_row_market()
    strategy = RootSwapper()
    backtest = Backtest(market, strategy)
    portfolio = backtest.portfolio
    strategy.backtest = backtest

    with pytest.raises(RuntimeError, match="market or portfolio"):
        backtest.run()

    assert backtest.market is market
    assert backtest.portfolio is portfolio
    assert [(level.price, level.size) for level in market.book.bids] == [
        (99.0, 1.0)
    ]
    assert [(level.price, level.size) for level in market.book.asks] == [
        (101.0, 1.0)
    ]
    assert (portfolio.cash, portfolio.position, portfolio.n_fills) == (0.0, 0.0, 0)


def test_root_replacement_is_rolled_back_when_callback_itself_raises():
    class RaisingRootSwapper(Strategy):
        def __init__(self):
            self.backtest = None

        def on_book_update(self, book):
            self.backtest.market = copy(self.backtest.market)
            self.backtest.portfolio = copy(self.backtest.portfolio)
            raise LookupError("callback failed after replacing roots")

    market = _one_row_market()
    strategy = RaisingRootSwapper()
    backtest = Backtest(market, strategy)
    portfolio = backtest.portfolio
    strategy.backtest = backtest

    with pytest.raises(LookupError, match="replacing roots"):
        backtest.run()

    assert backtest.market is market
    assert backtest.portfolio is portfolio
    assert (portfolio.cash, portfolio.position, portfolio.n_fills) == (0.0, 0.0, 0)


def test_strategy_root_replacement_is_rejected_without_blocking_internal_state():
    class StrategySwapper(Strategy):
        def __init__(self):
            self.backtest = None
            self.callbacks = 0

        def on_book_update(self, book):
            self.callbacks += 1
            self.backtest.strategy = _NoopStrategy()
            return []

    strategy = StrategySwapper()
    backtest = Backtest(_one_row_market(), strategy)
    strategy.backtest = backtest

    with pytest.raises(RuntimeError, match="strategy"):
        backtest.run()

    assert backtest.strategy is strategy
    assert strategy.callbacks == 1


def test_fill_ledger_exposes_reconstructed_values_not_authoritative_fill_aliases():
    class LedgerFillMutator(Strategy):
        def __init__(self):
            self.ledger = None

        def on_book_update(self, book):
            return [NewOrder(Order(
                "X", Side.BUY, 0.5, order_type=OrderType.MARKET
            ))]

        def on_fill(self, fill):
            exposed = list(self.ledger)[-1]
            exposed.__dict__["size"] = 999.0

    strategy = LedgerFillMutator()
    backtest = Backtest(_one_row_market(), strategy)
    strategy.ledger = backtest.portfolio._fills

    result = backtest.run()

    assert result.fills[0].size == 0.5
    assert list(backtest.portfolio._fills)[0].size == 0.5
    assert (backtest.portfolio.cash, backtest.portfolio.position) == (-50.5, 0.5)


def test_builtin_tuple_nodes_resist_tail_and_historical_reflection_mutation():
    class NodeCorruptor(Strategy):
        def __init__(self):
            self.ledger = None
            self.blocked = 0

        def on_book_update(self, book):
            tail = self.ledger._tail
            historical = tail[1]
            assert historical is not None
            corrupted = ((999, "X", "buy", 1.0, 999.0, None), None)
            for node in (tail, historical):
                try:
                    object.__setattr__(node, "values", corrupted)
                except (AttributeError, TypeError):
                    self.blocked += 1
                else:  # pragma: no cover - the invariant under test
                    raise AssertionError("builtin tuple node accepted mutation")
            return []

    strategy = NodeCorruptor()
    backtest = Backtest(_one_row_market(), strategy)
    backtest.portfolio.apply_fill(Fill(1, "X", Side.BUY, 1.0, 1.0))
    backtest.portfolio.apply_fill(Fill(2, "X", Side.SELL, 1.0, 1.0))
    strategy.ledger = backtest.portfolio._fills
    before = list(strategy.ledger)

    result = backtest.run()

    assert strategy.blocked == 2
    assert list(strategy.ledger) == before
    assert (backtest.portfolio.cash, backtest.portfolio.position) == (0.0, 0.0)
    assert backtest.portfolio.n_fills == 2
    assert result.n_fills == 0


def test_callback_checkpoints_do_not_materialize_long_fill_history(monkeypatch):
    backtest = Backtest(Market("X", [], depth=1), _NoopStrategy())
    for index in range(4096):
        backtest.portfolio.apply_fill(Fill(
            index * 2, "X", Side.BUY, 1.0, 1.0
        ))
        backtest.portfolio.apply_fill(Fill(
            index * 2 + 1, "X", Side.SELL, 1.0, 1.0
        ))

    ledger_type = type(backtest.portfolio._fills)

    def forbid_materialization(self):
        raise AssertionError("callback checkpoint materialized fill history")
        yield

    monkeypatch.setattr(ledger_type, "__iter__", forbid_materialization)

    result = backtest.run()

    assert result.n_steps == 0
    assert backtest.portfolio.n_fills == 8192


def test_vwap_rejects_one_unit_effect_loss_atomically():
    strategy = VWAPStrategy("X", Side.BUY, total_size=2e16, horizon=1)
    strategy.on_fill(Fill(1, "X", Side.BUY, 1.0, 1e16))
    before = strategy._executed

    with pytest.raises(OverflowError, match="not representable"):
        strategy.on_fill(Fill(2, "X", Side.BUY, 1.0, 100000001.0))

    assert strategy._executed == before


def test_vwap_rejects_distorted_residual_before_it_can_emit_an_overfill_retry():
    strategy = VWAPStrategy("X", Side.BUY, total_size=1e16, horizon=1)

    with pytest.raises(OverflowError, match="remaining parent"):
        strategy.on_fill(Fill(1, "X", Side.BUY, 1.0, 100000001.0))

    assert strategy._executed == 0.0


def test_vwap_retry_preserves_exact_parent_partition_when_representable():
    total = 1e16
    partial = 100000000.0
    strategy = VWAPStrategy("X", Side.BUY, total_size=total, horizon=1)
    strategy.on_fill(Fill(1, "X", Side.BUY, 1.0, partial))

    book = _one_row_market().step()
    retry = strategy.on_book_update(book)[0].order.size

    assert (
        Fraction.from_float(partial) + Fraction.from_float(retry)
        == Fraction.from_float(total)
    )
    strategy.on_fill(Fill(2, "X", Side.BUY, 1.0, retry))
    assert strategy._executed == total
    assert strategy.on_book_update(book) == []


def test_market_maker_rejects_one_unit_effect_loss_atomically():
    strategy = MarketMaker("X")
    strategy.inventory = 1e16

    with pytest.raises(OverflowError, match="not representable"):
        strategy.on_fill(Fill(1, "X", Side.BUY, 1.0, 100000001.0))

    assert strategy.inventory == 1e16


def test_strategy_effect_guards_accept_ordinary_binary_roundoff():
    vwap = VWAPStrategy("X", Side.BUY, total_size=2.0, horizon=1)
    vwap._executed = 1.4223
    vwap.on_fill(Fill(1, "X", Side.BUY, 1.0, 0.0413))
    assert vwap._executed == pytest.approx(1.4636)

    ordinary = VWAPStrategy("X", Side.BUY, total_size=1.0, horizon=1)
    ordinary.on_fill(Fill(2, "X", Side.BUY, 1.0, 0.1))
    assert ordinary._executed == 0.1

    maker = MarketMaker("X")
    maker.inventory = 1.4223
    maker.on_fill(Fill(3, "X", Side.BUY, 1.0, 0.0413))
    assert maker.inventory == pytest.approx(1.4636)
