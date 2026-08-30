#!/usr/bin/env python3
"""Deterministic adversarial release fuzz for MatchingEngine.

The corpus combines extreme finite prices and sizes with late mutations made
after Order/Level construction. It verifies:

* every rejected case leaves the caller's book strictly unchanged;
* successful fills never exceed the exact binary parent quantity;
* FOK is either an exact full fill or an atomic no-op;
* mutated order/id/timestamp/book inputs are never accepted;
* successful books and fill identities retain their public invariants.

Canonical release invocation::

    python framework/_build/fuzz_matching.py --seed 20260828 --cases 120000

The JSON includes a SHA-256 digest of the generated cases before the engine
runs. Therefore the same seed, case count, Python runtime and harness revision
prove that the same corpus was exercised even if a stricter engine legitimately
moves cases from success to rejected.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import random
import sys


FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
if str(FRAMEWORK_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_ROOT))

from exchange.book import Level, OrderBook  # noqa: E402
from exchange.matching import MatchingEngine  # noqa: E402
from exchange.orders import Order, OrderType, Side  # noqa: E402


SCHEMA = "matching-fuzz/v1"
DEFAULT_SEED = 20_260_828
DEFAULT_CASES = 120_000
PRICE_BASES = (
    1e-300, 1e-200, 1e-100, 1e-10, 1.0,
    100.0, 1e10, 1e100, 1e200, 1e300,
)
SIZES = (
    math.nextafter(0.0, 1.0),
    1e-300, 1e-200, 1e-100, 1e-16, 1e-12, 1e-9, 1e-4,
    0.1, 0.3, 1.0, 3.0, 1e8, 1e16, 1e100, 1e200, 1e308,
)
# Seven none slots retain broad valid/numeric-boundary coverage while every
# named mutation remains frequent in the canonical 120k corpus.
MUTATIONS = (
    "none", "none", "none", "none", "none", "none", "none",
    "size-bool", "size-nan", "size-zero",
    "price-bool", "price-inf", "bad-side", "bad-type",
    "id-bool", "id-zero", "symbol-mismatch",
    "timestamp-bool", "timestamp-float",
    "book-size-nan", "book-price-bool",
)
INVALID_MUTATIONS = frozenset(MUTATIONS) - {"none"}


def _encoded(value: object) -> object:
    """Return a canonical, type-aware JSON representation."""
    if isinstance(value, Side):
        return {"enum": "Side", "value": value.value}
    if isinstance(value, OrderType):
        return {"enum": "OrderType", "value": value.value}
    if type(value) is float:
        return {"type": "float", "hex": value.hex()}
    if type(value) is bool:
        return {"type": "bool", "value": value}
    if type(value) is int:
        return {"type": "int", "value": value}
    if type(value) is str:
        return {"type": "str", "value": value}
    if value is None:
        return {"type": "none"}
    return {
        "type": f"{type(value).__module__}.{type(value).__qualname__}",
        "repr": repr(value),
    }


def _state_token(value: object) -> tuple[str, object]:
    """Hashable strict token used by the atomicity comparison."""
    encoded = _encoded(value)
    return type(value).__qualname__, json.dumps(
        encoded, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def _book_state(
    book: OrderBook,
) -> tuple[
    tuple[str, object],
    tuple[tuple[tuple[str, object], tuple[str, object]], ...],
    tuple[tuple[tuple[str, object], tuple[str, object]], ...],
]:
    def levels(values: list[Level]):
        return tuple(
            (_state_token(level.price), _state_token(level.size))
            for level in values
        )

    return _state_token(book.symbol), levels(book.bids), levels(book.asks)


def _choose_order_size(rng: random.Random, opposite: list[Level]) -> float:
    mode = rng.randrange(4)
    if opposite and mode == 0:
        return opposite[rng.randrange(len(opposite))].size
    if opposite and mode == 1:
        exact = sum(
            (Fraction.from_float(level.size) for level in opposite), Fraction()
        )
        try:
            candidate = float(exact)
        except OverflowError:
            candidate = math.inf
        if math.isfinite(candidate) and candidate > 0:
            return candidate
    if opposite and mode == 2:
        return opposite[0].size * 0.5
    return rng.choice(SIZES)


def _make_case(
    rng: random.Random,
    index: int,
) -> tuple[Order, OrderBook, object, str, dict[str, object]]:
    """Build one valid case, then apply exactly one selected late mutation."""
    base = rng.choice(PRICE_BASES)
    bid_depth = rng.randrange(6)
    ask_depth = rng.randrange(6)
    bids = [
        Level(base * (0.99 - 0.01 * level), rng.choice(SIZES))
        for level in range(bid_depth)
    ]
    asks = [
        Level(base * (1.01 + 0.01 * level), rng.choice(SIZES))
        for level in range(ask_depth)
    ]
    book = OrderBook("X", bids, asks)
    side = rng.choice((Side.BUY, Side.SELL))
    order_type = rng.choice(tuple(OrderType))
    opposite = book.asks if side is Side.BUY else book.bids
    size = _choose_order_size(rng, opposite)
    if not math.isfinite(size) or size <= 0:
        size = rng.choice((0.1, 1.0, 3.0))

    if order_type is OrderType.MARKET:
        price = None
    else:
        price_mode = rng.randrange(3)
        if opposite and price_mode == 0:
            price = opposite[rng.randrange(len(opposite))].price
        elif side is Side.BUY:
            price = base * (1.10 if price_mode == 1 else 0.90)
        else:
            price = base * (0.90 if price_mode == 1 else 1.10)

    # Explicit ids make corpus generation independent of the process-global
    # pedagogical id counter.
    order = Order("X", side, size, price, order_type, id=index + 1)
    timestamp: object = index
    mutation = rng.choice(MUTATIONS)

    if mutation == "size-bool":
        order.size = True
    elif mutation == "size-nan":
        order.size = math.nan
    elif mutation == "size-zero":
        order.size = 0.0
    elif mutation == "price-bool":
        order.price = True
        if order.order_type is OrderType.MARKET:
            order.order_type = OrderType.LIMIT
    elif mutation == "price-inf":
        order.price = math.inf
        if order.order_type is OrderType.MARKET:
            order.order_type = OrderType.LIMIT
    elif mutation == "bad-side":
        order.side = "hold"  # type: ignore[assignment]
    elif mutation == "bad-type":
        order.order_type = "gtc"  # type: ignore[assignment]
    elif mutation == "id-bool":
        order.id = True
    elif mutation == "id-zero":
        order.id = 0
    elif mutation == "symbol-mismatch":
        order.symbol = "Y"
    elif mutation == "timestamp-bool":
        timestamp = False
    elif mutation == "timestamp-float":
        timestamp = 1.5
    elif mutation == "book-size-nan":
        target = book.bids or book.asks
        if target:
            target[0].size = math.nan
        else:
            mutation = "none-empty-book"
    elif mutation == "book-price-bool":
        target = book.asks or book.bids
        if target:
            target[0].price = True
        else:
            mutation = "none-empty-book"

    spec = {
        "index": index,
        "base": _encoded(base),
        "bids": [
            [_encoded(level.price), _encoded(level.size)] for level in book.bids
        ],
        "asks": [
            [_encoded(level.price), _encoded(level.size)] for level in book.asks
        ],
        "order": {
            "id": _encoded(order.id),
            "symbol": _encoded(order.symbol),
            "side": _encoded(order.side),
            "type": _encoded(order.order_type),
            "size": _encoded(order.size),
            "price": _encoded(order.price),
        },
        "timestamp": _encoded(timestamp),
        "mutation": mutation,
    }
    return order, book, timestamp, mutation, spec


def _valid_output_book(book: OrderBook) -> bool:
    for values, reverse in ((book.bids, True), (book.asks, False)):
        prices = [level.price for level in values]
        if prices != sorted(prices, reverse=reverse):
            return False
        for level in values:
            if isinstance(level.price, bool) or isinstance(level.size, bool):
                return False
            if (not math.isfinite(level.price) or level.price <= 0
                    or not math.isfinite(level.size) or level.size <= 0):
                return False
    return True


def run_fuzz(*, seed: int = DEFAULT_SEED,
             cases: int = DEFAULT_CASES) -> dict[str, object]:
    """Generate the corpus, execute it and return deterministic audit evidence."""
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if isinstance(cases, bool) or not isinstance(cases, int) or cases <= 0:
        raise ValueError("cases must be a positive integer")

    rng = random.Random(seed)
    engine = MatchingEngine()
    digest = hashlib.sha256()
    success = rejected = 0
    non_atomic_rejections = overfills = fok_partials = 0
    fok_noop_violations = accepted_invalid_mutations = 0
    output_invariant_violations = fill_identity_violations = 0
    rejection_types: dict[str, int] = {}
    mutation_counts: dict[str, int] = {}

    for index in range(cases):
        order, book, timestamp, mutation, spec = _make_case(rng, index)
        encoded_case = json.dumps(
            spec, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        digest.update(encoded_case)
        digest.update(b"\n")
        mutation_counts[mutation] = mutation_counts.get(mutation, 0) + 1

        before = _book_state(book)
        original_size = order.size
        original_type = order.order_type
        try:
            fills = engine.process(
                order, book, timestamp=timestamp  # type: ignore[arg-type]
            )
        except (TypeError, ValueError, OverflowError) as error:
            rejected += 1
            error_name = type(error).__name__
            rejection_types[error_name] = rejection_types.get(error_name, 0) + 1
            if _book_state(book) != before:
                non_atomic_rejections += 1
            continue

        success += 1
        if mutation in INVALID_MUTATIONS:
            accepted_invalid_mutations += 1
        if not _valid_output_book(book):
            output_invariant_violations += 1
        if any(
            fill.order_id != order.id
            or fill.symbol != order.symbol
            or fill.side != order.side
            or fill.timestamp != timestamp
            for fill in fills
        ):
            fill_identity_violations += 1

        if (not isinstance(original_size, bool)
                and isinstance(original_size, (int, float))
                and math.isfinite(float(original_size))
                and float(original_size) > 0):
            exact_filled = sum(
                (Fraction.from_float(fill.size) for fill in fills), Fraction()
            )
            exact_requested = Fraction.from_float(float(original_size))
            if exact_filled > exact_requested:
                overfills += 1
            if original_type is OrderType.FOK:
                if exact_filled not in (Fraction(), exact_requested):
                    fok_partials += 1
                if exact_filled == 0 and _book_state(book) != before:
                    fok_noop_violations += 1

    invariant_counts = {
        "accepted_invalid_mutations": accepted_invalid_mutations,
        "fill_identity_violations": fill_identity_violations,
        "fok_noop_violations": fok_noop_violations,
        "fok_partials": fok_partials,
        "non_atomic_rejections": non_atomic_rejections,
        "output_invariant_violations": output_invariant_violations,
        "overfills": overfills,
    }
    ok = success + rejected == cases and not any(invariant_counts.values())
    return {
        "schema": SCHEMA,
        "seed": seed,
        "cases": cases,
        "case_digest_sha256": digest.hexdigest(),
        "success": success,
        "rejected": rejected,
        "rejection_types": dict(sorted(rejection_types.items())),
        "mutation_counts": dict(sorted(mutation_counts.items())),
        **invariant_counts,
        "ok": ok,
    }


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--cases", type=_positive_int, default=DEFAULT_CASES)
    args = parser.parse_args(argv)
    result = run_fuzz(seed=args.seed, cases=args.cases)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
