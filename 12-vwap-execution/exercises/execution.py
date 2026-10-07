"""Una Strategy: programa el objetivo; los fills confirman ejecución."""
from math import isfinite
from profiles import normalize_profile, slice_sizes
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class StudentVWAPStrategy(Strategy):
    def __init__(self, side: str, total_size: float, profile: list[float], symbol: str = 'BTC'):
        if side not in ('buy','sell') or not isfinite(total_size) or total_size <= 0:
            raise ValueError('lado válido y tamaño positivo')
        self.side = side
        self.symbol = symbol
        self.total_size = total_size
        self.weights = normalize_profile(profile)
        self.sizes = slice_sizes(self.weights,total_size)
        self.on_start(None)

    def on_start(self, ctx):
        # TODO · Ejercicio 2A: completa on_start(ctx): reinicia step a 0, target y executed a 0.0; conserva el constructor proporcionado.
        raise NotImplementedError('Completa 2A en execution.py.')

    def advance_target(self):
        # TODO · Ejercicio 2B: completa advance_target(): devuelve False al agotar sizes; si queda intervalo, suma sizes[step] a target, incrementa step y devuelve True.
        raise NotImplementedError('Completa 2B en execution.py.')

    def on_fill(self, fill):
        # TODO · Ejercicio 2C: completa on_fill(fill): suma solo fill.size a executed; enviar una orden no aumenta este contador.
        raise NotImplementedError('Completa 2C en execution.py.')

    def pending_size(self):
        # TODO · Ejercicio 2D: completa pending_size(): devuelve max(0.0, target-executed), sin modificar el estado.
        raise NotImplementedError('Completa 2D en execution.py.')

    def on_book_update(self, book):
        # TODO · Ejercicio 2E: completa on_book_update(book): avanza el objetivo; si queda horizonte y pending_size()>1e-12, devuelve una NewOrder MARKET de ese tamaño; en otro caso devuelve [].
        raise NotImplementedError('Completa 2E en execution.py.')
