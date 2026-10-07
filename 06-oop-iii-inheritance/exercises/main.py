"""Conecta tu libro y tus reglas. Completa un apartado y ejecútalo de nuevo."""
from book import Level, OrderBook
from indicators import rsi
from signals import Signal, RSISignal, ImbalanceSignal


def main():
    # Proporcionado: datos sintéticos docentes, no cotizaciones reales.
    # Un cierre diario en USD; 15 observaciones para calcular 14 cambios.
    closes = [100, 101, 102, 103, 104, 105, 106, 107, 106, 105, 104, 104, 104, 104, 104]
    book = OrderBook([Level(99, 3)], [Level(101, 1)])
    # TODO · Ejercicio 1A: consulta imbalance del libro con un nivel.
    imb = None
    # Proporcionado: ambas hijas recibirán este mismo diccionario.
    data = {'closes': closes, 'imbalance': imb}
    print('dato compartido | RSI 14:', rsi(closes, 14), '| imbalance:', imb)

    # Proporcionado: captura solo el error esperado al crear la base abstracta.
    try:
        Signal()
        print('base instanciada: falta el decorador')
    except TypeError:
        print('base abstracta: necesita decide concreto')

    # TODO · Ejercicio 3C: crea rsi_rule y muestra su nombre y decisión sobre data.

    # TODO · Ejercicio 4C: crea imbalance_rule con umbral 0.3 y muestra su decisión.

    # TODO · Ejercicio 5A: recorre ambas reglas con el mismo data.

    # Proporcionado: ventanas sintéticas que sitúan el RSI exactamente en 30 y 70.
    closes30 = [100, 101, 102, 103, 102, 101, 100, 99, 98, 97, 96, 96, 96, 96, 96]
    closes70 = closes
    rsi_inputs = [{'closes': values} for values in
                  [closes30, closes70, closes[:14], [100] * 15]]
    missing = OrderBook([], []).imbalance(levels=1)
    imbalance_inputs = [{'imbalance': value} for value in [missing, -0.3, 0.3]]
    # TODO · Ejercicio 6A: prueba fronteras, ausencia y cambios de parámetros.

    # TODO · Ejercicio 6B: cambia cierres y tamaños; conserva las dos reglas.

    # Lectura 7A: traza super en enunciado.md; no cambia este programa.


if __name__ == '__main__':
    main()
