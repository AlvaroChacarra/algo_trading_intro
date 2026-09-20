"""OrderBook snapshot for L5-L6: composition and stable read-only metrics."""

from __future__ import annotations


class Level:
    """One price level; L7 expresses the same constructor as a dataclass."""

    def __init__(self, price: float, size: float) -> None:
        self.price = price
        self.size = size


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
        return (self.best_bid + self.best_ask) / 2

    def imbalance(self, levels: int = 1) -> float | None:
        bid_vol = sum(lv.size for lv in self.bids[:levels])
        ask_vol = sum(lv.size for lv in self.asks[:levels])
        total = bid_vol + ask_vol
        return None if total == 0 else (bid_vol - ask_vol) / total

    def __repr__(self) -> str:
        bb = f"{self.best_bid:g}" if self.best_bid is not None else "-"
        ba = f"{self.best_ask:g}" if self.best_ask is not None else "-"
        return f"OrderBook({self.symbol} {bb} / {ba}, spread={self.spread})"
