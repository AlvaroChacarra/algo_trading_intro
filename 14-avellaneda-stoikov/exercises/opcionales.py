"""OPTIONAL: variantes separadas de la ruta requerida."""
from maker import StudentAvellanedaStoikov

STEPS = ("5A", "5B", "5C", "5D")

def practice(through=None):
    # TODO · Ejercicio 5A: OPTIONAL: crea probe con gamma=0.5, sigma=0.5 y kappa=1.5, fija q=-1 y guarda centers a tau=1 y tau=0.
    raise NotImplementedError('Completa 5A en opcionales.py.')
    # Observación 5A
    print('centros:', centers, '; q:', probe.inventory, '; ancho final:', round(probe.spread(0),6))
    if through == '5A': return locals()

    # TODO · Ejercicio 5B: OPTIONAL: crea double_sigma con sigma=1.0 y q=-1; guarda quadrupled_shift como razón de los ajustes absolutos a tau=1 frente a probe.
    raise NotImplementedError('Completa 5B en opcionales.py.')
    # Observación 5B
    print('factor por duplicar sigma:', quadrupled_shift)
    if through == '5B': return locals()

    # TODO · Ejercicio 5C: OPTIONAL: consulta las quotes de double_sigma para mid=100 y tau=1 y guarda quoted_width=ask-bid; contrasta con spread(1).
    raise NotImplementedError('Completa 5C en opcionales.py.')
    # Observación 5C
    print(f'ancho de quotes {quoted_width:.6f}; método {double_sigma.spread(1):.6f}')
    if through == '5C': return locals()

    # TODO · Ejercicio 5D: OPTIONAL: completa equiv_certeza(media,gamma,var) con media menos gamma por var dividido entre dos; calcula barato y caro para media=100, var=30 y gamma 0.1 y 2.0.
    raise NotImplementedError('Completa 5D en opcionales.py.')
    # Observación 5D
    print('equivalente gamma 0.1:', barato, 'gamma 2:', caro)
    if through == '5D': return locals()

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
