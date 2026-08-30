"""Datos sintéticos para el doc de L7: los 500 snapshots, resumidos por el motor."""
from exchange.market import Market


def build() -> dict:
    m = Market.sample()
    raw0 = m._snapshots[0]
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
    raw = []
    for i in range(1, 4):
        raw.append({
            "i": i,
            "bidPrice": float(raw0[f"bid_price_{i}"]),
            "bidSize": float(raw0[f"bid_size_{i}"]),
            "askPrice": float(raw0[f"ask_price_{i}"]),
            "askSize": float(raw0[f"ask_size_{i}"]),
        })
    first = snaps[0]
    return {"raw": raw, "snaps": snaps, "mids": mids, "imbs": imbs,
            "signalUps": ups, "signalTotal": total,
            "imb0": first["imb1"], "micro0": first["micro"], "mid0": first["mid"],
            "depthBid3": round(sum(x[1] for x in first["bids"]), 3),
            "depthAsk3": round(sum(x[1] for x in first["asks"]), 3)}
