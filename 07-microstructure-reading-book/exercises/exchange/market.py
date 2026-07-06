"""market.py — el loop de simulación.

Construido en L9. Reproduce snapshots en orden, reconstruye el libro en cada
paso y acepta órdenes de la estrategia. Es la pieza que pone en marcha el
tiempo: book + matching + el flujo de órdenes ocurren aquí.
"""

from __future__ import annotations

import csv
import os

from exchange.book import OrderBook
from exchange.matching import MatchingEngine
from exchange.orders import Order
from exchange.trades import Fill


class Market:
    def __init__(self, symbol: str, snapshots: list[dict], depth: int = 10) -> None:
        self.symbol = symbol
        self._snapshots = snapshots
        self._depth = depth
        self._engine = MatchingEngine()
        self._i = -1
        self.book: OrderBook | None = None

    @classmethod
    def from_csv(cls, path: str, symbol: str = "BTCUSDT", depth: int = 10) -> "Market":
        with open(path, newline="") as f:
            rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]
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
        if 0 <= self._i < len(self._snapshots):
            return int(self._snapshots[self._i].get("timestamp", self._i))
        return None

    def __len__(self) -> int:
        return len(self._snapshots)

    def step(self) -> OrderBook | None:
        """Avanza al siguiente snapshot. Devuelve el libro o None si se acabó."""
        self._i += 1
        if self._i >= len(self._snapshots):
            self.book = None
            return None
        self.book = OrderBook.from_snapshot(
            self.symbol, self._snapshots[self._i], self._depth)
        return self.book

    def submit(self, order: Order) -> list[Fill]:
        """Envía una orden contra el libro actual."""
        if self.book is None:
            raise RuntimeError("no hay libro activo: llama a step() primero")
        return self._engine.process(order, self.book, self.timestamp)

    def reset(self) -> None:
        self._i = -1
        self.book = None
