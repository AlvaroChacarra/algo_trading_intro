"""El reloj del replay. El matching y la cartera tienen responsabilidades propias."""
from book import SnapshotBook
from matching import PlannedEngine


class ReplayMarket:
    def __init__(self, rows, symbol='BTC', depth=10):
        # Ejercicio 1A: guarda rows como lista, symbol, depth y PlannedEngine; deja _i=-1 y book=None.
        self.rows = list(rows)
        self.symbol = symbol
        self.depth = depth
        self.engine = PlannedEngine()
        self._i = -1
        self.book = None

    @property
    def timestamp(self):
        if self.book is None:
            return None
        return int(float(self.rows[self._i].get('timestamp', self._i)))

    def step(self):
        # Ejercicio 1B: avanza _i una vez; devuelve un SnapshotBook nuevo o limpia book y devuelve None al agotarse.
        self._i += 1
        if self._i >= len(self.rows):
            self.book = None
            return None
        self.book = SnapshotBook.from_snapshot(self.symbol, self.rows[self._i], self.depth)
        return self.book

    def submit(self, order):
        # Ejercicio 1C: exige un libro activo y devuelve engine.process(order, book, timestamp), sin avanzar _i.
        if self.book is None:
            raise RuntimeError('llama a step antes de enviar una orden')
        return self.engine.process(order, self.book, self.timestamp)

    def reset(self):
        # Ejercicio 1D: restaura _i=-1 y book=None, conservando las filas y el motor.
        self._i = -1
        self.book = None
