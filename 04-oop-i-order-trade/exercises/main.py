"""Clase 4: el mismo ejercicio que el notebook principal.

Guarda una copia como mi_main.py y traslada tu respuesta del notebook.
Desde esta carpeta: python mi_main.py
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
            # 1. Guarda side, price y size en esta instancia.
            pass

        def cash_flow(self):
            # 3. Devuelve el importe con el signo de esta ejecución.
            pass
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

    total_cash = None
    print('caja de la vuelta completa:', total_cash)
    print('cantidad neta:', f.size - g.size)


    # L04-P03 · 5 · Vende solo una unidad

    partial_sell = None
    partial_cash = None
    remaining_units = None
    print('venta parcial: caja / unidades:', partial_cash, remaining_units)


if __name__ == "__main__":
    main()
