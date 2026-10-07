"""OPTIONAL: variantes y previsiones; no alteran la estrategia requerida."""
from math import isfinite
from profiles import normalize_profile, slice_sizes
from execution import StudentVWAPStrategy
from matching import ExecutionFill

STEPS = ('6A','6B','6C','6D','6E','6F','6G','6H')


def rolling_mean(xs,k):
    # TODO · Ejercicio 6C: OPTIONAL: completa rolling_mean(xs,k): exige k entero entre 1 y len(xs), lanza ValueError fuera del dominio y devuelve la media de los últimos k valores.
    raise NotImplementedError('Completa 6C en opcionales.py.')


def correction(target_so_far,executed,remaining_slices):
    # TODO · Ejercicio 6F: OPTIONAL: completa correction(target_so_far,executed,remaining_slices): exige valores finitos y 0<=executed<=target_so_far e intervalos enteros positivos; devuelve el déficit dividido por intervalos, o lanza ValueError.
    raise NotImplementedError('Completa 6F en opcionales.py.')


def slope(xs,ys):
    # TODO · Ejercicio 6G: OPTIONAL: completa slope(xs,ys) con productos centrados divididos por variación de x; exige pares finitos del mismo tamaño, al menos dos y x variable; calcula b, intercept y prediction para xs=[1,2,3], ys=[3,5,7], x nuevo 4.
    raise NotImplementedError('Completa 6G en opcionales.py.')


def practice(through=None):
    print("OPTIONAL · pasado disponible; ninguna previsión se conecta al runner")
    # TODO · Ejercicio 6A: OPTIONAL: guarda a y b como pesos de dos estrategias buy de 1 BTC con perfiles [2]*5 y [1]*5; predice si cambian las proporciones.
    raise NotImplementedError('Completa 6A en opcionales.py.')
    print('6A · misma escala relativa:',a==b,a)
    if through == '6A': return locals()

    # TODO · Ejercicio 6B: OPTIONAL: crea variant buy de 1 BTC con [1,1], pide first, confirma un fill de 0.4 BTC y guarda next_size de la siguiente acción.
    raise NotImplementedError('Completa 6B en opcionales.py.')
    print('6B · fill / siguiente orden:',variant.executed,next_size)
    if through == '6B': return locals()

    print('6C · últimos dos:', rolling_mean([1, 2, 3, 4], 2))
    print('6C · toda la serie:', rolling_mean([1, 2, 3, 4], 4))
    if through == '6C': return locals()

    volumes = [100,120,90,110,130]
    # TODO · Ejercicio 6D: OPTIONAL: guarda pred como media de los últimos tres volumes=[100,120,90,110,130], sin consultar un volumen futuro.
    raise NotImplementedError('Completa 6D en opcionales.py.')
    print('6D · próximo volumen estimado:', pred)
    if through == '6D': return locals()

    preds = [120,80,200]
    # TODO · Ejercicio 6E: OPTIONAL: guarda profile normalizando preds=[120,80,200] con tu función normalize_profile.
    raise NotImplementedError('Completa 6E en opcionales.py.')
    print('6E · perfil:', profile, 'suma:', sum(profile))
    if through == '6E': return locals()

    print('6F · extra por intervalo:', round(correction(0.5, 0.3, 2), 6))
    print('6F · sin déficit:', correction(0.5, 0.5, 2))
    if through == '6F': return locals()

    xs=[1,2,3]
    ys=[3,5,7]
    b=slope(xs,ys)
    intercept=sum(ys)/len(ys)-b*sum(xs)/len(xs)
    prediction=intercept+b*4
    print('6G · pendiente:', b, 'intercepto:', intercept, 'predicción x=4:', prediction)
    if through == '6G': return locals()

    demanda = [5,10,20,25,20,10,6,4]
    # TODO · Ejercicio 6H: OPTIONAL: guarda plan de 100 barras normalizando demanda=[5,10,20,25,20,10,6,4] y usando slice_sizes; explica qué representa cada tamaño.
    raise NotImplementedError('Completa 6H en opcionales.py.')
    print('6H · plan de barras:', plan)
    print('6H · total:', sum(plan))
    if through == '6H': return locals()

    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='L12: variantes OPTIONAL.')
    parser.add_argument('--through', choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
