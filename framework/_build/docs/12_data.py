"""Datos reales para el doc de L12: vender grande de golpe vs troceado
(TWAP / VWAP), todo ejecutado por el motor de referencia."""
from copy import deepcopy

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


def realized_activity(horizon: int) -> list[float]:
    """Actividad real por snapshot: tamaño agregado en 5 niveles de ambos lados.
    Es el 'volumen visible' del que dispone un algoritmo para predecir."""
    m = Market.sample()
    acts = []
    while True:
        b = m.step()
        if b is None:
            break
        acts.append(sum(lv.size for lv in b.bids[:5]) + sum(lv.size for lv in b.asks[:5]))
    return acts[:horizon]


def _mae(pred: list[float], actual: list[float]) -> float:
    return sum(abs(p - a) for p, a in zip(pred, actual)) / len(actual)


def build() -> dict:
    m = Market.sample(depth=5)
    m.step()
    total = round(sum(lv.size for lv in m.book.bids[:5]) * 0.9, 2)
    mid0 = m.book.mid

    # de golpe: una market sell del total contra el primer snapshot
    fills = MatchingEngine().process(
        Order("BTCUSDT", "sell", total, order_type=OrderType.MARKET), deepcopy(m.book))
    sweep_avg = round(avg_price(fills), 2)
    sweep_filled = round(sum(f.size for f in fills), 3)

    horizon = 500
    _, twap_avg = run_vwap(None, total, horizon)
    prof = u_profile(horizon)
    _, vwap_avg = run_vwap(prof, total, horizon)

    # perfil (U) agregado a 25 barras para pintarlo
    n_b = 25
    bars = [0.0] * n_b
    for i, w in enumerate(prof):
        bars[min(n_b - 1, i * n_b // horizon)] += w
    s = sum(bars)
    bars = [round(b / s, 4) for b in bars]

    # ── predecir el volumen: ¿merece la pena un modelo? ──────────────────
    # actividad REAL agregada a 25 barras (media por barra)
    acts = realized_activity(horizon)
    vol = [0.0] * n_b
    cnt = [0] * n_b
    for i, v in enumerate(acts):
        j = min(n_b - 1, i * n_b // horizon)
        vol[j] += v
        cnt[j] += 1
    vol = [vol[j] / cnt[j] for j in range(n_b)]
    mean_v = sum(vol) / n_b

    # dos predictores del volumen de la barra i (para i>=1):
    #   estático  = la media global (perfil fijo)
    #   rolado    = media de las k barras anteriores (modelo "dinámico")
    k = 3
    static_pred = [mean_v] * (n_b - 1)
    roll_pred = [sum(vol[max(0, i - k):i]) / len(vol[max(0, i - k):i]) for i in range(1, n_b)]
    mae_static = _mae(static_pred, vol[1:])
    mae_roll = _mae(roll_pred, vol[1:])

    # ¿y si el perfil fuese el volumen REAL (previsión perfecta)?
    _, oracle_avg = run_vwap(acts, total, horizon)

    return {"total": total, "mid0": round(mid0, 2),
            "sweepAvg": sweep_avg, "sweepFilled": sweep_filled,
            "twapAvg": twap_avg, "vwapAvg": vwap_avg,
            "bars": bars,
            "sweepCostBps": round((mid0 - sweep_avg) / mid0 * 10000, 2),
            "twapCostBps": round((mid0 - twap_avg) / mid0 * 10000, 2),
            "vwapCostBps": round((mid0 - vwap_avg) / mid0 * 10000, 2),
            # sección "predecir el volumen"
            "vol": [round(v, 2) for v in vol],
            "volMean": round(mean_v, 2),
            "staticPred": [round(v, 2) for v in static_pred],
            "rollPred": [round(v, 2) for v in roll_pred],
            "rollK": k,
            "maeStatic": round(mae_static, 3),
            "maeRoll": round(mae_roll, 3),
            "oracleAvg": oracle_avg,
            "oracleVsTwapBps": round((oracle_avg - twap_avg) / twap_avg * 10000, 2)}
