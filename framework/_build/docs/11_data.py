"""Datos reales para el doc de L11: la estrategia con señal contra el mono
aleatorio, y el coste de ejecución medido contra el mid de llegada."""
import random

from exchange.backtest import Backtest
from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.strategy import NewOrder, Strategy


class ImbalanceStrategy(Strategy):
    def __init__(self, thr=0.5, clip=0.05, max_pos=0.5):
        self.thr = thr
        self.clip = clip
        self.max_pos = max_pos
        self._pos = 0.0
        self._mid = None
        self.slips = []          # fill.price - mid en el momento de decidir

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
        if self._mid is not None:
            sign = 1 if fill.side == "buy" else -1
            self.slips.append(round(sign * (fill.price - self._mid), 2))


class RandomStrategy(Strategy):
    """El mono con dardos: mismas armas, cero señal."""

    def __init__(self, p=0.06, clip=0.05, max_pos=0.5, seed=7):
        self.p = p
        self.clip = clip
        self.max_pos = max_pos
        self.rng = random.Random(seed)
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


def build() -> dict:
    sig = ImbalanceStrategy()
    r_sig = Backtest(Market.sample(), sig).run()
    mono_curves, mono_finals = [], []
    for seed in (7, 21, 99):
        r = Backtest(Market.sample(), RandomStrategy(seed=seed)).run()
        mono_curves.append([round(x, 2) for x in r.equity_curve])
        mono_finals.append(round(r.final_equity, 2))
    m = Market.sample()
    m.step()
    arrival = m.book.mid
    avg_slip = sum(sig.slips) / len(sig.slips) if sig.slips else 0.0
    return {
        "signal": {"equity": [round(x, 2) for x in r_sig.equity_curve],
                   "nFills": r_sig.n_fills,
                   "finalEquity": round(r_sig.final_equity, 2),
                   "finalPos": round(r_sig.final_position, 4)},
        "monos": mono_curves, "monoFinals": mono_finals,
        "arrivalMid": round(arrival, 2),
        "avgSlip": round(avg_slip, 3), "nSlips": len(sig.slips),
    }
