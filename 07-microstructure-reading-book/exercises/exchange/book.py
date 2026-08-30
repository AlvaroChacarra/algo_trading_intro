"""OrderBook snapshot for L7: external rows and read-only book metrics."""

from __future__ import annotations

from dataclasses import dataclass
import math

from exchange.orders import Side


@dataclass
class Level:
    price: float
    size: float

    def __post_init__(self) -> None:
        if isinstance(self.price, bool) or isinstance(self.size, bool):
            raise ValueError("level price and size must be numeric, not boolean")
        self.price = float(self.price)
        self.size = float(self.size)
        if not math.isfinite(self.price) or self.price <= 0:
            raise ValueError("level price must be finite and positive")
        if not math.isfinite(self.size) or self.size <= 0:
            raise ValueError("level size must be finite and positive")


class OrderBook:
    def __init__(self, symbol: str, bids: list[Level], asks: list[Level]) -> None:
        self.symbol = symbol
        self.bids = sorted(bids, key=lambda lv: -lv.price)
        self.asks = sorted(asks, key=lambda lv: lv.price)

    @classmethod
    def from_snapshot(cls, symbol: str, row: dict, depth: int = 10) -> "OrderBook":
        if isinstance(depth, bool) or not isinstance(depth, int) or depth <= 0:
            raise ValueError("depth must be a positive integer")
        bids, asks = [], []
        for i in range(1, depth + 1):
            bp, bs = row.get(f"bid_price_{i}"), row.get(f"bid_size_{i}")
            ap, as_ = row.get(f"ask_price_{i}"), row.get(f"ask_size_{i}")
            for price, size, destination in ((bp, bs, bids), (ap, as_, asks)):
                if price is None or size is None:
                    continue
                if isinstance(price, bool) or isinstance(size, bool):
                    raise ValueError("snapshot levels must be numeric, not boolean")
                numeric_size = float(size)
                if not math.isfinite(numeric_size) or numeric_size < 0:
                    raise ValueError("snapshot level size must be finite and non-negative")
                if numeric_size == 0:
                    continue
                destination.append(Level(float(price), numeric_size))
        return cls(symbol, bids, asks)

    @property
    def best_bid(self) -> float | None:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> float | None:
        return self.asks[0].price if self.asks else None

    @property
    def spread(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid

    @property
    def mid(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_bid + (self.best_ask - self.best_bid) / 2

    @property
    def microprice(self) -> float | None:
        if not self.bids or not self.asks:
            return None
        bid_size, ask_size = self.bids[0].size, self.asks[0].size
        scale = max(bid_size, ask_size)
        bid_weight = ask_size / scale
        ask_weight = bid_size / scale
        ask_share = ask_weight / (bid_weight + ask_weight)
        return self.best_bid + (self.best_ask - self.best_bid) * ask_share

    def imbalance(self, levels: int = 1) -> float | None:
        bid_vol = self.depth(Side.BUY, levels)
        ask_vol = self.depth(Side.SELL, levels)
        scale = max(bid_vol, ask_vol)
        if scale == 0:
            return None
        scaled_bid, scaled_ask = bid_vol / scale, ask_vol / scale
        return (scaled_bid - scaled_ask) / (scaled_bid + scaled_ask)

    def depth(self, side: Side, levels: int = 10) -> float:
        if isinstance(levels, bool) or not isinstance(levels, int) or levels <= 0:
            raise ValueError("levels must be a positive integer")
        side = Side(side)
        book_side = self.bids if side is Side.BUY else self.asks
        return math.fsum(lv.size for lv in book_side[:levels])

    def __repr__(self) -> str:
        bb = f"{self.best_bid:g}" if self.best_bid is not None else "-"
        ba = f"{self.best_ask:g}" if self.best_ask is not None else "-"
        return f"OrderBook({self.symbol} {bb} / {ba}, spread={self.spread})"
