"""market.py — el loop de simulación.

Construido en L9. Reproduce snapshots en orden, reconstruye el libro en cada
paso y acepta órdenes de la estrategia. Es la pieza que pone en marcha el
tiempo: book + matching + el flujo de órdenes ocurren aquí.
"""

from __future__ import annotations

from copy import deepcopy
import csv
from decimal import Decimal, InvalidOperation
import math
import os
from types import MappingProxyType

from exchange.book import OrderBook
from exchange.matching import MatchingEngine
from exchange.orders import Order
from exchange.trades import Fill


class _FrozenList(tuple):
    """Tagged immutable form of a list inside an owned replay row."""


class _FrozenTuple(tuple):
    """Tagged immutable form of a tuple inside an owned replay row."""


def _freeze_snapshot_value(value):
    """Own and recursively seal JSON-like replay data."""
    if isinstance(value, dict):
        return MappingProxyType({
            deepcopy(key): _freeze_snapshot_value(item)
            for key, item in value.items()
        })
    if isinstance(value, list):
        return _FrozenList(_freeze_snapshot_value(item) for item in value)
    if isinstance(value, tuple):
        return _FrozenTuple(_freeze_snapshot_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze_snapshot_value(item) for item in value)
    return deepcopy(value)


def _thaw_snapshot_value(value):
    """Return a detached value with the caller-visible container types."""
    if isinstance(value, MappingProxyType):
        return {
            deepcopy(key): _thaw_snapshot_value(item)
            for key, item in value.items()
        }
    if isinstance(value, _FrozenList):
        return [_thaw_snapshot_value(item) for item in value]
    if isinstance(value, _FrozenTuple):
        return tuple(_thaw_snapshot_value(item) for item in value)
    if isinstance(value, frozenset):
        return {_thaw_snapshot_value(item) for item in value}
    return deepcopy(value)


def _integer_timestamp(value) -> int:
    """Return an exact integer timestamp without a lossy float round-trip."""
    if isinstance(value, bool):
        raise ValueError("snapshot timestamp must be an integer, not boolean")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value) or not value.is_integer():
            raise ValueError("snapshot timestamp must be a finite integer")
        return int(value)
    if isinstance(value, str):
        try:
            numeric = Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("snapshot timestamp must be an integer") from exc
        if not numeric.is_finite() or numeric != numeric.to_integral_value():
            raise ValueError("snapshot timestamp must be a finite integer")
        return int(numeric)
    raise ValueError("snapshot timestamp must be an integer")


class Market:
    book: OrderBook | None

    def __init__(self, symbol: str, snapshots: list[dict], depth: int = 10) -> None:
        if isinstance(depth, bool) or not isinstance(depth, int) or depth <= 0:
            raise ValueError("depth must be a positive integer")
        self.symbol = symbol
        # Own and recursively seal the replay.  This makes the authoritative
        # rows immutable even when a strategy retained an alias to ``Market``;
        # the public property below still returns ordinary detached containers.
        self._snapshots = tuple(
            _freeze_snapshot_value(snapshot) for snapshot in snapshots
        )
        self._depth = depth
        self._engine = MatchingEngine()
        self._i = -1
        self._timestamp: int | None = None
        self.book: OrderBook | None = None

    @classmethod
    def from_csv(cls, path: str, symbol: str = "BTCUSDT", depth: int = 10) -> "Market":
        with open(path, newline="") as f:
            rows = []
            for row in csv.DictReader(f):
                converted = {
                    key: (_integer_timestamp(value) if key == "timestamp"
                          else float(value))
                    for key, value in row.items()
                }
                rows.append(converted)
        return cls(symbol, rows, depth)

    @classmethod
    def sample(cls, symbol: str = "BTCUSDT", depth: int = 10) -> "Market":
        """Mercado de ejemplo: 500 snapshots de BTCUSDT empaquetados con el curso.

        Funciona sin configurar rutas: `Market.sample()` y a correr.
        """
        here = os.path.dirname(__file__)
        return cls.from_csv(os.path.join(here, "_data", "btc_lob_snapshots.csv"),
                            symbol, depth)

    @property
    def timestamp(self) -> int | None:
        return self._timestamp

    @property
    def snapshots(self) -> list[dict]:
        """Return a deep defensive copy for guided replay exercises.

        The public API intentionally remains ``list[dict]`` so existing lesson
        slicing keeps working, while mutations at any nesting depth cannot
        alter the replay or a later read of this property.
        """
        return [_thaw_snapshot_value(snapshot) for snapshot in self._snapshots]

    def __len__(self) -> int:
        return len(self._snapshots)

    @property
    def is_fresh(self) -> bool:
        """Whether no snapshot has been consumed in this replay lifecycle."""
        return self._i == -1 and self.book is None

    def step(self) -> OrderBook | None:
        """Advance atomically: an invalid next row leaves current state intact."""
        next_i = self._i + 1
        if next_i >= len(self._snapshots):
            self._i = next_i
            self._timestamp = None
            self.book = None
            return None

        snapshot = self._snapshots[next_i]
        next_book = OrderBook.from_snapshot(self.symbol, snapshot, self._depth)
        raw_timestamp = snapshot.get("timestamp", next_i)
        next_timestamp = _integer_timestamp(raw_timestamp)

        self._i = next_i
        self._timestamp = next_timestamp
        self.book = next_book
        return next_book

    def submit(self, order: Order) -> list[Fill]:
        """Envía una orden contra el libro actual."""
        if self.book is None:
            raise RuntimeError("no hay libro activo: llama a step() primero")
        return self._engine.process(order, self.book, self.timestamp)

    def reset(self) -> None:
        self._i = -1
        self._timestamp = None
        self.book = None
