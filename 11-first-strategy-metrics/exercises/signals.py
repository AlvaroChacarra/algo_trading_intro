"""La regla nueva conserva el contrato Strategy y el mismo runner."""
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class ImbalanceStrategy(Strategy):
    def __init__(self, thr=0.3):
        self.thr = thr
    def on_book_update(self, book):
        # TODO · Ejercicio 3C: implementa ImbalanceStrategy con thr parametrizable, imbalance(3) y clip 0.05 MARKET; None e igualdad devuelven [].
        raise NotImplementedError('Completa 3C en signals.py.')
