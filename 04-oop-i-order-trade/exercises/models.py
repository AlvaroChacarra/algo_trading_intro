"""Una ejecución confirmada: datos y comportamiento en una misma clase."""
from math import isfinite


class Fill:
    def __init__(self, side, price, size):
        # Validación proporcionada; no necesitas modificarla.
        valid_numbers = all(isfinite(x) and x > 0 for x in (price, size))
        if side not in ('buy', 'sell') or not valid_numbers:
            raise ValueError('fill requiere lado válido y valores positivos finitos')
        # TODO · Ejercicio 1.a: guarda cada argumento en self.side, self.price
        # y self.size. Cada instancia necesita conservar sus propios datos.
        pass

    def cash_flow(self):
        # TODO · Ejercicio 3.a: devuelve self.price por self.size, negativo
        # para buy y positivo para sell: comprar paga; vender cobra.
        # Usa los atributos actuales; consultar el flujo no registra otra ejecución.
        pass

    def __repr__(self):
        # TODO · Ejercicio 6.a: sustituye el texto provisional por una cadena
        # construida con los atributos: Fill(buy 2 @ 100) para la compra del ejemplo.
        # Devuelve el texto; será print(buy) quien lo muestre.
        return "Fill(pendiente)"
