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
        self.fills = []

    def on_book_update(self, book):
        self._t += 1
        if self._t == self.step:
            return [NewOrder(Order("BTCUSDT", "buy", self.size,
                                   order_type=OrderType.MARKET))]
        return []

    def on_fill(self, fill):
        self.fills.append({"i": self._t - 1, "price": round(fill.price, 2),
                           "size": round(fill.size, 4)})


def build() -> dict:
    strat = BuyAt(step=50, size=0.5)
    sample = Market.sample()
    anatomy = []
    for i, row in enumerate(sample._snapshots[:4]):
        book = sample.step()
        anatomy.append({
            "i": i,
            "timestamp": int(row.get("timestamp", i)),
            "bestBid": book.best_bid,
            "bestAsk": book.best_ask,
            "mid": book.mid,
        })
    res = Backtest(Market.sample(), strat).run()
    return {
        "anatomy": anatomy,
        "equity": [round(x, 2) for x in res.equity_curve],
        "fills": strat.fills,
        "filled": round(sum(f["size"] for f in strat.fills), 4),
        "steps": res.n_steps, "nFills": res.n_fills,
        "finalEquity": round(res.final_equity, 2),
        "finalPos": round(res.final_position, 4),
    }
