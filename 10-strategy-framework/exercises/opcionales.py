"""OPTIONAL: variantes independientes de la ruta requerida."""
import argparse
from strategy import BuyOnce
from runner import ResearchBacktest
from market import ReplayMarket
from scenarios import rows
from exchange.strategy import Strategy, NewOrder
from exchange.orders import Order, OrderType


class ImbalanceBuyer(Strategy):
    def on_book_update(self,book):
        # TODO · Ejercicio 5C: OPTIONAL: compra 0.1 MARKET si imbalance(1)>0.3; en None, igualdad o valores inferiores devuelve [].
        raise NotImplementedError('Completa 5C en opcionales.py.')



def practice(through=None):
    print('OPTIONAL · las mismas dos fotos; no es requisito para continuar')
    # TODO · Ejercicio 5A: OPTIONAL: copia rows en partial_rows, elimina el segundo ask de la primera foto y ejecuta BuyOnce(1).
    raise NotImplementedError('Completa 5A en opcionales.py.')
    print('5A · parcial, fills / posición:', partial_result.n_fills, partial_result.final_position)
    print('parcial equity:', partial_result.equity_curve)
    if through == '5A': return locals()

    # TODO · Ejercicio 5B: OPTIONAL: ejecuta dos veces el mismo replay_runner y compara sus curvas y posiciones en same_result.
    raise NotImplementedError('Completa 5B en opcionales.py.')
    print('5B · repetición limpia:', same_result)
    if through == '5B': return locals()

    signal_result = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), ImbalanceBuyer()).run()
    print('5C · señal, fills / posición:', signal_result.n_fills, signal_result.final_position)
    return locals()


def main(through=None):
    try:
        return practice(through)
    except NotImplementedError as pending:
        print(pending)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Variantes OPTIONAL de L10.')
    parser.add_argument('--through', choices=('5A', '5B', '5C'))
    main(parser.parse_args().through)
