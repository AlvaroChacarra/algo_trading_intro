"""Datos reales para el doc de L12: vender grande de golpe vs troceado
(TWAP / VWAP), todo ejecutado por el motor de referencia."""
from exchange.backtest import Backtest
from exchange.market import Market
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType
from exchange.strategies.vwap import VWAPStrategy


def u_profile(n: int) -> list[float]:
    """Perfil intradía en U: más volumen en apertura y cierre."""
    return [0.6 + 1.6 * (2 * (i / (n - 1)) - 1) ** 2 for i in range(n)]


def avg_price(fills) -> float:
    tot = sum(f.size for f in fills)
    return sum(f.price * f.size for f in fills) / tot if tot else 0.0


def run_vwap(profile, total, horizon):
    strat = VWAPStrategy("BTCUSDT", "sell", total, horizon, profile)
    res = Backtest(Market.sample(), strat).run()
    return res, round(avg_price(res.fills), 2)


def build() -> dict:
    m = Market.sample(depth=5)
    m.step()
    total = round(sum(lv.size for lv in m.book.bids[:5]) * 0.9, 2)
    mid0 = m.book.mid

    # de golpe: una market sell del total contra el primer snapshot
    fills = MatchingEngine().process(
        Order("BTCUSDT", "sell", total, order_type=OrderType.MARKET), m.book.copy())
    sweep_avg = round(avg_price(fills), 2)
    sweep_filled = round(sum(f.size for f in fills), 3)

    horizon = 500
    _, twap_avg = run_vwap(None, total, horizon)
    prof = u_profile(horizon)
    _, vwap_avg = run_vwap(prof, total, horizon)

    # perfil agregado a 25 barras para pintarlo
    n_b = 25
    bars = [0.0] * n_b
    for i, w in enumerate(prof):
        bars[min(n_b - 1, i * n_b // horizon)] += w
    s = sum(bars)
    bars = [round(b / s, 4) for b in bars]

    return {"total": total, "mid0": round(mid0, 2),
            "sweepAvg": sweep_avg, "sweepFilled": sweep_filled,
            "twapAvg": twap_avg, "vwapAvg": vwap_avg,
            "bars": bars,
            "sweepCostBps": round((mid0 - sweep_avg) / mid0 * 10000, 2),
            "twapCostBps": round((mid0 - twap_avg) / mid0 * 10000, 2),
            "vwapCostBps": round((mid0 - vwap_avg) / mid0 * 10000, 2)}
