"""Datos sintéticos para el doc de L10: dos estrategias distintas por el MISMO
Backtest.run() — el polimorfismo contra un replay reproducible."""
from exchange.backtest import Backtest
from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.strategy import NewOrder, Strategy


class BuyOnce(Strategy):
    def __init__(self, size=0.5):
        self.size = size
        self._done = False

    def on_book_update(self, book):
        if self._done:
            return []
        self._done = True
        return [NewOrder(Order("BTCUSDT", "buy", self.size,
                               order_type=OrderType.MARKET))]


class ImbalanceStrategy(Strategy):
    def __init__(self, thr=0.5, clip=0.05, max_pos=0.5):
        self.thr = thr
        self.clip = clip
        self.max_pos = max_pos
        self._pos = 0.0

    def on_book_update(self, book):
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


def run(strategy):
    res = Backtest(Market.sample(), strategy).run()
    return {"equity": [round(x, 2) for x in res.equity_curve],
            "nFills": res.n_fills,
            "finalEquity": round(res.final_equity, 2),
            "finalPos": round(res.final_position, 4)}


def build() -> dict:
    return {"buyonce": run(BuyOnce()), "imbalance": run(ImbalanceStrategy())}
