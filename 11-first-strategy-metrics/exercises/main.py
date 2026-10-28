"""L11: observar, medir y comparar el mismo experimento."""
from known_strategies import BuyOnce, Hold
from runner import ResearchBacktest
from market import ReplayMarket
from book import SnapshotBook
from metrics import (running_peaks, drawdowns, max_drawdown, weighted_price,
                     execution_cost_bps, max_inventory, capture_arrival)
from signals import ImbalanceStrategy
from benchmarks import RandomControl, CONTROL_SEEDS
from metrics_support import metric_rows

STEPS = ("1A", "1B", "1C", "1D", "2A", "2B", "2C", "3A", "3B", "3C", "3D", "3E", "4A", "4B")


def rounded(values):
    # Proporcionado: redondeo solo para presentar, nunca para calcular métricas.
    return [round(value, 4) for value in values]


def practice(through=None):
    print('Cinco fotos · mid 100 → 102 → 100 → 103 → 97 · caja 1000 USDT')
    # TODO · Ejercicio 1A: ejecuta BuyOnce(1) con las cinco metric_rows, cash=1000 y sin fees; guarda result para medir el mismo experimento.
    raise NotImplementedError('Completa 1A en main.py.')
    print('1A · equity:', rounded(result.equity_curve))
    print('1A · fills:', [(f.price, f.size) for f in result.fills])
    if through == '1A': return locals()

    peaks = running_peaks(result.equity_curve, 1000)
    print('1B · picos:', rounded(peaks))
    if through == '1B': return locals()
    falls = drawdowns(result.equity_curve)
    print('1C · caídas:', rounded(falls))
    if through == '1C': return locals()
    print('1D · máximo drawdown:', round(max_drawdown(result.equity_curve), 4))
    if through == '1D': return locals()

    average = weighted_price(result.fills)
    print('2A · precio ponderado / sin fills:', round(average, 4), weighted_price([]))
    if through == '2A': return locals()
    # Proporcionado: misma referencia observable ANTES de enviar la primera orden.
    parent_arrival = SnapshotBook.from_snapshot('BTC', metric_rows[0], 2).mid
    print('2B · arrival / coste bps / fees:', parent_arrival,
          round(execution_cost_bps(result.fills, parent_arrival, 'buy'), 4), result.fees)
    if through == '2B': return locals()
    print('2C · posición final / máximo:', result.final_position, max_inventory(result.positions))
    if through == '2C': return locals()

    # TODO · Ejercicio 3A: ejecuta Hold con las mismas filas, caja y fees que BuyOnce; guarda hold_result como control sin operaciones.
    raise NotImplementedError('Completa 3A en main.py.')
    print('3A · Hold: fills / PnL / drawdown:', hold_result.n_fills,
          hold_result.final_equity - 1000, max_drawdown(hold_result.equity_curve))
    if through == '3A': return locals()
    # TODO · Ejercicio 3B: completa capture_arrival y guarda arrival, pnl, pasos y n_fills del experimento original; separa equity de PnL.
    raise NotImplementedError('Completa 3B en main.py.')
    print('3B · arrival / PnL / pasos / fills:', arrival, round(pnl, 4), pasos, n_fills)
    if through == '3B': return locals()
    signal_result = ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), ImbalanceStrategy(.3)).run()
    print('3C · señal: PnL / fills / máximo inventario:', round(signal_result.final_equity - 1000, 4),
          signal_result.n_fills, max_inventory(signal_result.positions))
    if through == '3C': return locals()

    # Proporcionado: controles sobre las mismas fotos, caja, tarifa y tamaño 0.05.
    # La actividad y la exposición pueden diferir; RandomControl limpia su semilla en on_start.
    controls = [ResearchBacktest(ReplayMarket(metric_rows, 'BTC', 2), RandomControl(seed)).run()
                for seed in CONTROL_SEEDS]
    monos = [r.final_equity - 1000 for r in controls]
    mi_equity = signal_result.final_equity - 1000
    # TODO · Ejercicio 3D: compara mi_equity con el rango de monos en fuera; justifica por qué ese rango no valida una señal.
    raise NotImplementedError('Completa 3D en main.py.')
    print('3D · controles: PnL / fills:', [(round(r.final_equity-1000, 4), r.n_fills) for r in controls])
    print('3D · fuera del rango:', fuera)
    if through == '3D': return locals()

    # TODO · Ejercicio 3E: predice y ejecuta los umbrales 0.1 y 0.5 en low/high; calcula ratio_a y ratio_b y explica las unidades de sus denominadores.
    raise NotImplementedError('Completa 3E en main.py.')
    print('3E · umbrales: PnL / fills / máximo:',
          [(round(r.final_equity-1000, 4), r.n_fills, max_inventory(r.positions)) for r in (low, high)])
    print('3E · ratios ilustrativos, USDT/BTC:', ratio_a, ratio_b)
    if through == '3E': return locals()

    # TODO · Ejercicio 4A: compón summary con pnl, drawdown, cost_bps y max_inventory del mismo result, sin redefinir las métricas.
    raise NotImplementedError('Completa 4A en main.py.')
    print('4A · diagnóstico:', {k: round(v, 4) for k, v in summary.items()})
    if through == '4A': return locals()
    # TODO · Ejercicio 4B: ejecuta otra vez BuyOnce con 10 bps en fee_result; conserva arrival y compara precio, comisión y resultado.
    raise NotImplementedError('Completa 4B en main.py.')
    print('4B · coste bps / fees / PnL / drawdown:',
          round(execution_cost_bps(fee_result.fills, arrival, 'buy'), 4), round(fee_result.fees, 4),
          round(fee_result.final_equity-1000, 4), round(max_drawdown(fee_result.equity_curve), 4))
    if through == '4B': return locals()
    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L11: mide el mismo experimento por apartados.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
