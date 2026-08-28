# Clase 11 - El juicio: senal vs mono, arrival y slippage. En un .py.
# Ejecuta desde exercises/:  python judge.py

import random

from exchange.backtest import Backtest
from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.strategy import NewOrder, Strategy


class ImbalanceStrategy(Strategy):
    def __init__(self, thr=0.5, clip=0.05, max_pos=0.5):
        self.thr, self.clip, self.max_pos = thr, clip, max_pos
        self._pos, self._mid, self.slips = 0.0, None, []

    def on_book_update(self, book):
        self._mid = book.mid
        imb = book.imbalance(1)
        if imb is None:
            return []
        if imb > self.thr and self._pos < self.max_pos:
            return [NewOrder(Order("BTCUSDT", "buy", self.clip,
                                   order_type=OrderType.MARKET))]
        if imb < -self.thr and self._pos > -self.max_pos:
            return [NewOrder(Order("BTCUSDT", "sell", self.clip,
                                   order_type=OrderType.MARKET))]
        return []

    def on_fill(self, fill):
        self._pos += fill.size if fill.side == "buy" else -fill.size
        sign = 1 if fill.side == "buy" else -1
        self.slips.append(sign * (fill.price - self._mid))


class RandomStrategy(Strategy):
    """El mono con dardos: misma municion, cero senal."""

    def __init__(self, seed, p=0.06, clip=0.05, max_pos=0.5):
        self.rng, self.p, self.clip, self.max_pos = random.Random(seed), p, clip, max_pos
        self._pos = 0.0

    def on_book_update(self, book):
        if self.rng.random() > self.p:
            return []
        side = self.rng.choice(["buy", "sell"])
        if side == "buy" and self._pos >= self.max_pos:
            return []
        if side == "sell" and self._pos <= -self.max_pos:
            return []
        return [NewOrder(Order("BTCUSDT", side, self.clip,
                               order_type=OrderType.MARKET))]

    def on_fill(self, fill):
        self._pos += fill.size if fill.side == "buy" else -fill.size


def main():
    parent_arrival = Market.sample().step().mid
    print(f"parent-order arrival mid: {parent_arrival:.2f}")

    signal = ImbalanceStrategy()
    res = Backtest(Market.sample(), signal).run()
    avg_slip = sum(signal.slips) / len(signal.slips)
    cost = avg_slip * len(signal.slips) * signal.clip
    print(f"senal : equity={res.final_equity:>7.2f}  fills={res.n_fills}  "
          f"child slippage medio={avg_slip:.2f}  coste ejecucion~{cost:.1f}")
    print(f"bruto sin peaje ~ {res.final_equity + cost:.1f}")

    for seed in (7, 21, 99):
        r = Backtest(Market.sample(), RandomStrategy(seed)).run()
        print(f"mono {seed:>3}: equity={r.final_equity:>7.2f}  fills={r.n_fills}")


if __name__ == "__main__":
    main()
