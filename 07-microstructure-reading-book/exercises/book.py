"""Un libro consultable. Level y OrderBook están incluidos en base_book.py."""
from base_book import OrderBook
from adapters import levels_from_snapshot


class SnapshotBook(OrderBook):
    def __init__(self, symbol, bids, asks):
        self.symbol = symbol
        super().__init__(bids, asks)

    @classmethod
    def from_snapshot(cls, symbol, row, depth=10):
        # TODO · Ejercicio 3A: fabrica el libro con levels_from_snapshot y devuelve cls(symbol, bids, asks).
        pass

    @property
    def best_bid(self):
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self):
        return self.asks[0].price if self.asks else None

    @property
    def spread(self):
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid

    def depth(self, side, levels=10):
        # TODO · Ejercicio 4A: suma size en los primeros levels del lado buy/sell; rechaza otros lados.
        pass

    def imbalance(self, levels=1):
        # TODO · Ejercicio 4B: compón depth para calcular (bid - ask) / (bid + ask); total cero devuelve None.
        pass

    @property
    def microprice(self):
        # TODO · Ejercicio 4C: calcula microprice con pesos cruzados; un lado vacío devuelve None.
        pass
