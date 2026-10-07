"""Experimentos de L8. Las clases y reglas viven en sus módulos."""
import argparse
import csv
from pathlib import Path
from book import SnapshotBook
from exchange.orders import Order, OrderType, Side
from matching import (opposite_levels, take_from_level, crosses, plan_fills,
                      commit_plan, rest_limit, validate_plan, PlannedEngine,
                      effective_price, compare_engine)
from scenarios import fresh_book, book_state


CHECKPOINTS = ('1A', '1B', '1C', '2A', '2B', '3A', '3B', '3C', '3D', '3E', '3F', '4A', '4B', '5A', '5B', '5C', '6A', '6B', '6C')


def practice(through=None):
    # Proporcionado: primer resultado, incluso con todos los TODO pendientes.
    book = fresh_book()
    print('Libro inicial · bids:', book_state(book)[0], '| asks:', book_state(book)[1])
    order = Order('BTC', 'buy', 1, order_type=OrderType.MARKET)

    # 1A · Selecciona el lado contrario
    # Comprobación 1A: completa opposite_levels en matching.py.
    levels = opposite_levels(order, book)
    print('1A · niveles contrarios:', [(lv.price,lv.size) for lv in levels])
    print('misma lista del libro:', levels is book.asks)
    if through == '1A': return locals()

    # 1B · Calcula take y remaining
    # Comprobación 1B: completa take_from_level en matching.py.
    take, pending = take_from_level(order.size, levels[0])
    print('1B · take / remaining:', take, pending)
    print('nivel intacto:', levels[0].size)
    if through == '1B': return locals()

    # 1C · Decide si el precio cruza
    # Comprobación 1C: completa crosses en matching.py.
    limited = Order('BTC','buy',1,price=101,order_type=OrderType.LIMIT)
    print('1C · compra limitada:', [crosses(limited, lv.price) for lv in levels])
    if through == '1C': return locals()

    # 2A · Construye un único plan
    # Comprobación 2A: completa plan_fills en matching.py.
    plan, remaining = plan_fills(order, levels)
    print('2A · plan MARKET:', [(lv.price, qty) for lv,qty in plan])
    print('remanente:', remaining)
    print('tamaños tras plan:', [lv.size for lv in levels])
    if through == '2A': return locals()

    # 2B · Aplica el plan y crea fills
    # Comprobación 2B: completa commit_plan en matching.py.
    # Cada observación reconstruye el estado y recalcula el plan con tus funciones.
    book = fresh_book()
    order = Order('BTC', 'buy', 1, order_type=OrderType.MARKET)
    levels = opposite_levels(order, book)
    plan, remaining = plan_fills(order, levels)
    fills = commit_plan(order, book, plan, timestamp=7)
    print('2B · fills MARKET:', [(f.price,f.size) for f in fills])
    print('asks finales:', [(lv.price,lv.size) for lv in book.asks])
    print('timestamp / caja:', fills[0].timestamp, sum(f.cash_flow() for f in fills))
    if through == '2B': return locals()

    # 3A · Recupera una foto limpia
    # TODO · Ejercicio 3A: crea clean con fresh_book y consulta su mid y spread antes de comparar políticas.
    raise NotImplementedError('Completa 3A en main.py.')
    print('3A · foto limpia, mid / spread:', mid0, spread0)
    if through == '3A': return locals()

    # 3B · Recupera la liquidez
    # TODO · Ejercicio 3B: guarda available como la profundidad ask de clean en dos niveles.
    raise NotImplementedError('Completa 3B en main.py.')
    print('3B · liquidez sell:', available)
    if through == '3B': return locals()

    # 3C · Un límite detiene el plan
    # TODO · Ejercicio 3C: planifica BUY 1 a 101 y SELL 1.5 a 99 sobre clean; conserva sus planes y pendientes.
    raise NotImplementedError('Completa 3C en main.py.')
    print('3C · LIMIT compra:', [(lv.price,q) for lv,q in limit_plan], limit_remaining)
    print('LIMIT venta:', [(lv.price,q) for lv,q in sell_plan], sell_remaining)
    if through == '3C': return locals()

    # 3D · Un remanente LIMIT descansa
    # Comprobación 3D: completa rest_limit en matching.py.
    resting = fresh_book()
    pending_plan, pending_size = plan_fills(limit_order, opposite_levels(limit_order,resting))
    limit_fills = commit_plan(limit_order,resting,pending_plan)
    rest_limit(limit_order,resting,pending_size)
    print('3D · LIMIT fills:', [(f.price,f.size) for f in limit_fills])
    print('LIMIT bids:', [(lv.price,lv.size) for lv in resting.bids])
    if through == '3D': return locals()

    # 3E · IOC cancela el resto
    # TODO · Ejercicio 3E: ejecuta el plan IOC BUY 1 a 101 sobre un libro nuevo y cancela el pendiente.
    raise NotImplementedError('Completa 3E en main.py.')
    print('3E · IOC ejecutado / cancelado:', sum(f.size for f in ioc_fills), ioc_remaining)
    print('IOC bids:', [(lv.price,lv.size) for lv in ioc_book.bids])
    if through == '3E': return locals()

    # 3F · Valida FOK antes de mutar
    # Comprobación 3F: completa validate_plan en matching.py.
    fok_book = fresh_book()
    fok_order = Order('BTC','buy',3,price=102,order_type=OrderType.FOK)
    fok_plan,fok_remaining = plan_fills(fok_order,opposite_levels(fok_order,fok_book))
    fok_fills = []
    if validate_plan(fok_order,fok_remaining):
        fok_fills = commit_plan(fok_order,fok_book,fok_plan)
    print('3F · FOK insuficiente, fills:', len(fok_fills))
    print('FOK asks intactos:', [(lv.price,lv.size) for lv in fok_book.asks])
    if through == '3F': return locals()

    # 4A · Integra tus fases en PlannedEngine
    # Comprobación 4A: completa PlannedEngine en matching.py.
    engine = PlannedEngine()
    for kind in (OrderType.MARKET,OrderType.LIMIT,OrderType.IOC,OrderType.FOK):
        policy_book = fresh_book()
        policy_order = Order('BTC','buy',1,price=None if kind is OrderType.MARKET else 101,order_type=kind)
        policy_fills = engine.process(policy_order,policy_book,timestamp=9)
        print(kind.value, 'fills:', [(f.price,round(f.size,6)) for f in policy_fills], 'bids:', [(lv.price,round(lv.size,6)) for lv in policy_book.bids])
    if through == '4A': return locals()

    # 4B · Una orden pequeña cabe
    # TODO · Ejercicio 4B: ejecuta MARKET BUY 0.2 sobre un libro nuevo con tu PlannedEngine y guarda small_fills.
    raise NotImplementedError('Completa 4B en main.py.')
    print('4B · pequeña:', [(f.price,f.size) for f in small_fills])
    if through == '4B': return locals()

    # 5A · Calcula precio efectivo
    # Comprobación 5A: completa effective_price en matching.py.
    sweep_fills = engine.process(Order('BTC','buy',1,order_type=OrderType.MARKET),fresh_book())
    eff = effective_price(sweep_fills)
    print('5A · precio efectivo:', eff)
    if through == '5A': return locals()

    # 5B · Coste respecto al mid
    # TODO · Ejercicio 5B: guarda buy_slippage = eff - mid inicial y explica el coste positivo de esta compra.
    raise NotImplementedError('Completa 5B en main.py.')
    print('5B · coste compra por unidad:', buy_slippage)
    if through == '5B': return locals()

    # 5C · Mide el barrido
    # TODO · Ejercicio 5C: suma los tamaños de sweep_fills en executed y cuenta sus fills en levels_used.
    raise NotImplementedError('Completa 5C en main.py.')
    print('5C · ejecutado / tramos:', executed, levels_used)
    if through == '5C': return locals()

    data_path = Path(__file__).resolve().parent / 'exchange/_data/btc_lob_snapshots.csv'
    with data_path.open(newline='') as stream:
        csv_row = next(csv.DictReader(stream))
    # 6A · Tu motor llega al CSV
    # TODO · Ejercicio 6A: construye csv_book, pide FOK por el doble de su liquidez ask y conserva csv_fills.
    raise NotImplementedError('Completa 6A en main.py.')
    print('6A · CSV FOK fills:',len(csv_fills))
    print('CSV liquidez tras FOK:',round(csv_book.depth('sell',10),6))
    csv_market_book = SnapshotBook.from_snapshot('BTCUSDT',csv_row,10)
    csv_market = Order('BTCUSDT','buy',.1,order_type=OrderType.MARKET)
    csv_market_fills = engine.process(csv_market,csv_market_book)
    print('CSV precio ejecutado:', effective_price(csv_market_fills))
    if through == '6A': return locals()

    # 6B · Contrasta con un oráculo explícito
    # Comprobación 6B: completa compare_engine en matching.py.
    for side,price in [('buy',101),('sell',99)]:
        for kind in (OrderType.MARKET,OrderType.LIMIT,OrderType.IOC,OrderType.FOK):
            matched = compare_engine(PlannedEngine,side,1.5,kind,None if kind is OrderType.MARKET else price)
            print('6B · contraste:',side,kind.value,matched)
    if through == '6B': return locals()

    # Lectura 6C: predice dos compras consecutivas antes de ejecutar este contraste.
    shared = fresh_book()
    first = engine.process(Order('BTC', 'buy', .3, order_type=OrderType.MARKET), shared)
    second = engine.process(Order('BTC', 'buy', .3, order_type=OrderType.MARKET), shared)
    print('6C · Consecutivas:', [(f.price, round(f.size, 9)) for f in first],
          [(f.price, round(f.size, 9)) for f in second], '| asks:', book_state(shared)[1])
    separate = [engine.process(Order('BTC', 'buy', .3, order_type=OrderType.MARKET), fresh_book())
                for _ in range(2)]
    print('6C · Libros nuevos:', [[(f.price, round(f.size, 9)) for f in fills] for fills in separate])

    return locals()


def main(through=None):
    # Proporcionado: detenerse en el hueco actual no exige resolver los posteriores.
    try:
        return practice(through)
    except NotImplementedError as pending:
        print(pending)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Práctica L8 por apartados.')
    parser.add_argument('--through', choices=CHECKPOINTS)
    main(parser.parse_args().through)
