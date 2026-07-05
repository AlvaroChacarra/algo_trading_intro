# Clase 10 - Strategy + Backtest, en un archivo .py
# Dos estrategias por el MISMO runner: el polimorfismo es el enchufe.
# Ejecuta desde exercises/:  python run_backtest.py

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
        self.thr, self.clip, self.max_pos = thr, clip, max_pos
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


def main():
    for strategy in (BuyOnce(), ImbalanceStrategy()):
        result = Backtest(Market.sample(), strategy).run()
        print(f"{type(strategy).__name__:>18}: {result}")
    print("lineas del motor tocadas para cambiar de estrategia: 0")


if __name__ == "__main__":
    main()
