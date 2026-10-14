"""Práctica L10: una propuesta, confirmaciones y un runner reutilizable."""
import argparse
from strategy import Hold, BuyOnce, SellOnce
from runner import FeePortfolio, ResearchResult, ResearchBacktest
from market import ReplayMarket
from portfolio import PositionTracker
from book import SnapshotBook
from exchange.backtest import Context
from scenarios import rows


CHECKPOINTS = ('1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B', '3C', '3D', '3E', '4A', '4B', '4C', '4D', '4E')


def practice(through=None):
    print('Dos fotos · mid 100 → 102 · caja 1000 USDT · asks: 101×0.4 + 102×0.6')
    preview_book = SnapshotBook.from_snapshot('BTC', rows[0], 2)
    print('1A · Hold propone:', Hold().on_book_update(preview_book))
    if through == '1A': return locals()

    strategy = BuyOnce(1)
    manual_market = ReplayMarket(rows, symbol='BTC', depth=2)
    tracker = PositionTracker(cash=1000)
    ctx = Context(manual_market, tracker)
    strategy.on_start(ctx)
    print('1B · inicio:', strategy.done, strategy.callbacks, strategy.executed)
    if through == '1B': return locals()

    first_actions = strategy.on_book_update(preview_book)
    print('1C · primera / segunda:', len(first_actions), strategy.on_book_update(preview_book))
    print('confirmado todavía:', strategy.executed)
    if through == '1C': return locals()

    # TODO · Ejercicio 2A: guarda la primera petición en action e inspecciona la orden sin enviarla ni cambiar la cartera.
    raise NotImplementedError('Completa 2A en main.py.')
    print('2A · petición:', action.order.side.value, action.order.size)
    print('antes del envío, caja / posición:', tracker.cash, tracker.position)
    if through == '2A': return locals()

    # TODO · Ejercicio 2B: avanza manual_market, captura su mid antes de ejecutar y envía action.order; guarda active_book, mark y confirmed.
    raise NotImplementedError('Completa 2B en main.py.')
    print('2B · fills:', [(f.price, f.size) for f in confirmed])
    print('mark anterior / mid después:', mark, active_book.mid)
    print('caja aún sin registrar:', tracker.cash)
    if through == '2B': return locals()

    # TODO · Ejercicio 2C: aplica cada fill confirmado a tracker, llama strategy.on_fill por cada uno y guarda first_equity al mark previo.
    raise NotImplementedError('Completa 2C en main.py.')
    print('2C · caja / posición / equity:', tracker.cash, tracker.position, first_equity)
    print('callbacks / ejecutado:', strategy.callbacks, strategy.executed)
    second_book = manual_market.step()
    print('segunda decisión:', strategy.on_book_update(second_book))
    print('segunda equity:', tracker.equity(second_book.mid))
    strategy.on_end(ctx)
    print('cierre manual:', strategy.end_position)
    if through == '2C': return locals()

    fee_probe = FeePortfolio(1000)
    fee_probe.charge(101.6 * 10 / 10000)
    print('3A · comisión / caja:', 101.6 * 10 / 10000, fee_probe.cash)
    if through == '3A': return locals()

    result_probe = ResearchResult()
    print('3B · contenedor vacío:', result_probe.n_steps, result_probe.n_fills)
    if through == '3B': return locals()

    # Proporcionado: sonda de inicio, sin fills ni dependencia del apartado 3D.
    class StartProbe(Hold):
        started = False
        def on_start(self, ctx):
            self.started = True
    start_probe = StartProbe()
    hold_probe = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), start_probe).run()
    print('3C · inicio notificado:', start_probe.started)
    print('control runner:', hold_probe.equity_curve, hold_probe.n_fills)
    if through == '3C': return locals()

    fill_probe = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), BuyOnce(1)).run()
    print('3D · registro runner:', fill_probe.equity_curve, fill_probe.n_fills)
    if through == '3D': return locals()

    runner = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), BuyOnce(1))
    result = runner.run()
    print('3E · runner equity:', result.equity_curve)
    print('runner caja / posición:', result.final_cash, result.final_position)
    print('runner pasos / fills:', result.n_steps, result.n_fills)
    print('cierre callback:', runner.strategy.end_position)
    if through == '3E': return locals()

    # TODO · Ejercicio 4A: ejecuta otra vez el mismo runner y guarda repeated, sin crear otra estrategia.
    raise NotImplementedError('Completa 4A en main.py.')
    print('4A · repetición equity:', repeated.equity_curve)
    print('repetición posición / callbacks:', repeated.final_position, runner.strategy.callbacks)
    if through == '4A': return locals()

    # TODO · Ejercicio 4B: compara callbacks con n_fills y executed con la suma de tamaños de repeated; guarda ambas comprobaciones.
    raise NotImplementedError('Completa 4B en main.py.')
    print('4B · callbacks / cantidad reconciliados:', callbacks_match, quantity_match)
    if through == '4B': return locals()

    sold = ResearchBacktest(ReplayMarket(rows, 'BTC', 2), SellOnce(.5)).run()
    print('4C · venta, caja / posición / equity:', sold.final_cash, sold.final_position, sold.final_equity)
    if through == '4C': return locals()

    # TODO · Ejercicio 4D: ejecuta Hold y BuyOnce(1) con 10 bps sobre las mismas filas; guarda hold_result y cost_result.
    raise NotImplementedError('Completa 4D en main.py.')
    print('4D · Hold con fee:', hold_result.equity_curve, hold_result.fees)
    print('BuyOnce con fee:', [round(v, 4) for v in cost_result.equity_curve], round(cost_result.fees, 4))
    print('diferencia final:', round(result.final_equity - cost_result.final_equity, 4))
    if through == '4D': return locals()

    # TODO · Ejercicio 4E: predice BuyOnce(3), ejecuta liquidity_runner y repite la misma instancia; guarda liquidity_result y liquidity_repeat.
    raise NotImplementedError('Completa 4E en main.py.')
    print('4E · solicitado / done / ejecutado / posición:', liquidity_runner.strategy.size, liquidity_runner.strategy.done, liquidity_runner.strategy.executed, liquidity_result.final_position)
    print('fills primera / repetida:', [(f.price, f.size) for f in liquidity_result.fills], [(f.price, f.size) for f in liquidity_repeat.fills])
    print('repetición posición / callbacks:', liquidity_repeat.final_position, liquidity_runner.strategy.callbacks)
    if through == '4E': return locals()

    return locals()


def main(through=None):
    try:
        return practice(through)
    except NotImplementedError as pending:
        print(pending)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Práctica L10 por apartados.')
    parser.add_argument('--through', choices=CHECKPOINTS)
    main(parser.parse_args().through)
