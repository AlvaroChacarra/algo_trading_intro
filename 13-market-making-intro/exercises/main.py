"""L13: ofrece precios, confirma fills y observa inventario."""
import math
from maker import fixed_quotes, StudentMarketMaker
from models import Fill
from portfolio import PositionTracker
from research_support import simulate

STEPS = ('1A', '1B', '1C', '1D', '2A', '2B', '2C', '2D', '2E', '3A', '3B', '4A', '4B', '4C')


def cara_utility(wealth, gamma):
    # TODO · Ejercicio 4B: completa cara_utility(wealth, gamma) con -math.exp(-gamma * wealth); compara U(5) y U(10) con gamma=0.1, distinguiendo utilidad de dinero.
    raise NotImplementedError('Completa 4B en main.py.')


def practice(through=None):
    print("Tu puesto: compra a bid, vende a ask; una quote aún no cambia la cuenta.")
    bid, ask = fixed_quotes(100, 0.6)
    # Observación 1A
    print(f'quotes: {bid:.2f} / {ask:.2f}; ancho: {ask-bid:.2f}')
    if through == '1A': return locals()

    # TODO · Ejercicio 1B: crea tracker = PositionTracker() y aplica Fill("buy", bid, 0.1) al bid calculado; contabiliza únicamente esta compra confirmada.
    raise NotImplementedError('Completa 1B en main.py.')
    # Observación 1B
    print(f'compra | caja {tracker.cash:.2f} | q {tracker.position:.1f} | mark 100 | equity {tracker.equity(100):.2f}')
    if through == '1B': return locals()

    # TODO · Ejercicio 1C: guarda marked_equity consultando tracker.equity(99), sin aplicar otro fill ni cambiar caja o posición; predice qué columnas cambian.
    raise NotImplementedError('Completa 1C en main.py.')
    # Observación 1C
    print(f'mark nuevo | caja {tracker.cash:.2f} | q {tracker.position:.1f} | mark 99 | equity {marked_equity:.2f}')
    if through == '1C': return locals()

    # TODO · Ejercicio 1D: aplica Fill("sell", ask, 0.1) a la misma tracker; este ejemplo confirma una venta al ask original, con quotes fijas y sin costes.
    raise NotImplementedError('Completa 1D en main.py.')
    # Observación 1D
    print(f'venta | caja {tracker.cash:.2f} | q {tracker.position:.1f} | mark 100 | equity {tracker.equity(100):.2f}')
    if through == '1D': return locals()

    maker = StudentMarketMaker(half_spread=0.6, skew=2.0, size=0.1)
    maker.inventory = 0.3
    mbid, mask = maker.quotes(100, 1)
    # Observación 2A
    print(f'centro {maker.reservation_price(100, 1):.2f}; quotes {mbid:.2f} / {mask:.2f}')
    if through == '2A': return locals()

    # TODO · Ejercicio 2B: consulta flat_quotes con maker.inventory = 0 y long_quotes con maker.inventory = 0.3; compara el centro y el ancho sin modificar half_spread.
    raise NotImplementedError('Completa 2B en main.py.')
    # Observación 2B
    print(f'q 0: {flat_quotes[0]:.2f} / {flat_quotes[1]:.2f}; q 0.3: {long_quotes[0]:.2f} / {long_quotes[1]:.2f}')
    print(f'ancho antes {flat_quotes[1]-flat_quotes[0]:.2f}; después {long_quotes[1]-long_quotes[0]:.2f}')
    if through == '2B': return locals()

    # TODO · Ejercicio 2C: crea wide_position con half_spread=0.5 y skew=1, fija inventory=2 y guarda variant_quotes para mid=100 y tau=1; anuncia el cambio de parámetros.
    raise NotImplementedError('Completa 2C en main.py.')
    # Observación 2C
    print('variante q=2:', variant_quotes)
    if through == '2C': return locals()

    # TODO · Ejercicio 2D: fija maker.inventory = -0.3 y guarda short_quotes con mid=100 y tau=1; predice hacia dónde se moverán ambas quotes.
    raise NotImplementedError('Completa 2D en main.py.')
    # Observación 2D
    print(f'corto: {short_quotes[0]:.2f} / {short_quotes[1]:.2f}')
    if through == '2D': return locals()

    # TODO · Ejercicio 2E: crea partial_tracker, compra 0.1 al bid y vende solo 0.04 al ask; guarda partial_equity a mark 100 y explica qué riesgo queda abierto.
    raise NotImplementedError('Completa 2E en main.py.')
    # Observación 2E
    print(f'parcial: q {partial_tracker.position:.2f}; equity {partial_equity:.3f}')
    if through == '2E': return locals()

    # TODO · Ejercicio 3A: crea simulation_maker = StudentMarketMaker() y guarda records = simulate(simulation_maker, seed=2026, sigma=0.5, steps=500); el simulador debe consumir tu clase.
    raise NotImplementedError('Completa 3A en main.py.')
    # Observación 3A
    print(f'cierre propio: pnl {records.final_pnl:.4f}; máximo q {records.max_inventory:.3f}; pasos {len(records)}')
    if through == '3A': return locals()

    # TODO · Ejercicio 3B: guarda terminal_q desde el último registro de records y max_q desde records.max_inventory; explica por qué el máximo absoluto no es la posición final.
    raise NotImplementedError('Completa 3B en main.py.')
    # Observación 3B
    print(f'riesgo observado: final {terminal_q:.3f}; máximo {max_q:.3f}')
    if through == '3B': return locals()

    # TODO · Ejercicio 4A: calcula shock_sd para sigma=2 y cuatro pasos de igual duración; suma sus varianzas independientes en total_variance y explica por qué no sumas desviaciones.
    raise NotImplementedError('Completa 4A en main.py.')
    # Observación 4A
    print('shock sd:', shock_sd, '; varianza del horizonte:', total_variance)
    if through == '4A': return locals()

    # Observación 4B
    print(f'U(5): {cara_utility(5, 0.1):.6f}; U(10): {cara_utility(10, 0.1):.6f}')
    if through == '4B': return locals()

    # TODO · Ejercicio 4C: con A=1 y kappa=1.5, calcula lambda_near a distancia 0.2 y lambda_far a distancia 1.0; predice qué ocurre al mantener la tasa y reducir dt a la mitad.
    raise NotImplementedError('Completa 4C en main.py.')
    # Observación 4C
    print(f'intensidad cerca: {lambda_near:.6f}; lejos: {lambda_far:.6f}')
    if through == '4C': return locals()

    return locals()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="L13: sigue los apartados del enunciado.")
    parser.add_argument("--through", choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
