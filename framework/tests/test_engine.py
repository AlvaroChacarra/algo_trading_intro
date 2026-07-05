"""Tests de invariantes del motor exchange/ — los bordes que el camino feliz no pisa.

Ejecutar desde framework/:  python -m pytest tests/ -q
"""

import random

import pytest

from exchange.book import Level, OrderBook
from exchange.market import Market
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType, Side
from exchange.portfolio import PositionTracker
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


def test_limit_that_does_not_cross_only_rests():
    book = make_book()
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", 0.2, price=99900, order_type=OrderType.LIMIT), book)
    assert fills == []
    assert any(lv.price == 99900 for lv in book.bids)


# ── Order ───────────────────────────────────────────────────────────────────

def test_order_validation():
    with pytest.raises(ValueError):
        Order("BTCUSDT", "buy", 0.0, price=100)          # size <= 0
    with pytest.raises(ValueError):
        Order("BTCUSDT", "buy", 1.0)                     # LIMIT sin precio
    assert Order("BTCUSDT", "buy", 1.0, order_type="market").price is None


def test_side_enum_compares_with_str():
    assert Side.BUY == "buy" and Side.BUY.opposite == "sell"


# ── PositionTracker ─────────────────────────────────────────────────────────

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


# ── Market ──────────────────────────────────────────────────────────────────

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
