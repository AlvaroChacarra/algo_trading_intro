# book_demo.py - clase 5: composicion y encapsulacion.
# OrderBookMini CONTIENE niveles; PositionTracker LLEVA LA CUENTA. Ejecuta: python book_demo.py
from exchange.trades import Fill


class OrderBookMini:
    def __init__(self, bids, asks):                  # ej. 1: contiene niveles
        self.bids = sorted(bids, key=lambda x: -x[0])
        self.asks = sorted(asks, key=lambda x: x[0])

    @property
    def best_bid(self):                              # ej. 2
        return self.bids[0][0]

    @property
    def best_ask(self):
        return self.asks[0][0]

    @property
    def mid(self):
        return (self.best_bid + self.best_ask) / 2


class PositionTracker:
    def __init__(self):                              # ej. 4: estado interno
        self._cash = 0.0
        self._position = 0.0

    def apply_fill(self, fill):
        self._cash += fill.cash_flow()
        self._position += fill.size if fill.side == "buy" else -fill.size

    def equity(self, mark_price):                    # ej. 5
        return self._cash + self._position * mark_price


def main():                                          # ej. 6: los dos juntos
    book = OrderBookMini([(99990, 2.0), (99980, 1.0)], [(100010, 1.5)])
    print("mid:", book.mid)

    tracker = PositionTracker()
    tracker.apply_fill(Fill(1, "BTCUSDT", "buy", 100000, 0.5))
    tracker.apply_fill(Fill(2, "BTCUSDT", "sell", 100050, 0.2))
    print("cash:", round(tracker._cash, 2), "| position:", tracker._position)
    print("equity @ mid:", round(tracker.equity(book.mid), 2))
    # La versión Mini fija la idea; A12 muestra la migración a exchange.OrderBook.


if __name__ == "__main__":
    main()
