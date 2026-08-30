"""Tests de invariantes del motor exchange/ — los bordes que el camino feliz no pisa.

Ejecutar desde framework/:  python -m pytest tests/ -q
"""

import math
import random
import sys
from dataclasses import FrozenInstanceError

import pytest

from exchange.book import Level, OrderBook
from exchange.backtest import Backtest
from exchange.market import Market
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType, Side
from exchange.portfolio import PositionTracker
from exchange.simulation import MMSimulation
from exchange.strategies.market_maker import MarketMaker
from exchange.strategies.vwap import VWAPStrategy
from exchange.strategy import Cancel, NewOrder, Strategy
from exchange.trades import Fill


def make_book():
    return OrderBook("BTCUSDT",
                     bids=[Level(99950, 0.5), Level(99940, 0.3)],
                     asks=[Level(100000, 0.4), Level(100010, 0.6)])


# ── OrderBook ───────────────────────────────────────────────────────────────

def test_book_orders_sides():
    ob = OrderBook("X", bids=[Level(99940, 1), Level(99950, 1)],
                   asks=[Level(100010, 1), Level(100000, 1)])
    assert ob.best_bid == 99950, "bids ordenados de mayor a menor"
    assert ob.best_ask == 100000, "asks ordenados de menor a mayor"


def test_empty_book_metrics_are_none():
    ob = OrderBook("X", bids=[], asks=[])
    assert ob.best_bid is None and ob.best_ask is None
    assert ob.spread is None and ob.mid is None and ob.microprice is None
    assert ob.imbalance(1) is None


def test_add_limit_merges_same_price():
    ob = make_book()
    ob.add_limit(Side.BUY, 99950, 0.5)
    assert ob.bids[0].size == pytest.approx(1.0), "mismo precio: se agrega, no se duplica"


def test_reduce_removes_exhausted_level():
    ob = make_book()
    ob.reduce(Side.SELL, 100000, 0.4)
    assert ob.best_ask == 100010, "el nivel agotado desaparece"


def test_reduce_nonexistent_price_is_noop():
    ob = make_book()
    before = [(lv.price, lv.size) for lv in ob.asks]
    ob.reduce(Side.SELL, 123456.0, 1.0)
    assert [(lv.price, lv.size) for lv in ob.asks] == before


def test_reduce_preserves_every_positive_tiny_residual():
    ob = OrderBook("X", bids=[], asks=[Level(100.0, 2e-13)])
    ob.reduce(Side.SELL, 100.0, 5e-14)
    assert len(ob.asks) == 1
    assert ob.asks[0].size == 2e-13 - 5e-14

    ob.reduce(Side.SELL, 100.0, ob.asks[0].size)
    assert ob.asks == []


def test_add_limit_overflow_is_atomic_and_extreme_metrics_stay_finite():
    largest = sys.float_info.max
    ob = OrderBook(
        "X",
        bids=[Level(1e308, largest)],
        asks=[Level(1.7e308, largest)],
    )
    assert math.isfinite(ob.mid)
    assert math.isfinite(ob.microprice)

    before = ob.bids[0].size
    with pytest.raises(OverflowError, match="level size"):
        ob.add_limit(Side.BUY, 1e308, largest)
    assert ob.bids[0].size == before


def test_unrepresentable_level_reduction_and_matching_are_atomic():
    direct = OrderBook("X", bids=[], asks=[Level(100.0, 1e16)])
    with pytest.raises(OverflowError, match="not representable"):
        direct.reduce(Side.SELL, 100.0, 1.0)
    assert direct.asks[0].size == 1e16

    for order_type in (OrderType.MARKET, OrderType.IOC, OrderType.FOK, OrderType.LIMIT):
        book = OrderBook("X", bids=[Level(99.0, 1.0)], asks=[Level(100.0, 1e16)])
        order = Order(
            "X", Side.BUY, 1.0,
            price=None if order_type is OrderType.MARKET else 100.0,
            order_type=order_type,
        )
        before = [(level.price, level.size) for level in book.asks]
        with pytest.raises(OverflowError, match="not representable"):
            MatchingEngine().process(order, book)
        assert [(level.price, level.size) for level in book.asks] == before


def test_book_rejects_materially_rounded_liquidity_changes_atomically():
    reduced = OrderBook("X", bids=[], asks=[Level(100.0, 1e16)])
    with pytest.raises(OverflowError, match="not representable"):
        reduced.reduce(Side.SELL, 100.0, 3.0)
    assert reduced.asks[0].size == 1e16

    added = OrderBook("X", bids=[Level(100.0, 1e16)], asks=[])
    with pytest.raises(OverflowError, match="not representable"):
        added.add_limit(Side.BUY, 100.0, 3.0)
    assert added.bids[0].size == 1e16


@pytest.mark.parametrize(
    ("base", "delta"),
    [
        (1e24, 1e16),  # the stored effect exceeds the request by 4,128,768
        (1e16, 100000001.0),  # the stored effect loses one whole unit
    ],
)
def test_book_rejects_large_scale_effect_distortion_atomically(base, delta):
    book = OrderBook("X", bids=[Level(100.0, base)], asks=[])
    before = book.bids[0].size

    with pytest.raises(OverflowError, match="not representable"):
        book.add_limit(Side.BUY, 100.0, delta)

    assert book.bids[0].size == before


def test_book_accepts_ordinary_relative_roundoff_without_an_absolute_epsilon():
    book = OrderBook("X", bids=[], asks=[Level(100.0, 1.4223)])
    book.reduce(Side.SELL, 100.0, 0.0413)
    assert book.asks[0].size == pytest.approx(1.381)

    smallest = math.ulp(0.0)
    tiny = OrderBook("X", bids=[], asks=[Level(smallest, 2 * smallest)])
    tiny.reduce(Side.SELL, smallest, smallest)
    assert tiny.asks[0].size == smallest


@pytest.mark.parametrize(
    "order_type",
    [OrderType.MARKET, OrderType.IOC, OrderType.FOK, OrderType.LIMIT],
)
def test_matching_rejects_an_unrepresentable_multilevel_remainder_atomically(
    order_type,
):
    book = OrderBook(
        "X",
        bids=[],
        asks=[Level(100.0, 1.0), Level(101.0, 1e16)],
    )
    order = Order(
        "X",
        Side.BUY,
        1e16,
        price=None if order_type is OrderType.MARKET else 101.0,
        order_type=order_type,
    )
    before = [(level.price, level.size) for level in book.asks]

    with pytest.raises(OverflowError, match="remainder is not representable"):
        MatchingEngine().process(order, book)

    assert [(level.price, level.size) for level in book.asks] == before


def test_matching_rejects_a_nonrepresentable_fractional_remainder_atomically():
    book = OrderBook(
        "X",
        bids=[],
        asks=[
            Level(100.0, 4.984050248487113e-104),
            Level(101.0, 7.3257760698808e-91),
        ],
    )
    order = Order(
        "X",
        Side.BUY,
        3.815678087081323e-91,
        order_type=OrderType.MARKET,
    )
    before = [(level.price, level.size) for level in book.asks]

    with pytest.raises(OverflowError, match="remainder is not representable"):
        MatchingEngine().process(order, book)

    assert [(level.price, level.size) for level in book.asks] == before


@pytest.mark.parametrize("field,bad", [
    ("price", True),
    ("size", False),
    ("price", math.nan),
    ("size", math.nan),
    ("price", math.inf),
    ("size", math.inf),
])
def test_matching_revalidates_mutated_book_levels_before_commit(field, bad):
    book = OrderBook("X", bids=[], asks=[Level(101.0, 1.0)])
    setattr(book.asks[0], field, bad)
    before = [
        (id(level), repr(level.price), repr(level.size))
        for level in book.asks
    ]

    with pytest.raises(ValueError):
        MatchingEngine().process(
            Order("X", Side.BUY, 0.5, order_type=OrderType.MARKET), book
        )

    assert [
        (id(level), repr(level.price), repr(level.size))
        for level in book.asks
    ] == before


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf, -math.inf])
def test_level_rejects_invalid_price_and_size(bad):
    with pytest.raises(ValueError):
        Level(bad, 1.0)
    with pytest.raises(ValueError):
        Level(100.0, bad)


@pytest.mark.parametrize("levels", [0, -1, True, 1.5])
def test_book_depth_requires_a_positive_integer(levels):
    with pytest.raises(ValueError, match="positive integer"):
        make_book().depth(Side.BUY, levels)


@pytest.mark.parametrize("bad_size", [-1.0, math.nan, math.inf, -math.inf])
def test_snapshot_rejects_invalid_level_sizes_instead_of_hiding_them(bad_size):
    row = {
        "bid_price_1": 99.0,
        "bid_size_1": bad_size,
        "ask_price_1": 101.0,
        "ask_size_1": 1.0,
    }
    with pytest.raises(ValueError, match="finite and non-negative"):
        OrderBook.from_snapshot("X", row, depth=1)


@pytest.mark.parametrize("depth", [0, -1, True, 1.5])
def test_snapshot_depth_requires_a_positive_integer(depth):
    with pytest.raises(ValueError, match="positive integer"):
        OrderBook.from_snapshot("X", {}, depth=depth)


def test_order_and_fill_notional_never_return_infinity():
    order = Order("X", Side.BUY, 1e308, 1e308)
    fill = Fill(order.id, "X", Side.BUY, 1e308, 1e308)
    with pytest.raises(OverflowError, match="order notional"):
        order.notional()
    with pytest.raises(OverflowError, match="fill notional"):
        _ = fill.notional
    with pytest.raises(OverflowError, match="fill notional"):
        fill.cash_flow()


def test_order_and_fill_notional_fail_closed_on_underflow():
    smallest = math.ulp(0.0)
    order = Order("X", Side.BUY, smallest, smallest)
    fill = Fill(order.id, "X", Side.BUY, smallest, smallest)
    with pytest.raises(OverflowError, match="underflowed to zero"):
        order.notional()
    with pytest.raises(OverflowError, match="underflowed to zero"):
        _ = fill.notional
    with pytest.raises(OverflowError, match="underflowed to zero"):
        fill.cash_flow()


@pytest.mark.parametrize("bad", [True, False])
def test_order_fill_and_level_reject_boolean_numeric_fields(bad):
    with pytest.raises(ValueError, match="boolean"):
        Order("X", Side.BUY, bad, 100.0)
    with pytest.raises(ValueError, match="boolean"):
        Order("X", Side.BUY, 1.0, bad)
    with pytest.raises(ValueError, match="positive integer"):
        Order("X", Side.BUY, 1.0, 100.0, id=bad)
    with pytest.raises(ValueError, match="boolean"):
        Fill(1, "X", Side.BUY, bad, 1.0)
    with pytest.raises(ValueError, match="boolean"):
        Fill(1, "X", Side.BUY, 100.0, bad)
    with pytest.raises(ValueError, match="order_id"):
        Fill(bad, "X", Side.BUY, 100.0, 1.0)
    with pytest.raises(ValueError, match="timestamp"):
        Fill(1, "X", Side.BUY, 100.0, 1.0, timestamp=bad)
    with pytest.raises(ValueError, match="boolean"):
        Level(bad, 1.0)
    with pytest.raises(ValueError, match="boolean"):
        Level(100.0, bad)


@pytest.mark.parametrize("bad", [True, False])
def test_book_rejects_boolean_snapshot_and_mutation_values_atomically(bad):
    row = {
        "bid_price_1": bad,
        "bid_size_1": 1.0,
        "ask_price_1": 101.0,
        "ask_size_1": 1.0,
    }
    with pytest.raises(ValueError, match="boolean"):
        OrderBook.from_snapshot("X", row, depth=1)
    row["bid_price_1"] = 99.0
    row["bid_size_1"] = bad
    with pytest.raises(ValueError, match="boolean"):
        OrderBook.from_snapshot("X", row, depth=1)

    for method in ("add_limit", "reduce"):
        for price, size in ((bad, 1.0), (100.0, bad)):
            book = make_book()
            before = (
                [(level.price, level.size) for level in book.bids],
                [(level.price, level.size) for level in book.asks],
            )
            with pytest.raises(ValueError, match="boolean"):
                getattr(book, method)(Side.BUY, price, size)
            assert before == (
                [(level.price, level.size) for level in book.bids],
                [(level.price, level.size) for level in book.asks],
            )


# ── MatchingEngine ──────────────────────────────────────────────────────────

def test_market_sweeps_multiple_levels():
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", 0.7, order_type=OrderType.MARKET), make_book())
    assert [f.price for f in fills] == [100000, 100010]
    assert sum(f.size for f in fills) == pytest.approx(0.7)


def test_market_partial_when_book_exhausted():
    book = make_book()
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", 5.0, order_type=OrderType.MARKET), book)
    assert sum(f.size for f in fills) == pytest.approx(1.0), "solo la liquidez visible"
    assert book.asks == [], "el lado queda vacío"


def test_limit_rests_remainder_at_its_price():
    book = make_book()
    MatchingEngine().process(
        Order("BTCUSDT", "buy", 1.0, price=100000, order_type=OrderType.LIMIT), book)
    assert book.best_bid == 100000, "el remanente descansa como nuevo best bid"
    assert book.bids[0].size == pytest.approx(0.6)


def test_ioc_cancels_remainder():
    book = make_book()
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", 1.0, price=100000, order_type=OrderType.IOC), book)
    assert sum(f.size for f in fills) == pytest.approx(0.4)
    assert book.best_bid == 99950, "IOC no deja nada descansando"


def test_fok_exact_fill_at_epsilon():
    book = make_book()
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", 1.0, price=100010, order_type=OrderType.FOK), book)
    assert sum(f.size for f in fills) == pytest.approx(1.0), "FOK exacto SÍ ejecuta"


def test_fok_impossible_leaves_book_untouched():
    book = make_book()
    before = [(lv.price, lv.size) for lv in book.asks]
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", 1.5, price=100010, order_type=OrderType.FOK), book)
    assert fills == []
    assert [(lv.price, lv.size) for lv in book.asks] == before


def test_fok_against_an_empty_opposite_side_is_a_noop():
    book = OrderBook("X", bids=[Level(99.0, 1.0)], asks=[])
    before = [(lv.price, lv.size) for lv in book.bids]
    fills = MatchingEngine().process(
        Order("X", Side.BUY, 1.0, 100.0, OrderType.FOK), book
    )
    assert fills == []
    assert [(lv.price, lv.size) for lv in book.bids] == before
    assert book.asks == []


def test_tiny_orders_are_never_dropped_by_an_absolute_epsilon():
    smallest = math.ulp(0.0)

    market_book = OrderBook("X", bids=[], asks=[Level(101.0, smallest)])
    fills = MatchingEngine().process(
        Order("X", Side.BUY, smallest, order_type=OrderType.MARKET),
        market_book,
    )
    assert [fill.size for fill in fills] == [smallest]
    assert market_book.asks == []

    resting_book = OrderBook("X", bids=[], asks=[Level(101.0, 1.0)])
    fills = MatchingEngine().process(
        Order("X", Side.BUY, smallest, 100.0, OrderType.LIMIT),
        resting_book,
    )
    assert fills == []
    assert resting_book.bids[0].size == smallest


def test_tiny_fok_shortfall_is_all_or_none_without_book_mutation():
    book = OrderBook("X", bids=[], asks=[Level(100.0, 1e-12)])
    before = [(lv.price, lv.size) for lv in book.asks]
    fills = MatchingEngine().process(
        Order("X", Side.BUY, 1.5e-12, 100.0, OrderType.FOK), book
    )
    assert fills == []
    assert [(lv.price, lv.size) for lv in book.asks] == before


def test_fok_uses_exact_fsum_capacity_not_sequential_roundoff():
    book = OrderBook(
        "X", bids=[], asks=[Level(100.0 + i, 0.1) for i in range(10)]
    )
    fills = MatchingEngine().process(
        Order("X", Side.BUY, 1.0, 109.0, OrderType.FOK), book
    )
    assert math.fsum(fill.size for fill in fills) == 1.0


def test_limit_that_does_not_cross_only_rests():
    book = make_book()
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", 0.2, price=99900, order_type=OrderType.LIMIT), book)
    assert fills == []
    assert any(lv.price == 99900 for lv in book.bids)


def test_symbol_mismatch_is_rejected_before_book_mutation():
    book = make_book()
    before = (
        [(lv.price, lv.size) for lv in book.bids],
        [(lv.price, lv.size) for lv in book.asks],
    )
    with pytest.raises(ValueError, match="symbol mismatch"):
        MatchingEngine().process(
            Order("ETHUSDT", "buy", 0.1, order_type=OrderType.MARKET), book
        )
    after = (
        [(lv.price, lv.size) for lv in book.bids],
        [(lv.price, lv.size) for lv in book.asks],
    )
    assert after == before


def test_matching_revalidates_mutated_order_before_book_mutation():
    book = OrderBook("X", bids=[], asks=[Level(101.0, 1.0)])
    order = Order("X", Side.BUY, 0.5, order_type=OrderType.MARKET)
    order.size = math.inf
    before = [(level.price, level.size) for level in book.asks]

    with pytest.raises(ValueError, match="size"):
        MatchingEngine().process(order, book)

    assert [(level.price, level.size) for level in book.asks] == before


@pytest.mark.parametrize("timestamp", [True, 1.5])
def test_matching_validates_timestamp_even_when_no_fill_is_created(timestamp):
    book = OrderBook("X", bids=[Level(99.0, 1.0)], asks=[Level(101.0, 1.0)])
    before = [(level.price, level.size) for level in book.bids]

    with pytest.raises(ValueError, match="timestamp"):
        MatchingEngine().process(
            Order("X", Side.BUY, 1.0, 100.0, OrderType.LIMIT),
            book,
            timestamp=timestamp,
        )

    assert [(level.price, level.size) for level in book.bids] == before


def test_matching_validates_fill_notional_before_atomic_commit():
    smallest = math.ulp(0.0)
    book = OrderBook("X", bids=[], asks=[Level(smallest, smallest)])
    before = [(level.price, level.size) for level in book.asks]

    with pytest.raises(OverflowError, match="fill notional"):
        MatchingEngine().process(
            Order("X", Side.BUY, smallest, order_type=OrderType.MARKET), book
        )

    assert [(level.price, level.size) for level in book.asks] == before


# ── Order ───────────────────────────────────────────────────────────────────

def test_order_validation():
    with pytest.raises(ValueError):
        Order("BTCUSDT", "buy", 0.0, price=100)          # size <= 0
    with pytest.raises(ValueError):
        Order("BTCUSDT", "buy", 1.0)                     # LIMIT sin precio
    assert Order("BTCUSDT", "buy", 1.0, order_type="market").price is None


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf, -math.inf])
def test_invalid_order_numbers_fail_before_book_mutation(bad):
    book = make_book()
    before = (
        [(lv.price, lv.size) for lv in book.bids],
        [(lv.price, lv.size) for lv in book.asks],
    )
    with pytest.raises(ValueError):
        Order("BTCUSDT", "buy", bad, price=100000)
    with pytest.raises(ValueError):
        Order("BTCUSDT", "buy", 1.0, price=bad)
    after = (
        [(lv.price, lv.size) for lv in book.bids],
        [(lv.price, lv.size) for lv in book.asks],
    )
    assert after == before


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf, -math.inf])
def test_fill_rejects_invalid_price_and_size(bad):
    with pytest.raises(ValueError):
        Fill(1, "X", Side.BUY, bad, 1.0)
    with pytest.raises(ValueError):
        Fill(1, "X", Side.BUY, 100.0, bad)


def test_fill_is_immutable_after_validation():
    fill = Fill(1, "X", Side.BUY, 100.0, 1.0)
    with pytest.raises(FrozenInstanceError):
        fill.size = 999.0


def test_side_enum_compares_with_str():
    assert Side.BUY == "buy" and Side.BUY.opposite == "sell"


# ── PositionTracker ─────────────────────────────────────────────────────────


@pytest.mark.parametrize("bad", [True, False])
def test_portfolio_rejects_boolean_cash_and_marks(bad):
    with pytest.raises(ValueError, match="boolean"):
        PositionTracker(cash=bad)
    tracker = PositionTracker()
    with pytest.raises(ValueError, match="boolean"):
        tracker.equity(bad)
    with pytest.raises(ValueError, match="boolean"):
        tracker.unrealized_pnl(bad)


def test_tracker_cash_position_always_consistent():
    """Invariante: tras N fills aleatorios, equity == cash + pos*mark exacto."""
    rng = random.Random(0)
    t = PositionTracker()
    cash = pos = 0.0
    for i in range(200):
        side = rng.choice(["buy", "sell"])
        price = 100 + rng.random()
        size = rng.random()
        t.apply_fill(Fill(i, "X", side, price, size))
        cash += -price * size if side == "buy" else price * size
        pos += size if side == "buy" else -size
    assert t.cash == pytest.approx(cash)
    assert t.position == pytest.approx(pos)
    assert t.equity(105.0) == pytest.approx(cash + pos * 105.0)


def test_tracker_rejects_unrepresentable_fill_atomically():
    tracker = PositionTracker()
    tracker.apply_fill(Fill(1, "X", Side.BUY, 1.0, 1e308))
    before = (tracker.cash, tracker.position, tracker.n_fills)

    with pytest.raises(OverflowError, match="not representable"):
        tracker.apply_fill(Fill(2, "X", Side.BUY, 1.0, 1e280))

    assert (tracker.cash, tracker.position, tracker.n_fills) == before

    distorted = PositionTracker()
    distorted.apply_fill(Fill(3, "X", Side.BUY, 1.0, 1e16))
    before = (distorted.cash, distorted.position, distorted.n_fills)
    with pytest.raises(OverflowError, match="not representable"):
        distorted.apply_fill(Fill(4, "X", Side.SELL, 1.0, 3.0))
    assert (distorted.cash, distorted.position, distorted.n_fills) == before


def test_tracker_rejects_one_unit_effect_loss_atomically():
    tracker = PositionTracker()
    tracker.apply_fill(Fill(1, "X", Side.BUY, 1.0, 1e16))
    before = (tracker.cash, tracker.position, tracker.n_fills)

    with pytest.raises(OverflowError, match="not representable"):
        tracker.apply_fill(Fill(2, "X", Side.BUY, 1.0, 100000001.0))

    assert (tracker.cash, tracker.position, tracker.n_fills) == before


# ── Market ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("bad", [True, False])
def test_market_rejects_boolean_depth_and_timestamp_atomically(bad):
    with pytest.raises(ValueError, match="depth"):
        Market("X", [], depth=bad)
    market = Market("X", [{"timestamp": bad}], depth=1)
    with pytest.raises(ValueError, match="timestamp"):
        market.step()
    assert market.is_fresh and market.book is None and market.timestamp is None


@pytest.mark.parametrize("bad", [1.5, math.nan, math.inf, -math.inf])
def test_market_rejects_nonintegral_or_nonfinite_timestamp_atomically(bad):
    market = Market("X", [{"timestamp": bad}], depth=1)
    with pytest.raises(ValueError, match="timestamp"):
        market.step()
    assert market.is_fresh and market.book is None and market.timestamp is None


def test_market_preserves_large_integer_timestamps_exactly(tmp_path):
    exact = 2**53 + 1
    direct = Market("X", [{"timestamp": exact}], depth=1)
    direct.step()
    assert direct.timestamp == exact

    path = tmp_path / "timestamps.csv"
    path.write_text(f"timestamp\n{exact}\n", encoding="utf-8")
    loaded = Market.from_csv(str(path), symbol="X", depth=1)
    loaded.step()
    assert loaded.timestamp == exact


def test_market_submit_before_step_raises():
    with pytest.raises(RuntimeError):
        Market.sample().submit(Order("BTCUSDT", "buy", 0.1, order_type="market"))


def test_market_reset_replays_identically():
    m = Market.sample()
    first = m.step().mid
    while m.step() is not None:
        pass
    m.reset()
    assert m.step().mid == first
    assert len(m) == 500


def test_market_snapshots_are_deep_defensive_at_input_and_output():
    source = [{
        "timestamp": 7,
        "bid_price_1": 99.0,
        "bid_size_1": 1.0,
        "ask_price_1": 101.0,
        "ask_size_1": 1.0,
        "metadata": {"levels": [{"size": 3.0}]},
    }]
    market = Market("X", source, depth=1)

    # Mutating the constructor input cannot rewrite the owned replay.
    source[0]["bid_price_1"] = 1.0
    source[0]["metadata"]["levels"][0]["size"] = 9.0

    exposed = market.snapshots
    exposed.append({"timestamp": 8})
    exposed[0]["ask_price_1"] = 999.0
    exposed[0]["metadata"]["levels"][0]["size"] = 11.0

    reread = market.snapshots
    assert len(reread) == 1
    assert reread[0]["bid_price_1"] == 99.0
    assert reread[0]["ask_price_1"] == 101.0
    assert reread[0]["metadata"]["levels"][0]["size"] == 3.0
    assert market.step().best_bid == 99.0


def test_market_step_rejects_invalid_next_snapshot_atomically():
    market = Market(
        "X",
        [
            {
                "timestamp": 7,
                "bid_price_1": 99.0,
                "bid_size_1": 1.0,
                "ask_price_1": 101.0,
                "ask_size_1": 1.0,
            },
            {
                "timestamp": 8,
                "bid_price_1": 99.0,
                "bid_size_1": 1.0,
                "ask_price_1": math.inf,
                "ask_size_1": 1.0,
            },
        ],
        depth=1,
    )
    first = market.step()
    with pytest.raises(ValueError, match="finite and positive"):
        market.step()

    assert market.book is first
    assert market.timestamp == 7
    assert market._i == 0
    assert market.book.best_ask == 101.0


# ── Strategy / Backtest lifecycle ──────────────────────────────────────────

class _SameTickPartialCancel(Strategy):
    def __init__(self) -> None:
        self.first = Order("X", Side.BUY, 1.0, 100.0, OrderType.LIMIT)
        self.second = Order("X", Side.BUY, 1.0, 100.0, OrderType.LIMIT)
        self.active_book = None
        self._sent = False

    def on_book_update(self, book):
        self.active_book = book
        if self._sent:
            return []
        self._sent = True
        return [
            NewOrder(self.first),
            NewOrder(self.second),
            Cancel(self.first.id),
        ]


def test_cancel_by_id_removes_only_partial_remainder():
    rows = [{
        "timestamp": 0,
        "bid_price_1": 99.0,
        "bid_size_1": 2.0,
        "ask_price_1": 100.0,
        "ask_size_1": 0.4,
    }]
    strategy = _SameTickPartialCancel()
    result = Backtest(Market("X", rows, depth=1), strategy).run()

    assert sum(fill.size for fill in result.fills) == pytest.approx(0.4)
    assert all(lv.price != 100.0 for lv in strategy.active_book.bids)
    assert strategy.active_book.bids[0].size == pytest.approx(2.0), (
        "owned remainders must stay out of the external snapshot book"
    )


class _RestAcrossTicksThenCancel(Strategy):
    def __init__(self) -> None:
        self.order = Order("X", Side.BUY, 1.0, 100.0, OrderType.LIMIT)
        self.tick = 0
        self.seen_remainder = None
        self.last_book = None
        self.fill_sizes = []

    def on_fill(self, fill):
        self.fill_sizes.append(fill.size)

    def on_book_update(self, book):
        self.last_book = book
        if self.tick == 0:
            actions = [NewOrder(self.order)]
        else:
            own_level = next((lv for lv in book.bids if lv.price == 100.0), None)
            self.seen_remainder = own_level.size if own_level else None
            actions = [Cancel(self.order.id)]
        self.tick += 1
        return actions


def test_resting_limit_survives_tick_fills_partially_then_cancels():
    rows = [
        {
            "timestamp": 0,
            "bid_price_1": 99.0,
            "bid_size_1": 2.0,
            "ask_price_1": 101.0,
            "ask_size_1": 1.0,
        },
        {
            "timestamp": 1,
            "bid_price_1": 99.0,
            "bid_size_1": 2.0,
            "ask_price_1": 100.0,
            "ask_size_1": 0.4,
        },
    ]
    strategy = _RestAcrossTicksThenCancel()
    result = Backtest(Market("X", rows, depth=1), strategy).run()

    assert strategy.fill_sizes == pytest.approx([0.4])
    assert strategy.seen_remainder is None, "own remainder is tracked outside the book"
    assert sum(fill.size for fill in result.fills) == pytest.approx(0.4)
    assert all(lv.price != 100.0 for lv in strategy.last_book.bids)
    assert strategy.last_book.best_bid == 99.0
    assert strategy.last_book.bids[0].size == pytest.approx(2.0), (
        "cancelling own remainder must preserve snapshot liquidity"
    )


def test_opposite_owned_limits_cannot_self_cross_or_manufacture_pnl():
    class TwoSided(Strategy):
        def __init__(self):
            self.sell = Order("X", Side.SELL, 1.0, 105.0, OrderType.LIMIT)
            self.buy = Order("X", Side.BUY, 1.0, 106.0, OrderType.LIMIT)

        def on_book_update(self, book):
            self.book = book
            return [NewOrder(self.sell), NewOrder(self.buy),
                    Cancel(self.sell.id), Cancel(self.buy.id)]

    rows = [{
        "timestamp": 0,
        "bid_price_1": 99.0,
        "bid_size_1": 10.0,
        "ask_price_1": 110.0,
        "ask_size_1": 10.0,
    }]
    strategy = TwoSided()
    result = Backtest(Market("X", rows, depth=1), strategy).run()

    assert result.fills == []
    assert result.final_cash == result.final_position == 0.0
    assert [(lv.price, lv.size) for lv in strategy.book.bids] == [(99.0, 10.0)]
    assert [(lv.price, lv.size) for lv in strategy.book.asks] == [(110.0, 10.0)]


def test_unknown_cancel_id_is_a_noop_for_external_liquidity():
    class CancelUnknown(Strategy):
        def on_book_update(self, book):
            self.book = book
            return [Cancel(999_999)]

    rows = [{
        "timestamp": 0,
        "bid_price_1": 100.0,
        "bid_size_1": 3.0,
        "ask_price_1": 101.0,
        "ask_size_1": 2.0,
    }]
    strategy = CancelUnknown()
    Backtest(Market("X", rows, depth=1), strategy).run()
    assert strategy.book.bids[0].size == pytest.approx(3.0)


class _NoopStrategy(Strategy):
    def on_book_update(self, book):
        return []


def _one_row_market():
    return Market("X", [{
        "timestamp": 0,
        "bid_price_1": 99.0,
        "bid_size_1": 1.0,
        "ask_price_1": 101.0,
        "ask_size_1": 1.0,
    }], depth=1)


def test_backtest_is_single_use_and_requires_fresh_market_and_strategy():
    strategy = _NoopStrategy()
    backtest = Backtest(_one_row_market(), strategy)
    assert backtest.run().n_steps == 1
    with pytest.raises(RuntimeError, match="single-use"):
        backtest.run()

    with pytest.raises(ValueError, match="strategy instance"):
        Backtest(_one_row_market(), strategy).run()

    stepped = _one_row_market()
    stepped.step()
    with pytest.raises(ValueError, match="market must be fresh"):
        Backtest(stepped, _NoopStrategy()).run()


def test_backtest_rejects_unknown_action_and_nonfinite_cash():
    class InvalidAction(Strategy):
        def on_book_update(self, book):
            return [object()]

    with pytest.raises(TypeError, match="NewOrder or Cancel"):
        Backtest(_one_row_market(), InvalidAction()).run()
    for cash in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError, match="cash"):
            Backtest(_one_row_market(), _NoopStrategy(), cash=cash)


def test_backtest_context_and_callback_book_are_detached_read_only_views():
    class HostileStrategy(Strategy):
        def on_start(self, ctx):
            self.start_ctx = ctx
            leaked = ctx.market.snapshots
            leaked[0]["ask_size_1"] = 0.0
            assert not hasattr(ctx.market, "step")
            assert not hasattr(ctx.market, "submit")
            assert not hasattr(ctx.portfolio, "apply_fill")
            with pytest.raises(FrozenInstanceError):
                ctx.portfolio.cash = 1_000_000.0

        def on_book_update(self, book):
            # If this were the authoritative book, both orders below would
            # lose their liquidity. It is only the callback's detached copy.
            book.asks.clear()
            book.bids[0].size = sys.float_info.max
            return [
                NewOrder(Order("X", Side.BUY, 0.5, order_type=OrderType.MARKET)),
                NewOrder(Order("X", Side.BUY, 0.5, order_type=OrderType.MARKET)),
            ]

        def on_end(self, ctx):
            self.end_ctx = ctx

    strategy = HostileStrategy()
    result = Backtest(_one_row_market(), strategy, cash=1_000.0).run()

    assert math.fsum(fill.size for fill in result.fills) == 1.0
    assert result.final_position == 1.0
    assert result.final_cash == 899.0
    assert strategy.start_ctx.market is not strategy.end_ctx.market
    assert strategy.end_ctx.portfolio.position == 1.0


def test_backtest_rejects_and_rolls_back_a_strategy_market_alias():
    market = _one_row_market()

    class AliasedMarketStrategy(Strategy):
        def __init__(self, aliased_market):
            self.aliased_market = aliased_market

        def on_book_update(self, book):
            self.aliased_market.book.asks.clear()
            return [NewOrder(Order("X", Side.BUY, 0.5,
                                   order_type=OrderType.MARKET))]

    backtest = Backtest(market, AliasedMarketStrategy(market))
    with pytest.raises(RuntimeError, match="market or portfolio"):
        backtest.run()
    assert [(level.price, level.size) for level in market.book.asks] == [(101.0, 1.0)]
    assert backtest.portfolio.n_fills == 0


def test_backtest_restores_state_when_callback_corrupts_guarded_book_shape():
    market = _one_row_market()

    class StructurallyCorruptingStrategy(Strategy):
        def __init__(self, aliased_market):
            self.aliased_market = aliased_market
            self.backtest = None
            self.authoritative_book = None

        def on_book_update(self, book):
            self.authoritative_book = self.aliased_market.book
            self.aliased_market.book.bids = None
            self.backtest.portfolio._cash = 123.0
            return []

    strategy = StructurallyCorruptingStrategy(market)
    backtest = Backtest(market, strategy)
    strategy.backtest = backtest

    with pytest.raises(RuntimeError, match="market or portfolio") as exc_info:
        backtest.run()

    assert isinstance(exc_info.value.__cause__, TypeError)
    assert market.book is strategy.authoritative_book
    assert [(level.price, level.size) for level in market.book.bids] == [(99.0, 1.0)]
    assert [(level.price, level.size) for level in market.book.asks] == [(101.0, 1.0)]
    assert backtest.portfolio.cash == 0.0
    assert backtest.portfolio.n_fills == 0


def test_backtest_restores_an_aliased_structurally_corrupt_fill_ledger():
    class FillLedgerCorruptor(Strategy):
        def __init__(self):
            self.ledger = None

        def on_book_update(self, book):
            # The strategy retained the exact private ledger object before the
            # callback, then corrupts its cursor rather than replacing it.
            self.ledger._tail = object()
            self.ledger._length = "corrupt"
            return []

    strategy = FillLedgerCorruptor()
    backtest = Backtest(_one_row_market(), strategy)
    backtest.portfolio.apply_fill(Fill(1, "X", Side.BUY, 1.0, 1.0))
    backtest.portfolio.apply_fill(Fill(2, "X", Side.SELL, 1.0, 1.0))
    strategy.ledger = backtest.portfolio._fills
    original_fills = list(strategy.ledger)

    with pytest.raises(RuntimeError, match="portfolio"):
        backtest.run()

    assert backtest.portfolio._fills is strategy.ledger
    assert list(strategy.ledger) == original_fills
    assert (backtest.portfolio.cash, backtest.portfolio.position) == (0.0, 0.0)
    assert backtest.portfolio.n_fills == 2


@pytest.mark.parametrize("mutation", ["append", "clear", "replace"])
def test_backtest_restores_fill_history_alias_mutations(mutation):
    class FillHistoryMutator(Strategy):
        def __init__(self):
            self.backtest = None
            self.ledger = None

        def on_book_update(self, book):
            if mutation == "append":
                self.ledger.append(Fill(99, "X", Side.BUY, 1.0, 1.0))
            elif mutation == "clear":
                self.ledger.clear()
            else:
                self.backtest.portfolio._fills = object()
            return []

    strategy = FillHistoryMutator()
    backtest = Backtest(_one_row_market(), strategy)
    backtest.portfolio.apply_fill(Fill(1, "X", Side.BUY, 1.0, 1.0))
    backtest.portfolio.apply_fill(Fill(2, "X", Side.SELL, 1.0, 1.0))
    strategy.backtest = backtest
    strategy.ledger = backtest.portfolio._fills
    original_fills = list(strategy.ledger)

    with pytest.raises(RuntimeError, match="portfolio"):
        backtest.run()

    assert backtest.portfolio._fills is strategy.ledger
    assert list(strategy.ledger) == original_fills
    assert (backtest.portfolio.cash, backtest.portfolio.position) == (0.0, 0.0)
    assert backtest.portfolio.n_fills == 2


def test_callback_guard_does_not_iterate_existing_fill_history(monkeypatch):
    """A callback checkpoint must stay O(1) as the fill history grows."""
    backtest = Backtest(Market("X", [], depth=1), _NoopStrategy())
    for index in range(512):
        backtest.portfolio.apply_fill(
            Fill(index * 2, "X", Side.BUY, 1.0, 1.0)
        )
        backtest.portfolio.apply_fill(
            Fill(index * 2 + 1, "X", Side.SELL, 1.0, 1.0)
        )

    ledger_type = type(backtest.portfolio._fills)

    def forbid_history_scan(self):
        raise AssertionError("callback guard scanned historical fills")
        yield  # pragma: no cover - retain generator protocol

    monkeypatch.setattr(ledger_type, "__iter__", forbid_history_scan)

    result = backtest.run()

    assert result.n_steps == 0
    assert result.final_cash == result.final_position == result.final_equity == 0.0
    assert backtest.portfolio.n_fills == 1024


def test_backtest_fill_callback_cannot_rewrite_authoritative_fill():
    class FillMutator(Strategy):
        def on_book_update(self, book):
            return [NewOrder(Order("X", Side.BUY, 0.25,
                                   order_type=OrderType.MARKET))]

        def on_fill(self, fill):
            with pytest.raises(FrozenInstanceError):
                fill.size = 100.0

    result = Backtest(_one_row_market(), FillMutator()).run()
    assert result.fills[0].size == 0.25
    assert result.final_position == 0.25
    assert result.final_cash == -25.25


def test_backtest_prevalidates_entire_action_batch_before_execution():
    class ValidThenInvalid(Strategy):
        def on_book_update(self, book):
            return [
                NewOrder(Order("X", Side.BUY, 0.5,
                               order_type=OrderType.MARKET)),
                object(),
            ]

    market = _one_row_market()
    backtest = Backtest(market, ValidThenInvalid())
    with pytest.raises(TypeError, match="NewOrder or Cancel"):
        backtest.run()

    assert backtest.portfolio.n_fills == 0
    assert backtest.portfolio.position == 0.0
    assert market.book.asks[0].size == 1.0


def test_backtest_materializes_failing_action_generators_before_execution():
    class FailingGenerator(Strategy):
        def on_book_update(self, book):
            def actions():
                yield NewOrder(Order("X", Side.BUY, 0.5,
                                     order_type=OrderType.MARKET))
                raise RuntimeError("generator failed")
            return actions()

    market = _one_row_market()
    backtest = Backtest(market, FailingGenerator())
    with pytest.raises(RuntimeError, match="generator failed"):
        backtest.run()
    assert backtest.portfolio.n_fills == 0
    assert market.book.asks[0].size == 1.0


def test_backtest_guards_deferred_generator_code_against_market_aliases():
    market = _one_row_market()

    class DeferredAliasMutation(Strategy):
        def __init__(self, aliased_market):
            self.aliased_market = aliased_market

        def on_book_update(self, book):
            def actions():
                self.aliased_market.book.asks.clear()
                yield NewOrder(Order("X", Side.BUY, 0.5,
                                     order_type=OrderType.MARKET))
            return actions()

    backtest = Backtest(market, DeferredAliasMutation(market))
    with pytest.raises(RuntimeError, match="market or portfolio"):
        backtest.run()

    assert [(level.price, level.size) for level in market.book.asks] == [(101.0, 1.0)]
    assert backtest.portfolio.n_fills == 0


def test_backtest_rejects_and_restores_nested_replay_alias_mutation():
    market = _one_row_market()

    class ReplayAliasMutation(Strategy):
        def __init__(self, aliased_market):
            self.aliased_market = aliased_market

        def on_book_update(self, book):
            self.aliased_market._snapshots[0]["ask_price_1"] = 1.0
            return []

    with pytest.raises(TypeError):
        Backtest(market, ReplayAliasMutation(market)).run()

    market.reset()
    assert market.step().best_ask == 101.0


def test_backtest_mutation_guard_compares_numeric_types_strictly():
    market = _one_row_market()

    class BooleanAliasMutation(Strategy):
        def __init__(self, aliased_market):
            self.aliased_market = aliased_market
            self.backtest = None

        def on_book_update(self, book):
            self.aliased_market.book.asks[0].size = True
            self.backtest.portfolio._cash = False
            return []

    strategy = BooleanAliasMutation(market)
    backtest = Backtest(market, strategy)
    strategy.backtest = backtest
    with pytest.raises(RuntimeError, match="market or portfolio"):
        backtest.run()

    assert type(backtest.portfolio.cash) is float
    assert backtest.portfolio.cash == 0.0
    assert type(market.book.asks[0].size) is float
    assert market.book.asks[0].size == 1.0


def test_backtest_rejects_an_unrepresentable_limit_remainder_atomically():
    class HugeLimit(Strategy):
        def __init__(self):
            self.sent = False

        def on_book_update(self, book):
            if self.sent:
                return []
            self.sent = True
            return [NewOrder(Order("X", Side.BUY, 1e16, 100.0,
                                   OrderType.LIMIT))]

    market = Market("X", [{
        "timestamp": 0,
        "bid_price_1": 99.0,
        "bid_size_1": 1.0,
        "ask_price_1": 100.0,
        "ask_size_1": 1.0,
    }], depth=1)
    backtest = Backtest(market, HugeLimit())

    with pytest.raises(OverflowError, match="remainder is not representable"):
        backtest.run()

    assert [(level.price, level.size) for level in market.book.asks] == [(100.0, 1.0)]
    assert backtest.portfolio.n_fills == 0


def test_backtest_rejects_a_fractional_limit_remainder_atomically():
    class FractionalLimit(Strategy):
        def on_book_update(self, book):
            return [NewOrder(Order(
                "X",
                Side.BUY,
                3.815678087081323e-91,
                100.0,
                OrderType.LIMIT,
            ))]

    tiny_liquidity = 4.984050248487113e-104
    market = Market("X", [{
        "timestamp": 0,
        "bid_price_1": 99.0,
        "bid_size_1": 1.0,
        "ask_price_1": 100.0,
        "ask_size_1": tiny_liquidity,
    }], depth=1)
    backtest = Backtest(market, FractionalLimit())

    with pytest.raises(OverflowError, match="remainder is not representable"):
        backtest.run()

    assert [(level.price, level.size) for level in market.book.asks] == [
        (100.0, tiny_liquidity)
    ]
    assert backtest.portfolio.n_fills == 0


def test_backtest_rolls_back_book_and_portfolio_when_on_fill_raises():
    class FailingFillCallback(Strategy):
        def on_book_update(self, book):
            return [NewOrder(Order("X", Side.BUY, 0.5,
                                   order_type=OrderType.MARKET))]

        def on_fill(self, fill):
            raise RuntimeError("fill callback failed")

    market = _one_row_market()
    backtest = Backtest(market, FailingFillCallback())
    with pytest.raises(RuntimeError, match="fill callback failed"):
        backtest.run()

    assert [(level.price, level.size) for level in market.book.asks] == [(101.0, 1.0)]
    assert backtest.portfolio.n_fills == 0
    assert backtest.portfolio.position == 0.0


def test_nested_on_fill_alias_rollback_restores_the_pre_execution_ledger():
    class FailingAliasedFillCallback(Strategy):
        def __init__(self):
            self.ledger = None

        def on_book_update(self, book):
            return [NewOrder(Order("X", Side.BUY, 0.5,
                                   order_type=OrderType.MARKET))]

        def on_fill(self, fill):
            # ``invoke`` first restores the state containing the authoritative
            # fill; ``execute`` must then roll that fill back as one transaction.
            self.ledger.clear()
            self.ledger.append(Fill(999, "X", Side.SELL, 1.0, 1.0))
            raise RuntimeError("aliased fill callback failed")

    market = _one_row_market()
    strategy = FailingAliasedFillCallback()
    backtest = Backtest(market, strategy)
    strategy.ledger = backtest.portfolio._fills

    with pytest.raises(RuntimeError, match="aliased fill callback failed"):
        backtest.run()

    assert backtest.portfolio._fills is strategy.ledger
    assert list(strategy.ledger) == []
    assert (backtest.portfolio.cash, backtest.portfolio.position) == (0.0, 0.0)
    assert backtest.portfolio.n_fills == 0
    assert [(level.price, level.size) for level in market.book.asks] == [(101.0, 1.0)]


def test_callback_mutation_followed_by_exception_cannot_touch_market_state():
    class MutateThenRaise(Strategy):
        def on_book_update(self, book):
            book.asks.clear()
            book.bids[0].size = sys.float_info.max
            raise RuntimeError("callback failed")

    market = _one_row_market()
    backtest = Backtest(market, MutateThenRaise())
    with pytest.raises(RuntimeError, match="callback failed"):
        backtest.run()
    assert backtest.portfolio.n_fills == 0
    assert [(lv.price, lv.size) for lv in market.book.bids] == [(99.0, 1.0)]
    assert [(lv.price, lv.size) for lv in market.book.asks] == [(101.0, 1.0)]


def test_context_snapshot_mutation_followed_by_exception_cannot_rewrite_replay():
    class MutateContextThenRaise(Strategy):
        def on_start(self, ctx):
            snapshots = ctx.market.snapshots
            snapshots[0]["ask_price_1"] = 1.0
            raise RuntimeError("start failed")

        def on_book_update(self, book):
            return []

    market = _one_row_market()
    with pytest.raises(RuntimeError, match="start failed"):
        Backtest(market, MutateContextThenRaise()).run()
    assert market.is_fresh
    assert market.step().best_ask == 101.0


def test_backtest_empty_and_one_sided_mark_contract_is_explicit():
    empty = Backtest(Market("X", [], depth=1), _NoopStrategy(), cash=17.0).run()
    assert empty.n_steps == 0
    assert empty.equity_curve == []
    assert empty.final_equity == 17.0

    one_sided = Market("X", [{
        "timestamp": 0,
        "ask_price_1": 101.0,
        "ask_size_1": 1.0,
    }], depth=1)
    held = Backtest(one_sided, _NoopStrategy(), cash=17.0).run()
    assert held.equity_curve == [17.0]
    assert held.final_equity == 17.0


def test_backtest_rejects_trading_before_first_two_sided_mark_atomically():
    class TradesWithoutMark(Strategy):
        def on_book_update(self, book):
            return [NewOrder(Order("X", Side.BUY, 0.5,
                                   order_type=OrderType.MARKET))]

    market = Market("X", [{
        "timestamp": 0,
        "ask_price_1": 101.0,
        "ask_size_1": 1.0,
    }], depth=1)
    backtest = Backtest(market, TradesWithoutMark())
    with pytest.raises(ValueError, match="two-sided mark"):
        backtest.run()
    assert backtest.portfolio.n_fills == 0
    assert market.book.asks[0].size == 1.0


# ── Execution and market-making feedback ───────────────────────────────────


@pytest.mark.parametrize("bad", [True, False])
def test_vwap_rejects_boolean_sizes_and_profile_weights(bad):
    with pytest.raises(ValueError, match="boolean"):
        VWAPStrategy("X", Side.BUY, total_size=bad, horizon=1)
    with pytest.raises(ValueError, match="boolean"):
        VWAPStrategy("X", Side.BUY, total_size=1.0, horizon=1, profile=[bad])


def test_vwap_progress_is_fill_driven_and_retries_shortfall():
    strategy = VWAPStrategy("X", Side.BUY, total_size=1.0, horizon=2)
    book = OrderBook("X", bids=[Level(99.0, 1.0)], asks=[Level(101.0, 1.0)])

    first = strategy.on_book_update(book)[0].order
    assert first.size == pytest.approx(0.5)
    assert strategy._executed == 0.0, "submitting is not executing"

    strategy.on_fill(Fill(first.id, "X", Side.BUY, 101.0, 0.2))
    assert strategy._executed == pytest.approx(0.2)

    second = strategy.on_book_update(book)[0].order
    assert second.size == pytest.approx(0.8), (
        "second cumulative slice must retry the unfilled 0.3"
    )


def test_vwap_rejects_unrepresentable_progress_and_overfill_atomically():
    strategy = VWAPStrategy("X", Side.BUY, total_size=1e308, horizon=1)
    strategy.on_fill(Fill(1, "X", Side.BUY, 1.0, 1e300))
    before = strategy._executed
    with pytest.raises(OverflowError, match="not representable"):
        strategy.on_fill(Fill(2, "X", Side.BUY, 1.0, 1e280))
    assert strategy._executed == before

    small = VWAPStrategy("X", Side.BUY, total_size=1.0, horizon=1)
    with pytest.raises(ValueError, match="remaining parent"):
        small.on_fill(Fill(3, "X", Side.BUY, 1.0, 1.1))
    assert small._executed == 0.0

    lossy_remaining = VWAPStrategy(
        "X", Side.BUY, total_size=1e16, horizon=2,
        profile=[1.0, 1e16],
    )
    with pytest.raises(OverflowError, match="remaining parent"):
        lossy_remaining.on_fill(Fill(4, "X", Side.BUY, 1.0, 1.0))
    assert lossy_remaining._executed == 0.0

    distorted = VWAPStrategy("X", Side.BUY, total_size=2e16, horizon=2)
    distorted.on_fill(Fill(5, "X", Side.BUY, 1.0, 1e16))
    before = distorted._executed
    with pytest.raises(OverflowError, match="not representable"):
        distorted.on_fill(Fill(6, "X", Side.BUY, 1.0, 3.0))
    assert distorted._executed == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"total_size": 0.0, "horizon": 2},
        {"total_size": math.nan, "horizon": 2},
        {"total_size": 1.0, "horizon": 0},
        {"total_size": 1.0, "horizon": 2, "profile": [1.0]},
        {"total_size": 1.0, "horizon": 2, "profile": [0.0, 0.0]},
        {"total_size": 1.0, "horizon": 2, "profile": [1.0, -1.0]},
        {"total_size": 1.0, "horizon": 2, "profile": [1.0, math.inf]},
    ],
)
def test_vwap_rejects_profiles_that_cannot_define_the_parent_schedule(kwargs):
    with pytest.raises(ValueError):
        VWAPStrategy("X", Side.BUY, **kwargs)


@pytest.mark.parametrize(
    "field,bad",
    [
        ("total_size", True),
        ("total_size", math.nan),
        ("horizon", True),
        ("horizon", 0),
        ("profile", True),
        ("profile", [True, False]),
        ("profile", [0.2, 0.2]),
        ("side", True),
    ],
)
def test_vwap_revalidates_mutable_public_configuration(field, bad):
    strategy = VWAPStrategy("X", Side.BUY, total_size=1.0, horizon=2)
    setattr(strategy, field, bad)
    book = OrderBook("X", [Level(99.0, 1.0)], [Level(101.0, 1.0)])
    with pytest.raises(ValueError):
        strategy.on_book_update(book)
    assert strategy._t == 0 and strategy._executed == 0.0


def test_vwap_valid_profile_is_copied_and_reaches_parent_with_liquidity():
    profile = [1.0, 1.0, 8.0]
    strategy = VWAPStrategy("X", Side.BUY, total_size=1.0, horizon=3,
                            profile=profile)
    profile[:] = [8.0, 1.0, 1.0]
    book = OrderBook("X", [Level(99.0, 10.0)], [Level(101.0, 10.0)])
    submitted = 0.0
    for _ in range(3):
        order = strategy.on_book_update(book)[0].order
        submitted += order.size
        strategy.on_fill(Fill(order.id, "X", Side.BUY, 101.0, order.size))
    assert submitted == pytest.approx(1.0)
    assert strategy._executed == pytest.approx(strategy.total_size)


def test_vwap_terminal_target_is_exact_and_retries_a_partial_final_slice():
    strategy = VWAPStrategy("X", Side.BUY, total_size=1e16, horizon=4,
                            profile=[8.0, 9.0, 9.0, 9.0])
    book = OrderBook("X", [Level(99.0, 1.0)], [Level(101.0, 1e16)])
    orders = []
    for _ in range(3):
        order = strategy.on_book_update(book)[0].order
        orders.append(order)
        strategy.on_fill(Fill(order.id, "X", Side.BUY, 101.0, order.size))
    final = strategy.on_book_update(book)[0].order
    partial = final.size / 2
    strategy.on_fill(Fill(final.id, "X", Side.BUY, 101.0, partial))
    retry = strategy.on_book_update(book)[0].order
    assert retry.size == strategy.total_size - strategy._executed
    strategy.on_fill(Fill(retry.id, "X", Side.BUY, 101.0, retry.size))
    assert strategy._executed == strategy.total_size


def test_vwap_preserves_a_positive_subnormal_parent_order():
    smallest = math.ulp(0.0)
    strategy = VWAPStrategy("X", Side.BUY, total_size=smallest, horizon=1)
    book = OrderBook("X", [Level(99.0, 1.0)], [Level(101.0, 1.0)])
    order = strategy.on_book_update(book)[0].order
    assert order.size == smallest
    strategy.on_fill(Fill(order.id, "X", Side.BUY, 101.0, smallest))
    assert strategy.on_book_update(book) == []


@pytest.mark.parametrize("bad", [True, False])
def test_market_maker_rejects_boolean_numeric_state_and_parameters(bad):
    for field in ("quote_size", "half_spread", "inventory_skew"):
        with pytest.raises(ValueError, match="boolean"):
            MarketMaker("SIM", **{field: bad})
    maker = MarketMaker("SIM")
    with pytest.raises(ValueError, match="boolean"):
        maker.inventory = bad
    with pytest.raises(ValueError, match="boolean"):
        maker.reservation_price(bad)


def test_market_maker_rejects_distorted_inventory_fill_atomically():
    maker = MarketMaker("SIM")
    maker.inventory = 1e16
    with pytest.raises(OverflowError, match="not representable"):
        maker.on_fill(Fill(1, "SIM", Side.SELL, 1.0, 3.0))
    assert maker.inventory == 1e16


@pytest.mark.parametrize(
    "field,bad",
    [
        ("quote_size", True),
        ("quote_size", math.nan),
        ("half_spread", True),
        ("half_spread", math.inf),
        ("inventory_skew", True),
        ("inventory_skew", math.nan),
    ],
)
def test_market_maker_revalidates_mutable_public_configuration(field, bad):
    maker = MarketMaker("SIM")
    setattr(maker, field, bad)
    book = OrderBook("SIM", [Level(99.0, 1.0)], [Level(101.0, 1.0)])
    with pytest.raises(ValueError):
        maker.quotes(book)


@pytest.mark.parametrize("bad", [True, False])
def test_mm_simulation_rejects_boolean_model_parameters(bad):
    for field in ("s0", "sigma", "A", "kappa"):
        with pytest.raises(ValueError, match="boolean"):
            MMSimulation(MarketMaker("SIM"), steps=1, **{field: bad})


@pytest.mark.parametrize(
    "field,bad",
    [
        ("s0", True),
        ("s0", math.nan),
        ("sigma", True),
        ("sigma", math.inf),
        ("steps", True),
        ("steps", 0),
        ("A", True),
        ("A", math.nan),
        ("kappa", True),
        ("kappa", math.inf),
    ],
)
def test_mm_simulation_revalidates_mutable_public_configuration(field, bad):
    simulation = MMSimulation(MarketMaker("SIM"), steps=2)
    setattr(simulation, field, bad)
    with pytest.raises(ValueError):
        simulation.run()
    assert simulation._has_run is False


def test_mm_simulation_enforces_synthetic_book_domain_before_lifecycle():
    maker = MarketMaker("SIM", half_spread=0.0, inventory_skew=0.0)
    simulation = MMSimulation(maker, s0=1.0, sigma=0.0, steps=2, A=0.0)
    simulation.s0 = 0.5

    with pytest.raises(ValueError, match="synthetic-book half-spread"):
        simulation.run()

    assert simulation._has_run is False
    assert not hasattr(maker, "_exchange_mm_consumed")

    simulation.s0 = math.nextafter(0.5, math.inf)
    result = simulation.run()
    assert len(result.mid) == 2
    assert all(price == simulation.s0 for price in result.mid)


@pytest.mark.parametrize("s0", [math.ulp(0.0), 0.5])
def test_mm_simulation_rejects_unusable_initial_book_prices_at_construction(s0):
    maker = MarketMaker("SIM")
    with pytest.raises(ValueError, match="synthetic-book half-spread"):
        MMSimulation(maker, s0=s0)
    assert not hasattr(maker, "_exchange_mm_consumed")


def test_mm_simulation_revalidates_strategy_before_consuming_lifecycle():
    maker = MarketMaker("SIM")
    maker.half_spread = True
    simulation = MMSimulation(maker, steps=2)
    with pytest.raises(ValueError, match="boolean"):
        simulation.run()
    assert simulation._has_run is False
    assert not hasattr(maker, "_exchange_mm_consumed")


def test_mm_simulation_reports_real_fills_and_coherent_metrics():
    strategy = MarketMaker(
        "SIM", quote_size=0.1, half_spread=0.3, inventory_skew=2.0
    )
    result = MMSimulation(strategy, steps=200, seed=42).run()

    assert result.n_fills > 0
    assert len(result.pnl) == len(result.inventory) == 200
    assert math.isfinite(result.final_pnl)
    assert math.isfinite(result.max_inventory) and result.max_inventory > 0
    assert strategy.inventory == pytest.approx(result.inventory[-1])


def test_mm_simulation_rejects_preloaded_or_reused_strategy_state():
    preloaded = MarketMaker("SIM")
    preloaded.inventory = 1.0
    with pytest.raises(ValueError, match="flat"):
        MMSimulation(preloaded, steps=3).run()

    simulation = MMSimulation(MarketMaker("SIM"), steps=3)
    simulation.run()
    with pytest.raises(RuntimeError, match="single-use"):
        simulation.run()


def test_mm_simulation_rejects_strategy_that_ignores_fill_feedback():
    class BrokenFeedback(MarketMaker):
        def on_fill(self, fill):
            pass

    with pytest.raises(RuntimeError, match="inventory synchronized"):
        MMSimulation(BrokenFeedback("SIM", half_spread=0.0), steps=3, A=1.0).run()


def test_mm_simulation_checks_inventory_sync_even_when_no_fill_occurs():
    class MutatesInsideQuotes(MarketMaker):
        def quotes(self, book):
            self.inventory = 3.0
            return super().quotes(book)

    with pytest.raises(RuntimeError, match="inventory synchronized"):
        MMSimulation(MutatesInsideQuotes("SIM"), steps=1, A=0.0).run()


def test_mm_peak_inventory_includes_intra_tick_round_trips():
    strategy = MarketMaker("SIM", quote_size=1.0, half_spread=0.0)
    result = MMSimulation(strategy, steps=1, A=1e308, kappa=0.0, seed=1).run()
    assert result.n_fills == 2
    assert result.inventory == [0.0]
    assert result.max_inventory == 1.0


def test_mm_arrival_probability_uses_horizon_scaled_intervals():
    coarse = MMSimulation(MarketMaker("SIM"), steps=100, A=2.0, kappa=0.0)
    fine = MMSimulation(MarketMaker("SIM"), steps=400, A=2.0, kappa=0.0)
    assert coarse._fill_prob(0.0) == pytest.approx(-math.expm1(-2.0 / 100))
    assert fine._fill_prob(0.0) == pytest.approx(-math.expm1(-2.0 / 400))
    assert (1 - coarse._fill_prob(0.0)) ** 100 == pytest.approx(math.exp(-2.0))
    assert (1 - fine._fill_prob(0.0)) ** 400 == pytest.approx(math.exp(-2.0))


@pytest.mark.parametrize("seed", [True, 1.5, math.nan, math.inf, -math.inf])
def test_mm_simulation_seed_must_be_a_deterministic_integer(seed):
    with pytest.raises(ValueError, match="seed"):
        MMSimulation(MarketMaker("SIM"), steps=3, seed=seed)


def test_mm_simulation_rejects_reuse_even_when_no_fill_occurs():
    strategy = MarketMaker("SIM", half_spread=10.0)
    MMSimulation(strategy, steps=1, A=0.0).run()
    with pytest.raises(ValueError, match="already been consumed"):
        MMSimulation(strategy, steps=1, A=0.0).run()
