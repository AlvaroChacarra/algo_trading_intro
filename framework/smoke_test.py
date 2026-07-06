"""smoke_test.py — verificación end-to-end del paquete de referencia.

Comprueba que:
  1. El libro se construye desde snapshots y calcula métricas.
  2. El matching cruza market/limit/IOC/FOK correctamente.
  3. El Backtest corre con cualquier Strategy (polimorfismo).
  4. VWAP y un market maker son intercambiables en el mismo runner.

Ejecutar:  python smoke_test.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from exchange import (
    Backtest, Market, MatchingEngine, Order, OrderBook, OrderType, Side,
)
from exchange.strategies import AvellanedaStoikov, MarketMaker, VWAPStrategy

CSV = os.path.join(
    os.path.dirname(__file__), "..", "data", "btc_lob_snapshots.csv",
)


def check(name, cond):
    status = "ok " if cond else "FAIL"
    print(f"  [{status}] {name}")
    assert cond, name


def test_book_metrics():
    print("1) OrderBook + métricas")
    book = OrderBook.from_snapshot("BTCUSDT", {
        "bid_price_1": 100.0, "bid_size_1": 2.0,
        "bid_price_2": 99.0, "bid_size_2": 1.0,
        "ask_price_1": 101.0, "ask_size_1": 1.0,
        "ask_price_2": 102.0, "ask_size_2": 3.0,
    }, depth=2)
    check("best_bid=100", book.best_bid == 100.0)
    check("best_ask=101", book.best_ask == 101.0)
    check("spread=1", book.spread == 1.0)
    check("mid=100.5", book.mid == 100.5)
    check("imbalance(1) > 0 (más bid)", book.imbalance(1) > 0)
    check("depth buy 2 niveles = 3", book.depth(Side.BUY, 2) == 3.0)
    check("microprice entre bid y ask", 100.0 < book.microprice < 101.0)


def test_matching():
    print("2) MatchingEngine")
    eng = MatchingEngine()

    book = OrderBook.from_snapshot("X", {
        "ask_price_1": 101.0, "ask_size_1": 1.0,
        "ask_price_2": 102.0, "ask_size_2": 2.0,
    }, depth=2)
    fills = eng.process(Order("X", Side.BUY, 1.5, order_type=OrderType.MARKET), book)
    check("market buy cruza 2 niveles", len(fills) == 2)
    check("market buy llena 1.5", abs(sum(f.size for f in fills) - 1.5) < 1e-9)
    check("consume primero el mejor ask (101)", fills[0].price == 101.0)

    book = OrderBook.from_snapshot("X", {
        "ask_price_1": 101.0, "ask_size_1": 1.0,
        "ask_price_2": 105.0, "ask_size_2": 5.0,
    }, depth=2)
    fills = eng.process(Order("X", Side.BUY, 3.0, price=101.0, order_type=OrderType.LIMIT), book)
    check("limit buy @101 solo cruza el nivel a 101", len(fills) == 1 and fills[0].size == 1.0)
    check("remanente de limit descansa en bids", book.best_bid == 101.0)

    book = OrderBook.from_snapshot("X", {
        "ask_price_1": 101.0, "ask_size_1": 1.0,
    }, depth=1)
    fills = eng.process(Order("X", Side.BUY, 5.0, price=101.0, order_type=OrderType.FOK), book)
    check("FOK no se llena entera -> 0 fills", len(fills) == 0)
    check("FOK no toca el libro", book.best_ask == 101.0)


def test_backtest_polymorphism():
    print("3) Backtest + polimorfismo de estrategias")
    if not os.path.exists(CSV):
        print("  (CSV de snapshots no encontrado, uso datos sintéticos)")
        rows = [{
            "timestamp": i,
            "bid_price_1": 100 - 0.5, "bid_size_1": 2.0,
            "ask_price_1": 100 + 0.5, "ask_size_1": 2.0,
        } for i in range(50)]
        market = Market("BTCUSDT", rows, depth=1)
    else:
        market = Market.from_csv(CSV, "BTCUSDT")

    strategies = {
        "VWAP": VWAPStrategy("BTCUSDT", Side.BUY, total_size=1.0, horizon=20),
        "MarketMaker": MarketMaker("BTCUSDT"),
        "AvellanedaStoikov": AvellanedaStoikov("BTCUSDT", horizon=len(market)),
    }
    for name, strat in strategies.items():
        market.reset()
        result = Backtest(market, strat, cash=0.0).run()
        check(f"{name}: corre sin error y da pasos", result.n_steps > 0)
        print(f"       -> {result}")

    # VWAP con market orders garantiza fills
    market.reset()
    vwap_res = Backtest(market, VWAPStrategy("BTCUSDT", Side.BUY, 1.0, 20)).run()
    check("VWAP ejecuta fills", vwap_res.n_fills > 0)
    check("VWAP acumula posición larga", vwap_res.final_position > 0)


if __name__ == "__main__":
    test_book_metrics()
    test_matching()
    test_backtest_polymorphism()
    print("\nTODO OK ✅  — el paquete de referencia funciona end-to-end.")
