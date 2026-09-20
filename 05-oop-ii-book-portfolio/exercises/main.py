"""Clase 5: el mismo ejercicio que el notebook principal.

Guarda una copia como mi_main.py y traslada tu respuesta del notebook.
Desde esta carpeta: python mi_main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

def main():
    # L05-P01 · 1 · Consulta el mid
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
            # 1. Completa la propiedad mid.
            pass

        def imbalance(self, levels=1):
            bid = sum(level.size for level in self.bids[:levels])
            ask = sum(level.size for level in self.asks[:levels])
            return (bid - ask) / (bid + ask) if bid + ask else None
    book = OrderBook([Level(98, 1), Level(99, 2)], [Level(101, 3)])
    print('mid:', book.mid)
    print('sin asks:', OrderBook([Level(99, 2)], []).mid)


    # L05-P02 · Tu cartera · una sola celda editable
    from math import isfinite

    fill_record = {'side': 'buy', 'price': 100, 'size': 2}
    class Fill:
        def __init__(self, side, price, size):
            valid_numbers = all(isfinite(x) and x > 0 for x in (price, size))
            if side not in ('buy', 'sell') or not valid_numbers:
                raise ValueError('fill requiere lado válido y valores positivos finitos')
            self.side = side
            self.price = price
            self.size = size

        def cash_flow(self):
            sign = -1 if self.side == 'buy' else 1
            return sign * self.price * self.size


    class PositionTracker:
        def __init__(self, cash=0.0):
            self.cash = cash
            self.position = 0.0

        def apply_fill(self, fill):
            # 2. Suma el flujo del fill a caja.
            pass
            # 3. Actualiza la posición.

        def equity(self, mark):
            # 4. Devuelve la valoración.
            pass
    tracker = PositionTracker(cash=1000)
    buy = Fill('buy', 101, 2)
    tracker.apply_fill(buy)
    print('caja:', tracker.cash)
    print('posición:', tracker.position)
    print('operación | caja | posición | mark | equity')
    print('buy 2 a 101 |', tracker.cash, '|', tracker.position, '|', book.mid, '|', tracker.equity(book.mid))


    # L05-P03 · 5 · Cambia solo el mark

    marked_equity = None
    print('mark nuevo |', tracker.cash, '|', tracker.position, '| 105 |', marked_equity)


    # L05-P04 · 6 · Procesa el segundo fill

    # Aplica Fill('sell', 103, 1).
    print('sell 1 a 103 |', tracker.cash, '|', tracker.position, '|', book.mid, '|', tracker.equity(book.mid))


if __name__ == "__main__":
    main()
