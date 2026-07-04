"""Datos reales para el doc de L9: un día completo por el loop, con su equity."""
from exchange.backtest import Backtest
from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.strategy import NewOrder, Strategy


class BuyAt(Strategy):
    def __init__(self, step: int, size: float) -> None:
        self.step = step
        self.size = size
        self._t = 0
        self.fill_info = None

    def on_book_update(self, book):
        self._t += 1
        if self._t == self.step:
            return [NewOrder(Order("BTCUSDT", "buy", self.size,
                                   order_type=OrderType.MARKET))]
        return []

    def on_fill(self, fill):
        self.fill_info = {"i": self._t - 1, "price": round(fill.price, 2),
                          "size": fill.size}


def build() -> dict:
    strat = BuyAt(step=50, size=0.5)
    res = Backtest(Market.sample(), strat).run()
    return {
        "equity": [round(x, 2) for x in res.equity_curve],
        "fill": strat.fill_info,
        "steps": res.n_steps, "nFills": res.n_fills,
        "finalEquity": round(res.final_equity, 2),
        "finalPos": round(res.final_position, 4),
    }
