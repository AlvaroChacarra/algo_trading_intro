"""Variantes OPTIONAL: misma conclusión final, recorridos distintos."""
from metrics import max_drawdown, max_inventory
from known_strategies import BuyOnce
from runner import ResearchBacktest
from market import ReplayMarket
from metrics_support import metric_rows, show_curve

STEPS = ('5A', '5B', '5C', '5D')


def practice(through=None):
    # TODO · Ejercicio 5A: OPTIONAL: calcula dd_a y dd_b con initial_equity=0 para dos curvas que terminan en el mismo PnL.
    raise NotImplementedError('Completa 5A en opcionales.py.')
    print('5A · mismo PnL, drawdowns:', dd_a, dd_b)
    if through == '5A': return locals()
    # TODO · Ejercicio 5B: OPTIONAL: calcula exposure_a y exposure_b para dos recorridos que terminan planos, sin confundir final con máximo.
    raise NotImplementedError('Completa 5B en opcionales.py.')
    print('5B · posición final cero, máximos:', exposure_a, exposure_b)
    if through == '5B': return locals()
    result = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), BuyOnce(1), cash=1000).run()
    # TODO · Ejercicio 5C: OPTIONAL: guarda curve del nuevo result y localiza el pico y valle de su peor caída; usa el dibujo proporcionado.
    raise NotImplementedError('Completa 5C en opcionales.py.')
    print('5C · curva / peor caída:', curve, max_drawdown(curve))
    show_curve(curve, 1000)
    if through == '5C': return locals()
    kcal_a, precio_a = 1800, 6.0
    kcal_b, precio_b = 1500, 4.0
    # TODO · Ejercicio 5D: OPTIONAL: calcula kcal por euro de las dos cestas y guarda mejor; explica qué mide y qué omite ese ratio.
    raise NotImplementedError('Completa 5D en opcionales.py.')
    print('5D · kcal/€:', ratio_a, ratio_b, 'mayor:', mejor)
    if through == '5D': return locals()
    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L11: variantes OPTIONAL independientes.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
