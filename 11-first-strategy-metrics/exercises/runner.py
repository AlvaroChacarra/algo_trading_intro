"""Un runner común: coordinar decisiones, fills, costes y valoración."""
from math import isfinite
from portfolio import PositionTracker
from exchange.strategy import NewOrder
from exchange.orders import OrderType
from exchange.backtest import Context


class FeePortfolio(PositionTracker):
    def charge(self, fee):
        if not isfinite(fee) or fee < 0:
            raise ValueError('comisión finita y no negativa')
        # Ejercicio 3A: resta fee de self.cash en FeePortfolio.charge; conserva la validación proporcionada.
        self.cash -= fee


class ResearchResult:
    def __init__(self):
        self.equity_curve = []
        self.positions = []
        self.fills = []
        self.fees = 0.0
        self.final_cash = 0.0
        self.final_position = 0.0
        self.final_equity = 0.0

    @property
    def n_steps(self):
        # Ejercicio 3B: deriva n_steps de equity_curve y n_fills de fills, sin contadores independientes.
        return len(self.equity_curve)

    @property
    def n_fills(self):
        # Ejercicio 3B: deriva n_steps de equity_curve y n_fills de fills, sin contadores independientes.
        return len(self.fills)


class ResearchBacktest:
    def __init__(self, market, strategy, fee_bps=0.0, cash=1000):
        if not isfinite(fee_bps) or fee_bps < 0 or not isfinite(cash):
            raise ValueError('cash finito y comisiones finitas no negativas')
        self.market = market
        self.strategy = strategy
        self.fee_bps = fee_bps
        self.cash = cash

    def run(self):
        self.market.reset()
        tracker = FeePortfolio(self.cash)
        ctx = Context(self.market, tracker)
        result = ResearchResult()
        # Ejercicio 3C: llama on_start(ctx) antes del bucle de ResearchBacktest.run para reiniciar la estrategia.
        self.strategy.on_start(ctx)
        while True:
            book = self.market.step()
            if book is None:
                break
            mark = book.mid
            if mark is None:
                raise ValueError('el replay requiere dos lados para valorar')
            for action in self.strategy.on_book_update(book):
                if not isinstance(action, NewOrder):
                    raise ValueError('este runner admite acciones NewOrder')
                if action.order.order_type not in (OrderType.MARKET, OrderType.IOC):
                    raise ValueError('este runner admite solo MARKET/IOC')
                for fill in self.market.submit(action.order):
                    # Ejercicio 3D: registra cada fill en la cartera, cobra su fee una vez y notifica strategy.on_fill(fill).
                    tracker.apply_fill(fill)
                    fee = fill.price * fill.size * self.fee_bps / 10000
                    # Ejercicio 3D: registra cada fill en la cartera, cobra su fee una vez y notifica strategy.on_fill(fill).
                    tracker.charge(fee)
                    result.fees += fee
                    result.fills.append(fill)
                    # Ejercicio 3D: registra cada fill en la cartera, cobra su fee una vez y notifica strategy.on_fill(fill).
                    self.strategy.on_fill(fill)
            result.equity_curve.append(tracker.equity(mark))
            result.positions.append(tracker.position)
        result.final_cash = tracker.cash
        result.final_position = tracker.position
        result.final_equity = (result.equity_curve[-1]
                               if result.equity_curve else tracker.cash)
        # Ejercicio 3E: llama on_end(ctx) tras la contabilidad final y antes de devolver el resultado.
        self.strategy.on_end(ctx)
        return result
