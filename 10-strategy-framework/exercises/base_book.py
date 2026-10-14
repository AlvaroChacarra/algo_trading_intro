"""Level y OrderBook resueltos: niveles ordenados, mid e imbalance."""


class Level:
    def __init__(self, price, size):
        self.price = price
        self.size = size


class OrderBook:
    def __init__(self, bids, asks):
        self.bids = sorted(bids, key=lambda level: -level.price)
        self.asks = sorted(asks, key=lambda level: level.price)

    @property
    def mid(self):
        # Ejercicio 5.b: calcular desde los objetos actuales.
        if not self.bids or not self.asks:
            return None
        bid = self.bids[0].price
        ask = self.asks[0].price
        return (bid + ask) / 2

    def imbalance(self, levels=1):
        """Proporcionado: compara tamaños de los primeros levels de cada lado."""
        bid = sum(level.size for level in self.bids[:levels])
        ask = sum(level.size for level in self.asks[:levels])
        return (bid - ask) / (bid + ask) if bid + ask else None
