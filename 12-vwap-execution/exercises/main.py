"""L12: del encargo al calendario y a la ejecución confirmada."""
from profiles import normalize_profile, slice_sizes
from execution import StudentVWAPStrategy
from runner import ResearchBacktest
from market import ReplayMarket
from book import SnapshotBook
from matching import ExecutionFill
from metrics import weighted_price, execution_cost_bps
from scenarios import raw, total_size, partial_rows, raw_u, schedule_rows, precios, volumenes

STEPS = ('1A', '1B', '2A', '2B', '2C', '2D', '2E', '2F', '3A', '3B', '4A', '4B', '4C', '4D', '4E', '4F', '4G', '5A')


def practice(through=None):
    print('Encargo: 5 BTC · cinco intervalos iguales · perfil conocido antes de operar')
    weights = normalize_profile(raw)
    print('1A · pesos:', weights, 'suma:', sum(weights))
    if through == '1A': return locals()

    sizes = slice_sizes(weights,total_size)
    print('1B · tamaños BTC:', sizes, 'total:', sum(sizes))
    if through == '1B': return locals()


    print('Variación: compra 1 BTC · dos intervalos · fills parciales')
    schedule = StudentVWAPStrategy('buy',1,[1,1])
    print('2A · estado inicial:', schedule.step, schedule.target, schedule.executed)
    if through == '2A': return locals()

    available = schedule.advance_target()
    print('2B · primer objetivo:', available, schedule.target, 'confirmado:', schedule.executed)
    if through == '2B': return locals()

    schedule.on_fill(ExecutionFill(0,'BTC','buy',101,.25))
    print('2C · confirmado BTC:', schedule.executed)
    if through == '2C': return locals()

    schedule.advance_target()
    print('2D · objetivo / confirmado / déficit:', schedule.target, schedule.executed, schedule.pending_size())
    if through == '2D': return locals()

    trace = StudentVWAPStrategy('buy',1,[1,1])
    print('2E · nueva instancia para la traza: step / executed:', trace.step, trace.executed)
    if through == '2E': return locals()

    # TODO · Ejercicio 2F: guarda first_action y second_action de trace.on_book_update(None), confirmando entre ambas un ExecutionFill de 0.25 BTC; predice el segundo tamaño y comprueba que no hay tercer envío.
    raise NotImplementedError('Completa 2F en main.py.')
    print('2F · primer / segundo envío BTC:', first_action.order.size, second_action.order.size)
    print('2F · confirmado / sin tercer envío:', trace.executed, trace.on_book_update(None))
    if through == '2F': return locals()

    # TODO · Ejercicio 3A: guarda strategy como StudentVWAPStrategy buy, total 1, perfil [1,1]; ejecuta ResearchBacktest con partial_rows, profundidad 1, cash 1000 y fee_bps=10; guarda execution.
    raise NotImplementedError('Completa 3A en main.py.')
    print('3A · fills:', [(f.price,f.size) for f in execution.fills])
    print('3A · mercado / intervalos:', execution.n_steps, strategy.step)
    if through == '3A': return locals()

    # TODO · Ejercicio 3B: fija arrival en el mid de la primera partial_rows antes de operar; guarda vwap_price con weighted_price, price_cost con execution_cost_bps y residual como total_size-executed.
    raise NotImplementedError('Completa 3B en main.py.')
    print('cierre ejecución propia:', round(strategy.executed,4), round(residual,4), round(vwap_price,4), round(price_cost,4), round(execution.fees,4))
    if through == '3B': return locals()

    # TODO · Ejercicio 4A: guarda w20 normalizando veinte unos; calcula total20 sumando slice_sizes(w20,1); predice el peso de cada intervalo.
    raise NotImplementedError('Completa 4A en main.py.')
    print('4A · peso / total:', w20[0], round(total20,6))
    if through == '4A': return locals()

    # TODO · Ejercicio 4B: normaliza raw_u=[3,1,1,1,4] en pesos_u y calcula sizes_u para 5 BTC; conserva el total.
    raise NotImplementedError('Completa 4B en main.py.')
    print('4B · pesos / tamaños BTC:', pesos_u, sizes_u)
    if through == '4B': return locals()

    # TODO · Ejercicio 4C: ejecuta tu clase buy de 5 BTC con [1]*5 y raw_u sobre schedule_rows; guarda twap_result y vwap_result; compara fills y precio ponderado.
    raise NotImplementedError('Completa 4C en main.py.')
    print('4C · TWAP / VWAP: cantidad y precio:', [(sum(f.size for f in r.fills),weighted_price(r.fills)) for r in (twap_result,vwap_result)])
    if through == '4C': return locals()

    # TODO · Ejercicio 4D: calcula coste_bps de una venta a 99974.5 frente al arrival 100000 y explica por qué un coste positivo es adverso.
    raise NotImplementedError('Completa 4D en main.py.')
    print('4D · coste venta bps:', round(coste_bps,4))
    if through == '4D': return locals()

    # TODO · Ejercicio 4E: calcula avg_manual para 0.25 BTC a 101 y 0.75 a 103; explica por qué 102, la media simple, no representa esos fills.
    raise NotImplementedError('Completa 4E en main.py.')
    print('4E · precio manual / fills:', avg_manual, vwap_price)
    if through == '4E': return locals()

    # TODO · Ejercicio 4F: calcula vwap_sesion con precios [100,101,102] y volumenes [5,2,1]; contrasta con vwap_price y explica por qué el volumen futuro solo sirve para evaluar después.
    raise NotImplementedError('Completa 4F en main.py.')
    print('4F · VWAP sesión / propios fills:', vwap_sesion, vwap_price)
    if through == '4F': return locals()

    # TODO · Ejercicio 4G: ejecuta tu clase sell de 1 BTC con [1,1] sobre partial_rows; guarda sell_result y ejecutado como suma de tamaños de sus fills; explica el signo de final_position.
    raise NotImplementedError('Completa 4G en main.py.')
    print('4G · venta: BTC / posición / coste bps:', ejecutado, sell_result.final_position, round(execution_cost_bps(sell_result.fills,100,'sell'),4))
    if through == '4G': return locals()

    # TODO · Ejercicio 5A: copia partial_rows en short_rows y cambia solo ask_size_1 de la segunda foto a 0.5; ejecuta sparse_strategy y sparse_result, calcula shortfall y comprueba que otra foto líquida no abre un nuevo intervalo.
    raise NotImplementedError('Completa 5A en main.py.')
    print('5A · confirmado / déficit / intervalos / fotos:', sparse_strategy.executed, shortfall, sparse_strategy.step, sparse_result.n_steps)
    print('5A · sin envío posterior:', sparse_strategy.on_book_update(None))
    if through == '5A': return locals()

    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L12: sigue los apartados del enunciado.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
