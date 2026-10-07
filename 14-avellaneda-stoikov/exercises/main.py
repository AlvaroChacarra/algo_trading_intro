"""L14: construye centro/ancho, luego contrasta tus quotes."""
import math
from maker import StudentAvellanedaStoikov
from base_maker import StudentMarketMaker
from research_support import simulate

STEPS = ('1A', '1B', '1C', '2A', '2B', '2C', '2D', '2E', '2F', '2G', '3A', '3B', '3C', '3D', '4A', '4B', '4C', '4D')

def practice(through=None):
    maker = StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5)
    maker.inventory = 1
    # Observación 1A
    print(f'ajuste: {maker.inventory_adjustment(1):.6f}')
    if through == '1A': return locals()

    # Observación 1B
    print(f'centro: {maker.reservation_price(100, 1):.6f}')
    if through == '1B': return locals()

    # Observación 1C
    print(f'ancho total: {maker.spread(1):.6f}')
    bid, ask = maker.quotes(100, 1)
    print(f'quotes: {bid:.6f} / {ask:.6f}; centro {(bid+ask)/2:.6f}')
    if through == '1C': return locals()

    # TODO · Ejercicio 2A: fija maker.inventory=-1 y guarda short_quotes; después fija inventory=0 y guarda flat_quotes, siempre con mid=100 y tau=1; predice centro y ancho antes de ejecutar.
    raise NotImplementedError('Completa 2A en main.py.')
    # Observación 2A
    print(f'q=-1: centro {sum(short_quotes)/2:.6f}; ancho {short_quotes[1]-short_quotes[0]:.6f}')
    print(f'q=0: centro {sum(flat_quotes)/2:.6f}; ancho {flat_quotes[1]-flat_quotes[0]:.6f}')
    if through == '2A': return locals()

    # TODO · Ejercicio 2B: fija maker.inventory=1 y guarda time_quotes como pares (tau, quotes) para tau 1, 0.5 y 0; explica qué cambia y qué sigue abierto al final.
    raise NotImplementedError('Completa 2B en main.py.')
    # Observación 2B
    for tau, (b, a) in time_quotes:
        print(f'tau={tau}: centro {(b+a)/2:.6f}; ancho {a-b:.6f}; q {maker.inventory}')
    if through == '2B': return locals()

    # TODO · Ejercicio 2C: crea sign_maker con gamma=0.5, sigma=0.5 y kappa=1.5; guarda centers para inventarios -2, 0 y 2, con mid=100 y tau=1, sin simular.
    raise NotImplementedError('Completa 2C en main.py.')
    # Observación 2C
    print('centros por signo:', centers)
    if through == '2C': return locals()

    # TODO · Ejercicio 2D: crea un maker por cada sigma de (0.5, 1.0), fija q=1 y guarda sus inventory_adjustment(1) en sigma_adjustments; predice el factor antes de consultar.
    raise NotImplementedError('Completa 2D en main.py.')
    # Observación 2D
    print('ajustes sigma 0.5/1.0:', sigma_adjustments, '; factor:', sigma_adjustments[1]/sigma_adjustments[0])
    if through == '2D': return locals()

    # TODO · Ejercicio 2E: guarda liquidity_width consultando maker.spread(0) y risk_width como spread(1) menos liquidity_width; separa los dos términos del ancho sin duplicar la fórmula.
    raise NotImplementedError('Completa 2E en main.py.')
    # Observación 2E
    print(f'ancho riesgo {risk_width:.6f}; liquidez {liquidity_width:.6f}')
    if through == '2E': return locals()

    # TODO · Ejercicio 2F: consulta las quotes de maker para mid=100 y tau=1 y guarda observed_width como ask menos bid; contrasta el ancho observado con spread(1).
    raise NotImplementedError('Completa 2F en main.py.')
    # Observación 2F
    print(f'ancho en quotes: {observed_width:.6f}; método: {maker.spread(1):.6f}')
    if through == '2F': return locals()

    # TODO · Ejercicio 2G: crea variant con gamma=0.5, sigma=2 y kappa=0.5, fija q=2 y guarda variant_quotes con mid=100 y tau=0.5; anuncia que este es otro caso.
    raise NotImplementedError('Completa 2G en main.py.')
    # Observación 2G
    print(f'variante: centro {sum(variant_quotes)/2:.6f}; ancho {variant_quotes[1]-variant_quotes[0]:.6f}')
    if through == '2G': return locals()

    # TODO · Ejercicio 3A: crea simulation_maker con gamma=0.5, sigma=0.5 y kappa=1.5; guarda records = simulate(simulation_maker, seed=2026, steps=500, sigma=simulation_maker.sigma, kappa=simulation_maker.kappa).
    raise NotImplementedError('Completa 3A en main.py.')
    # Observación 3A
    print(f'cierre propio: pnl {records.final_pnl:.4f}; máximo q {records.max_inventory:.3f}; pasos {len(records)}')
    if through == '3A': return locals()

    # TODO · Ejercicio 3B: guarda control_records simulando StudentMarketMaker() con seed=2026, steps=500, sigma=0.5 y kappa=1.5; conserva el control con skew=2 y half_spread=0.6.
    raise NotImplementedError('Completa 3B en main.py.')
    # Observación 3B
    print(f'control L13: pnl {control_records.final_pnl:.4f}; máximo q {control_records.max_inventory:.3f}')
    if through == '3B': return locals()

    # TODO · Ejercicio 3C: completa compare_rules(seeds): por cada semilla crea control y StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5), simula cada uno con los mismos parámetros y devuelve filas (seed, nombre, PnL, máximo inventario).
    raise NotImplementedError('Completa 3C en main.py.')
    # Observación 3C
    comparison = compare_rules((2026, 7, 314))
    for seed, name, pnl, maximum in comparison:
        print(f'comparación {seed} {name}: pnl {pnl:.4f}; máximo {maximum:.3f}')
    if through == '3C': return locals()

    # TODO · Ejercicio 3D: extrae as_pnls de todas las filas StudentAvellanedaStoikov de comparison y guarda pnl_range=(mínimo, máximo); interpreta dispersión sin seleccionar solo la mejor semilla.
    raise NotImplementedError('Completa 3D en main.py.')
    # Observación 3D
    print(f'rango A-S: {pnl_range[0]:.4f} / {pnl_range[1]:.4f}; semillas {len(as_pnls)}')
    if through == '3D': return locals()

    # TODO · Ejercicio 4A: guarda gamma_shifts con los ajustes de makers gamma=0.1 y 1.0, sigma=0.5, kappa=1.5 y q=1 a tau=1; separa este cálculo fijo de una simulación.
    raise NotImplementedError('Completa 4A en main.py.')
    # Observación 4A
    print('ajustes gamma:', gamma_shifts)
    if through == '4A': return locals()

    # TODO · Ejercicio 4B: guarda gamma_rows con (gamma, PnL, máximo inventario) para gamma=0.1 y 1.0, seed=3 y steps=50; usa sigma=0.5 y kappa=1.5 en regla y mercado y describe ambas filas sin imponer monotonía.
    raise NotImplementedError('Completa 4B en main.py.')
    # Observación 4B
    for gamma, pnl, maximum in gamma_rows:
        print(f'gamma {gamma}: pnl {pnl:.4f}; máximo {maximum:.3f}')
    if through == '4B': return locals()

    # TODO · Ejercicio 4C: crea control=StudentMarketMaker(), fija q=0.3 y guarda control_center y control_width consultando reservation_price(100,1) y spread(1).
    raise NotImplementedError('Completa 4C en main.py.')
    # Observación 4C
    print(f'control: centro {control_center:.2f}; ancho {control_width:.2f}')
    if through == '4C': return locals()

    # TODO · Ejercicio 4D: calcula ideal_round_trip como el ancho ask-bid de 1C por tamaño 0.1; explica qué fills confirmados exigiría cobrarlo y qué inventario puede quedar abierto.
    raise NotImplementedError('Completa 4D en main.py.')
    # Observación 4D
    print(f'vuelta ideal: {ideal_round_trip:.6f}')
    if through == '4D': return locals()

    return locals()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
