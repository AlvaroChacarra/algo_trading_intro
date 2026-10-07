"""OPTIONAL: variantes separadas de la práctica requerida."""
import math
from maker import StudentMarketMaker

STEPS = ("5A", "5B", "5C")

def practice(through=None):
    # TODO · Ejercicio 5A: OPTIONAL: crea negative = StudentMarketMaker(), fija inventory=-0.5 y guarda negative_quotes para mid=100 y tau=1.
    raise NotImplementedError('Completa 5A en opcionales.py.')
    # Observación 5A
    print('inventario -0.5:', negative_quotes)
    if through == '5A': return locals()

    # TODO · Ejercicio 5B: OPTIONAL: fija negative.inventory=0.5 y guarda positive_quotes; calcula same_width comparando ambos anchos con tolerancia 1e-9.
    raise NotImplementedError('Completa 5B en opcionales.py.')
    # Observación 5B
    print('inventario +0.5:', positive_quotes, '; mismo ancho:', same_width)
    if through == '5B': return locals()

    # TODO · Ejercicio 5C: OPTIONAL: calcula rate con A=50, kappa=1.5 y distancia 0.2; conviértela en probability por paso mediante 1 - exp(-rate / 500).
    raise NotImplementedError('Completa 5C en opcionales.py.')
    # Observación 5C
    print(f'tasa {rate:.3f}; probabilidad {probability:.5f}')
    if through == '5C': return locals()

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
