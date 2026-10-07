"""Reglas intercambiables: proponen órdenes y reciben confirmaciones."""
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class Hold(Strategy):
    def on_book_update(self, book):
        # Ejercicio 1A: devuelve [] desde Hold.on_book_update: observar el libro no obliga a enviar una orden.
        return []


class BuyOnce(Strategy):
    def __init__(self, size=1.0):
        self.size = size
        self.done = False
        self.callbacks = 0
        self.executed = 0.0
        self.end_position = None

    def on_start(self, ctx):
        # Ejercicio 1B: reinicia done, callbacks, executed y end_position en BuyOnce.on_start para repetir la misma estrategia.
        self.done = False
        self.callbacks = 0
        self.executed = 0.0
        self.end_position = None

    def on_book_update(self, book):
        # Ejercicio 1C: propón una única NewOrder MARKET de self.size usando book.symbol; después devuelve [].
        if self.done:
            return []
        self.done = True
        return [NewOrder(Order(book.symbol, 'buy', self.size,
                               order_type=OrderType.MARKET))]

    def on_fill(self, fill):
        self.callbacks += 1
        self.executed += fill.size

    def on_end(self, ctx):
        self.end_position = ctx.position


class SellOnce(BuyOnce):
    def on_book_update(self,book):
        # Ejercicio 4C: sobrescribe solo SellOnce.on_book_update para proponer una venta MARKET única del tamaño configurado.
        if self.done:
            return []
        self.done=True
        return [NewOrder(Order(book.symbol,'sell',self.size,order_type=OrderType.MARKET))]
