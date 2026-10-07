"""Una ejecución confirmada: datos y comportamiento en una misma clase."""
from math import isfinite


class Fill:
    def __init__(self, side, price, size):
        # Validación proporcionada; no necesitas modificarla.
        valid_numbers = all(isfinite(x) and x > 0 for x in (price, size))
        if side not in ('buy', 'sell') or not valid_numbers:
            raise ValueError('fill requiere lado válido y valores positivos finitos')
        self.side = side
        self.price = price
        self.size = size

    def cash_flow(self):
        sign = -1 if self.side == 'buy' else 1
        return sign * self.price * self.size

    def __repr__(self):
        return f'Fill({self.side} {self.size} @ {self.price})'
