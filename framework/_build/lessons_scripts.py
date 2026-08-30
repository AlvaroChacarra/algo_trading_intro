"""lessons_scripts.py — los .py consolidados de L7-L14 (ingrediente 6 del formato).

Cada script es el núcleo de su clase condensado en un archivo ejecutable desde
la propia carpeta exercises/ (el paquete `exchange/` viaja al lado):

    python <script>.py
"""

EXTRA_SCRIPTS = {
    7: ("read_book.py", '''# Clase 7 - Snapshot sintético a OrderBook, en un archivo .py
# Ejecuta desde exercises/:  python read_book.py

import csv
import os

from exchange.book import OrderBook


def describe(book):
    print(f"  mid={book.mid:.2f}  spread={book.spread:.2f}  "
          f"imb1={book.imbalance(1):+.3f}  imb5={book.imbalance(5):+.3f}  "
          f"micro={book.microprice:.2f}")


def main():
    path = os.path.join(os.path.dirname(__file__), "exchange", "_data",
                        "btc_lob_snapshots.csv")
    with open(path, newline="") as f:
        row = {k: float(v) for k, v in next(csv.DictReader(f)).items()}
    book = OrderBook.from_snapshot("BTCUSDT", row, depth=10)
    print("raw snapshot -> OrderBook:")
    describe(book)
    print(f"  depth bid(5)={book.depth('buy', 5):.3f}  "
          f"depth ask(5)={book.depth('sell', 5):.3f}")


if __name__ == "__main__":
    main()
'''),

    8: ("matching_demo.py", '''# Clase 8 - Barridos y tipos de orden, en un archivo .py
# Ejecuta desde exercises/:  python matching_demo.py

import csv
import os

from exchange.book import Level, OrderBook
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType


def fresh_book():
    path = os.path.join(os.path.dirname(__file__), "exchange", "_data",
                        "btc_lob_snapshots.csv")
    with open(path, newline="") as f:
        row = {k: float(v) for k, v in next(csv.DictReader(f)).items()}
    raw = OrderBook.from_snapshot("BTCUSDT", row, depth=10)
    binary_sizes = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0)
    return OrderBook(
        raw.symbol,
        [Level(level.price, binary_sizes[i])
         for i, level in enumerate(raw.bids)],
        [Level(level.price, binary_sizes[i])
         for i, level in enumerate(raw.asks)],
    )


def sweep(size):
    """Una market buy contra el primer snapshot: fills, efectivo y slippage."""
    book = fresh_book()
    mid = book.mid
    fills = MatchingEngine().process(
        Order("BTCUSDT", "buy", size, order_type=OrderType.MARKET), book)
    filled = sum(f.size for f in fills)
    eff = sum(f.price * f.size for f in fills) / filled
    print(f"  buy {size:>6}: {len(fills)} fills  eff={eff:.2f}  "
          f"slippage=+{eff - mid:.2f}")


def main():
    book = fresh_book()
    c1 = book.asks[0].size
    print(f"mid={book.mid:.2f}  mejor ask={book.asks[0].price} x {c1:.3f}")
    print("precios del snapshot + tamanos binarios normalizados")
    print("la ley del dia: mas tamano, peor precio ->")
    for size in (c1 / 2, c1 + book.asks[1].size / 2,
                 sum(level.size for level in book.asks[:3])):
        sweep(size)


if __name__ == "__main__":
    main()
'''),

    9: ("run_day.py", '''# Clase 9 - El loop de simulacion, en un archivo .py
# Ejecuta desde exercises/:  python run_day.py

from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.portfolio import PositionTracker


def main():
    market = Market.sample()
    tracker = PositionTracker()
    equity_curve = []
    step = 0

    while market.step() is not None:
        step += 1
        if step == 50:  # la decision: comprar en el paso 50
            for fill in market.submit(Order("BTCUSDT", "buy", 0.5,
                                            order_type=OrderType.MARKET)):
                tracker.apply_fill(fill)
                print(f"paso {step}: {fill}")
        equity_curve.append(tracker.equity(market.book.mid))

    print(f"dia completo: {step} pasos  posicion={tracker.position:.4f}  "
          f"equity final={equity_curve[-1]:.2f}")


if __name__ == "__main__":
    main()
'''),

    10: ("run_backtest.py", '''# Clase 10 - Strategy + Backtest, en un archivo .py
# Dos estrategias por el MISMO runner: el polimorfismo es el enchufe.
# Ejecuta desde exercises/:  python run_backtest.py

from exchange.backtest import Backtest
from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.strategy import NewOrder, Strategy


class BuyOnce(Strategy):
    def __init__(self, size=0.5):
        self.size = size
        self._done = False

    def on_book_update(self, book):
        if self._done:
            return []
        self._done = True
        return [NewOrder(Order("BTCUSDT", "buy", self.size,
                               order_type=OrderType.MARKET))]


class ImbalanceStrategy(Strategy):
    def __init__(self, thr=0.5, clip=0.05, max_pos=0.5):
        self.thr, self.clip, self.max_pos = thr, clip, max_pos
        self._pos = 0.0

    def on_book_update(self, book):
        imb = book.imbalance(1)
        if imb is None:
            return []
        if imb > self.thr and self._pos < self.max_pos:
            return [NewOrder(Order("BTCUSDT", "buy", self.clip,
                                   order_type=OrderType.MARKET))]
        if imb < -self.thr and self._pos > -self.max_pos:
            return [NewOrder(Order("BTCUSDT", "sell", self.clip,
                                   order_type=OrderType.MARKET))]
        return []

    def on_fill(self, fill):
        self._pos += fill.size if fill.side == "buy" else -fill.size


def main():
    for strategy in (BuyOnce(), ImbalanceStrategy()):
        result = Backtest(Market.sample(), strategy).run()
        print(f"{type(strategy).__name__:>18}: {result}")
    print("lineas del motor tocadas para cambiar de estrategia: 0")


if __name__ == "__main__":
    main()
'''),

    11: ("judge.py", '''# Clase 11 - El juicio: senal vs mono, arrival y slippage. En un .py.
# Ejecuta desde exercises/:  python judge.py

import random

from exchange.backtest import Backtest
from exchange.market import Market
from exchange.orders import Order, OrderType
from exchange.strategy import NewOrder, Strategy


class ImbalanceStrategy(Strategy):
    def __init__(self, thr=0.5, clip=0.05, max_pos=0.5):
        self.thr, self.clip, self.max_pos = thr, clip, max_pos
        self._pos, self._mid, self.slips = 0.0, None, []

    def on_book_update(self, book):
        self._mid = book.mid
        imb = book.imbalance(1)
        if imb is None:
            return []
        if imb > self.thr and self._pos < self.max_pos:
            return [NewOrder(Order("BTCUSDT", "buy", self.clip,
                                   order_type=OrderType.MARKET))]
        if imb < -self.thr and self._pos > -self.max_pos:
            return [NewOrder(Order("BTCUSDT", "sell", self.clip,
                                   order_type=OrderType.MARKET))]
        return []

    def on_fill(self, fill):
        self._pos += fill.size if fill.side == "buy" else -fill.size
        sign = 1 if fill.side == "buy" else -1
        self.slips.append(sign * (fill.price - self._mid))


class RandomStrategy(Strategy):
    """El mono con dardos: misma municion, cero senal."""

    def __init__(self, seed, p=0.06, clip=0.05, max_pos=0.5):
        self.rng, self.p, self.clip, self.max_pos = random.Random(seed), p, clip, max_pos
        self._pos = 0.0

    def on_book_update(self, book):
        if self.rng.random() > self.p:
            return []
        side = self.rng.choice(["buy", "sell"])
        if side == "buy" and self._pos >= self.max_pos:
            return []
        if side == "sell" and self._pos <= -self.max_pos:
            return []
        return [NewOrder(Order("BTCUSDT", side, self.clip,
                               order_type=OrderType.MARKET))]

    def on_fill(self, fill):
        self._pos += fill.size if fill.side == "buy" else -fill.size


def main():
    parent_arrival = Market.sample().step().mid
    print(f"parent-order arrival mid: {parent_arrival:.2f}")

    signal = ImbalanceStrategy()
    res = Backtest(Market.sample(), signal).run()
    avg_slip = sum(signal.slips) / len(signal.slips)
    cost = avg_slip * len(signal.slips) * signal.clip
    print(f"senal : equity={res.final_equity:>7.2f}  fills={res.n_fills}  "
          f"child slippage medio={avg_slip:.2f}  coste ejecucion~{cost:.1f}")
    print(f"bruto sin peaje ~ {res.final_equity + cost:.1f}")

    for seed in (7, 21, 99):
        r = Backtest(Market.sample(), RandomStrategy(seed)).run()
        print(f"mono {seed:>3}: equity={r.final_equity:>7.2f}  fills={r.n_fills}")


if __name__ == "__main__":
    main()
'''),

    12: ("run_vwap.py", '''# Clase 12 - Vender grande: de golpe vs TWAP vs VWAP. En un .py.
# Ejecuta desde exercises/:  python run_vwap.py

from exchange.backtest import Backtest
from exchange.market import Market
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType
from exchange.strategies.vwap import VWAPStrategy


def u_profile(n):
    """Perfil intradia en U: mas volumen en apertura y cierre."""
    return [0.6 + 1.6 * (2 * (i / (n - 1)) - 1) ** 2 for i in range(n)]


def avg_price(fills):
    total = sum(f.size for f in fills)
    return sum(f.price * f.size for f in fills) / total


def main():
    book = Market.sample(depth=5).step()
    total = round(sum(lv.size for lv in book.bids[:5]) * 0.9, 2)
    mid0 = book.mid
    print(f"vender {total} BTC  (mid inicial {mid0:.2f})")

    fills = MatchingEngine().process(
        Order("BTCUSDT", "sell", total, order_type=OrderType.MARKET), book)
    print(f"  de golpe : precio medio {avg_price(fills):.2f}")

    for name, profile in (("TWAP", None), ("VWAP-U", u_profile(500))):
        strat = VWAPStrategy("BTCUSDT", "sell", total, 500, profile)
        res = Backtest(Market.sample(), strat).run()
        print(f"  {name:<8}: precio medio {avg_price(res.fills):.2f}")


if __name__ == "__main__":
    main()
'''),

    13: ("run_mm.py", '''# Clase 13 - El market maker, con y sin correa. En un .py.
# Ejecuta desde exercises/:  python run_mm.py

from exchange.simulation import MMSimulation
from exchange.strategies import MarketMaker

SIGMA_HORIZON = 0.5
HORIZON = 500
ARRIVAL_INTENSITY = 520.0


def run(skew):
    mm = MarketMaker("SIM", quote_size=0.1, half_spread=0.6, inventory_skew=skew)
    res = MMSimulation(mm, s0=100.0, sigma=SIGMA_HORIZON,
                       steps=HORIZON, A=ARRIVAL_INTENSITY, seed=42).run()
    print(f"  skew={skew:>3}: PnL={res.final_pnl:>6.2f}  "
          f"max|inventario|={res.max_inventory:.2f}")


def main():
    print("misma semilla, mismo mercado; solo cambia la correa:")
    run(0.0)
    run(2.0)
    print("la correa domestica el inventario... y cuesta PnL. Trade-off.")


if __name__ == "__main__":
    main()
'''),

    14: ("mm_sweep.py", '''# Clase 14 - Avellaneda-Stoikov: el barrido de gamma. En un .py.
# Ejecuta desde exercises/:  python mm_sweep.py

from exchange.simulation import MMSimulation
from exchange.strategies import AvellanedaStoikov, MarketMaker

SIGMA_HORIZON = 0.5
HORIZON = 500
ARRIVAL_INTENSITY = 520.0


def run(strategy):
    return MMSimulation(strategy, s0=100.0, sigma=SIGMA_HORIZON, steps=HORIZON,
                        A=ARRIVAL_INTENSITY, kappa=1.5, seed=42).run()


def main():
    naive = run(MarketMaker("SIM", quote_size=0.1, half_spread=0.6,
                            inventory_skew=2.0))
    print(f"naive (L13)  : PnL={naive.final_pnl:>6.2f}  "
          f"max|inv|={naive.max_inventory:.2f}")

    print("gamma  PnL     max|inv|   <- la frontera riesgo/retorno")
    for gamma in (0.05, 0.2, 0.5, 1.0, 2.0):
        mm = AvellanedaStoikov("SIM", quote_size=0.1, gamma=gamma,
                               sigma=SIGMA_HORIZON, kappa=1.5, horizon=HORIZON)
        res = run(mm)
        print(f"{gamma:<5}  {res.final_pnl:>6.2f}   {res.max_inventory:.2f}")


if __name__ == "__main__":
    main()
'''),
}
