"""Regression tests for the cumulative public API shipped with each lesson."""

from __future__ import annotations

import copy
import os
from pathlib import Path
import subprocess
import sys

import pytest


BUILD = Path(__file__).resolve().parents[1] / "_build"
sys.path.insert(0, str(BUILD))
import build_course  # noqa: E402
from build_course import modules_for, stage_package  # noqa: E402


ROOT_SYMBOLS_BY_LESSON = {
    4: {"Order", "Side", "OrderType", "Fill"},
    5: {"OrderBook", "Level", "PositionTracker"},
    8: {"MatchingEngine"},
    9: {"Market"},
    10: {"Strategy", "NewOrder", "Cancel", "Action", "Backtest", "BacktestResult"},
}
STRATEGY_SYMBOLS_BY_LESSON = {
    12: {"VWAPStrategy"},
    13: {"MarketMaker"},
    14: {"AvellanedaStoikov"},
}
CORE_FILES_BY_LESSON = {
    4: {"orders.py", "trades.py"},
    5: {"book.py", "portfolio.py"},
    8: {"matching.py"},
    9: {"market.py"},
    10: {"strategy.py", "backtest.py"},
    13: {"simulation.py"},
}
STRATEGY_FILES_BY_LESSON = {
    12: {"vwap.py"},
    13: {"market_maker.py"},
    14: {"avellaneda_stoikov.py"},
}


def _through(mapping: dict[int, set[str]], lesson: int) -> set[str]:
    return set().union(*(names for first, names in mapping.items() if lesson >= first))


def _assert_import_surface(exercises: Path, lesson: int) -> None:
    expected_root = sorted(_through(ROOT_SYMBOLS_BY_LESSON, lesson))
    future_root = sorted(_through(ROOT_SYMBOLS_BY_LESSON, 14) - set(expected_root))
    expected_strategies = sorted(_through(STRATEGY_SYMBOLS_BY_LESSON, lesson))
    future_strategies = sorted(
        _through(STRATEGY_SYMBOLS_BY_LESSON, 14) - set(expected_strategies)
    )
    script = f"""
import exchange

for name in {expected_root!r}:
    assert hasattr(exchange, name), f"missing root symbol: {{name}}"
for name in {future_root!r}:
    assert not hasattr(exchange, name), f"future root symbol leaked: {{name}}"

expected_strategies = {expected_strategies!r}
if expected_strategies:
    import exchange.strategies as strategies
    for name in expected_strategies:
        assert hasattr(strategies, name), f"missing strategy symbol: {{name}}"
    for name in {future_strategies!r}:
        assert not hasattr(strategies, name), f"future strategy leaked: {{name}}"
else:
    try:
        import exchange.strategies
    except ModuleNotFoundError:
        pass
    else:
        raise AssertionError("strategies package leaked before L12")
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(exercises)
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=exercises,
        env=env,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.parametrize("lesson", range(1, 15))
def test_snapshot_exposes_only_the_surface_available_in_that_lesson(
    tmp_path: Path, lesson: int
) -> None:
    exercises = tmp_path / f"L{lesson:02d}" / "exercises"
    exercises.mkdir(parents=True)

    has_package = stage_package(lesson, str(exercises))
    package = exercises / "exchange"
    assert has_package is (lesson >= 4)
    assert package.exists() is (lesson >= 4)
    if lesson < 4:
        return

    expected_core = {"__init__.py"} | _through(CORE_FILES_BY_LESSON, lesson)
    assert {path.name for path in package.glob("*.py")} == expected_core

    strategy_dir = package / "strategies"
    expected_strategy_files = _through(STRATEGY_FILES_BY_LESSON, lesson)
    if expected_strategy_files:
        assert {path.name for path in strategy_dir.glob("*.py")} == (
            {"__init__.py"} | expected_strategy_files
        )
    else:
        assert not strategy_dir.exists()

    assert (package / "_data" / "btc_lob_snapshots.csv").exists() is (lesson >= 7)
    _assert_import_surface(exercises, lesson)


def test_l13_does_not_leak_l14_model(tmp_path: Path) -> None:
    exercises = tmp_path / "exercises"
    exercises.mkdir()
    stage_package(13, str(exercises))

    strategies = exercises / "exchange" / "strategies"
    market_maker = (strategies / "market_maker.py").read_text(encoding="utf-8")
    assert not (strategies / "avellaneda_stoikov.py").exists()
    assert "class AvellanedaStoikov" not in market_maker
    assert "def optimal_spread" not in market_maker


@pytest.mark.parametrize(
    ("lesson", "present", "absent"),
    [
        (5, {"best_bid", "best_ask", "spread", "mid", "imbalance"},
         {"from_snapshot", "depth", "microprice", "add_limit", "reduce"}),
        (7, {"from_snapshot", "depth", "microprice"}, {"add_limit", "reduce"}),
        (8, {"from_snapshot", "depth", "microprice", "add_limit", "reduce"}, set()),
    ],
)
def test_orderbook_method_surface_appears_only_at_its_lesson(
    tmp_path: Path, lesson: int, present: set[str], absent: set[str]
) -> None:
    exercises = tmp_path / "exercises"
    exercises.mkdir()
    stage_package(lesson, str(exercises))
    script = f"""
from exchange.book import OrderBook
for name in {sorted(present)!r}:
    assert hasattr(OrderBook, name), f"missing {{name}}"
for name in {sorted(absent)!r}:
    assert not hasattr(OrderBook, name), f"future method leaked: {{name}}"
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(exercises)
    proc = subprocess.run(
        [sys.executable, "-c", script], cwd=exercises, env=env,
        text=True, capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.parametrize(
    ("lesson", "has_matching_policies"),
    [(4, False), (5, False), (6, False), (7, False), (8, True)],
)
def test_order_policy_surface_appears_only_in_l8(
    tmp_path: Path, lesson: int, has_matching_policies: bool
) -> None:
    exercises = tmp_path / "exercises"
    exercises.mkdir()
    stage_package(lesson, str(exercises))
    script = f"""
from exchange.orders import OrderType, Side
assert hasattr(Side, 'opposite') is {has_matching_policies!r}
assert hasattr(OrderType, 'IOC') is {has_matching_policies!r}
assert hasattr(OrderType, 'FOK') is {has_matching_policies!r}
assert hasattr(OrderType, 'LIMIT') and hasattr(OrderType, 'MARKET')
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(exercises)
    proc = subprocess.run(
        [sys.executable, "-c", script], cwd=exercises, env=env,
        text=True, capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_self_test_executes_against_each_lesson_snapshot(monkeypatch) -> None:
    lesson = copy.deepcopy(next(item for item in build_course.LESSONS if item["n"] == 5))
    exercise = next(
        item for item in lesson["aux"]
        if item.get("title") == "A12. Los objetos reales del paquete"
    )
    exercise["given"] = ""
    exercise["solution"] = (
        "from exchange.strategies import AvellanedaStoikov\n"
        "future = AvellanedaStoikov('BTC')"
    )
    exercise["validator"] = "assert future is not None"
    monkeypatch.setattr(build_course, "LESSONS", [lesson])

    failures = build_course.self_test()
    assert any("exchange.strategies" in failure for failure in failures)


def test_early_snapshot_removes_stale_future_package(tmp_path: Path) -> None:
    exercises = tmp_path / "exercises"
    exercises.mkdir()
    stage_package(14, str(exercises))
    assert (exercises / "exchange" / "strategies" / "avellaneda_stoikov.py").exists()

    assert stage_package(1, str(exercises)) is False
    assert not (exercises / "exchange").exists()


def test_modules_for_places_market_making_model_only_in_l14() -> None:
    _, l13_strategies, _ = modules_for(13)
    _, l14_strategies, _ = modules_for(14)
    assert ("market_maker", "MarketMaker") in l13_strategies
    assert all(name != "avellaneda_stoikov" for name, _ in l13_strategies)
    assert ("avellaneda_stoikov", "AvellanedaStoikov") in l14_strategies
