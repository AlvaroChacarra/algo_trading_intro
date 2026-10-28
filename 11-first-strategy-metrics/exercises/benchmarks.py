"""Control aleatorio proporcionado: contrato de comparación, no señal predictiva.

Mismo clip 0.05 BTC y regla de probabilidad 0.6 por foto. Cada ejecución
restablece la semilla. No impone un límite de inventario distinto del de la señal.
"""
from random import Random
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType

CONTROL_SEEDS = (7, 21, 99)


class RandomControl(Strategy):
    def __init__(self, seed=7):
        self.seed = seed

    def on_start(self, ctx):
        self.rng = Random(self.seed)

    def on_book_update(self, book):
        if self.rng.random() > 0.6:
            return []
        side = self.rng.choice(['buy', 'sell'])
        return [NewOrder(Order(book.symbol, side, 0.05, order_type=OrderType.MARKET))]
