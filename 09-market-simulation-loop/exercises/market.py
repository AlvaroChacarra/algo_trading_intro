"""El reloj del replay. El matching y la cartera tienen responsabilidades propias."""
from book import SnapshotBook
from matching import PlannedEngine


class ReplayMarket:
    def __init__(self, rows, symbol='BTC', depth=10):
        # TODO · Ejercicio 1A: guarda rows como lista, symbol, depth y PlannedEngine; deja _i=-1 y book=None.
        raise NotImplementedError('Completa 1A en market.py.')

    @property
    def timestamp(self):
        if self.book is None:
            return None
        return int(float(self.rows[self._i].get('timestamp', self._i)))

    def step(self):
        # TODO · Ejercicio 1B: avanza _i una vez; devuelve un SnapshotBook nuevo o limpia book y devuelve None al agotarse.
        raise NotImplementedError('Completa 1B en market.py.')

    def submit(self, order):
        # TODO · Ejercicio 1C: exige un libro activo y devuelve engine.process(order, book, timestamp), sin avanzar _i.
        raise NotImplementedError('Completa 1C en market.py.')

    def reset(self):
        # TODO · Ejercicio 1D: restaura _i=-1 y book=None, conservando las filas y el motor.
        raise NotImplementedError('Completa 1D en market.py.')
