"""OrderBook snapshot for L5-L6: composition and stable read-only metrics."""

from __future__ import annotations

import math


class Level:
    """One price level; L7 expresses the same constructor as a dataclass."""

    def __init__(self, price: float, size: float) -> None:
        if isinstance(price, bool) or isinstance(size, bool):
            raise ValueError("level price and size must be numeric, not boolean")
        self.price = float(price)
        self.size = float(size)
        if not math.isfinite(self.price) or self.price <= 0:
            raise ValueError("level price must be finite and positive")
        if not math.isfinite(self.size) or self.size <= 0:
            raise ValueError("level size must be finite and positive")


class OrderBook:
    def __init__(self, symbol: str, bids: list[Level], asks: list[Level]) -> None:
        self.symbol = symbol
        self.bids = sorted(bids, key=lambda lv: -lv.price)
        self.asks = sorted(asks, key=lambda lv: lv.price)

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

    def imbalance(self, levels: int = 1) -> float | None:
        if isinstance(levels, bool) or not isinstance(levels, int) or levels <= 0:
            raise ValueError("levels must be a positive integer")
        bid_vol = math.fsum(lv.size for lv in self.bids[:levels])
        ask_vol = math.fsum(lv.size for lv in self.asks[:levels])
        scale = max(bid_vol, ask_vol)
        if scale == 0:
            return None
        scaled_bid, scaled_ask = bid_vol / scale, ask_vol / scale
        return (scaled_bid - scaled_ask) / (scaled_bid + scaled_ask)

    def __repr__(self) -> str:
        bb = f"{self.best_bid:g}" if self.best_bid is not None else "-"
        ba = f"{self.best_ask:g}" if self.best_ask is not None else "-"
        return f"OrderBook({self.symbol} {bb} / {ba}, spread={self.spread})"
