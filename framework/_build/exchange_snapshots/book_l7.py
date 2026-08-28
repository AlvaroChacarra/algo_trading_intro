"""OrderBook snapshot for L7: external rows and read-only book metrics."""

from __future__ import annotations

from dataclasses import dataclass

from exchange.orders import Side


@dataclass
class Level:
    price: float
    size: float


class OrderBook:
    def __init__(self, symbol: str, bids: list[Level], asks: list[Level]) -> None:
        self.symbol = symbol
        self.bids = sorted(bids, key=lambda lv: -lv.price)
        self.asks = sorted(asks, key=lambda lv: lv.price)

    @classmethod
    def from_snapshot(cls, symbol: str, row: dict, depth: int = 10) -> "OrderBook":
        bids, asks = [], []
        for i in range(1, depth + 1):
            bp, bs = row.get(f"bid_price_{i}"), row.get(f"bid_size_{i}")
            ap, as_ = row.get(f"ask_price_{i}"), row.get(f"ask_size_{i}")
            if bp is not None and bs is not None and float(bs) > 0:
                bids.append(Level(float(bp), float(bs)))
            if ap is not None and as_ is not None and float(as_) > 0:
                asks.append(Level(float(ap), float(as_)))
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
        return (self.best_bid + self.best_ask) / 2

    @property
    def microprice(self) -> float | None:
        if not self.bids or not self.asks:
            return None
        bid_size, ask_size = self.bids[0].size, self.asks[0].size
        return (
            self.best_bid * ask_size + self.best_ask * bid_size
        ) / (bid_size + ask_size)

    def imbalance(self, levels: int = 1) -> float | None:
        bid_vol = self.depth(Side.BUY, levels)
        ask_vol = self.depth(Side.SELL, levels)
        total = bid_vol + ask_vol
        return None if total == 0 else (bid_vol - ask_vol) / total

    def depth(self, side: Side, levels: int = 10) -> float:
        side = Side(side)
        book_side = self.bids if side is Side.BUY else self.asks
        return sum(lv.size for lv in book_side[:levels])

    def __repr__(self) -> str:
        bb = f"{self.best_bid:g}" if self.best_bid is not None else "-"
        ba = f"{self.best_ask:g}" if self.best_ask is not None else "-"
        return f"OrderBook({self.symbol} {bb} / {ba}, spread={self.spread})"
