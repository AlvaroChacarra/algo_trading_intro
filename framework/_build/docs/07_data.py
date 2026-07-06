"""Datos reales para el doc de L7: los 500 snapshots, resumidos por el motor."""
from exchange.market import Market


def build() -> dict:
    m = Market.sample()
    snaps, mids, imbs = [], [], []
    while m.step() is not None:
        b = m.book
        snaps.append({
            "bids": [[lv.price, round(lv.size, 3)] for lv in b.bids[:3]],
            "asks": [[lv.price, round(lv.size, 3)] for lv in b.asks[:3]],
            "mid": round(b.mid, 2), "spread": round(b.spread, 2),
            "imb1": round(b.imbalance(1), 3), "imb5": round(b.imbalance(5), 3),
            "micro": round(b.microprice, 2),
        })
        mids.append(round(b.mid, 2))
        imbs.append(round(b.imbalance(1), 3))

    # la pregunta empírica: tras imbalance(1) > 0.3, ¿el mid sube en el paso siguiente?
    ups = total = 0
    for i in range(len(mids) - 1):
        if imbs[i] > 0.3:
            total += 1
            if mids[i + 1] > mids[i]:
                ups += 1
    return {"snaps": snaps, "mids": mids, "imbs": imbs,
            "signalUps": ups, "signalTotal": total,
            "imb0": snaps[0]["imb1"], "micro0": snaps[0]["micro"], "mid0": snaps[0]["mid"]}
