"""Clase 4: el mismo ejercicio que el notebook principal.

Solución de referencia. Desde esta carpeta: python main.py
Compara los resultados; ejecutar sin errores no prueba que sean correctos.
"""

def main():
    # L04-P01 · Tu Fill · una sola celda editable
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
    f = Fill(fill_record['side'], fill_record['price'], fill_record['size'])
    print('compra:', f.side, f.price, f.size)
    g = Fill('sell', 110, 2)
    print('venta:', g.side, g.price, g.size)
    print('compra intacta:', f.side, f.price, f.size)
    print('objetos distintos:', f is not g)
    print('flujo compra:', f.cash_flow())
    print('flujo venta:', g.cash_flow())
    print('otra consulta:', f.cash_flow())


    # L04-P02 · 4 · Reúne compra y venta

    total_cash = f.cash_flow() + g.cash_flow()
    print('caja de la vuelta completa:', total_cash)
    print('cantidad neta:', f.size - g.size)


    # L04-P03 · 5 · Vende solo una unidad

    partial_sell = Fill('sell', 110, 1)
    partial_cash = f.cash_flow() + partial_sell.cash_flow()
    remaining_units = f.size - partial_sell.size
    print('venta parcial: caja / unidades:', partial_cash, remaining_units)


if __name__ == "__main__":
    main()
