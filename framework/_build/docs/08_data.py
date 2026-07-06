"""Datos reales para el doc de L8: barridos de market orders calculados por el
MatchingEngine de referencia sobre el primer snapshot real."""
from exchange.market import Market
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType


def build() -> dict:
    m = Market.sample(depth=5)
    m.step()
    book0 = m.book
    mid = book0.mid
    engine = MatchingEngine()

    asks = [[lv.price, round(lv.size, 3)] for lv in book0.asks[:5]]
    bids = [[lv.price, round(lv.size, 3)] for lv in book0.bids[:5]]
    c1 = book0.asks[0].size
    c3 = sum(lv.size for lv in book0.asks[:3])
    c5 = sum(lv.size for lv in book0.asks[:5])
    sizes = [round(c1 * 0.5, 3), round(c1 + book0.asks[1].size * 0.4, 3),
             round(c3, 3), round(c5 * 1.15, 3)]

    sweeps = []
    for size in sizes:
        fills = engine.process(Order("BTCUSDT", "buy", size, order_type=OrderType.MARKET),
                               book0.copy())
        filled = sum(f.size for f in fills)
        notional = sum(f.price * f.size for f in fills)
        eff = notional / filled if filled else None
        sweeps.append({
            "size": size,
            "fills": [[f.price, round(f.size, 3)] for f in fills],
            "filled": round(filled, 3),
            "eff": round(eff, 2) if eff else None,
            "slip": round(eff - mid, 2) if eff else None,
        })

    # limit / IOC / FOK sobre el mismo libro, precio límite = 2º nivel ask
    lim_px = book0.asks[1].price
    big = round(c3 * 1.4, 3)
    variants = {}
    for name, otype in (("limit", OrderType.LIMIT), ("ioc", OrderType.IOC),
                        ("fok", OrderType.FOK)):
        bk = book0.copy()
        fills = engine.process(Order("BTCUSDT", "buy", big, price=lim_px,
                                     order_type=otype), bk)
        filled = sum(f.size for f in fills)
        rest = 0.0
        for lv in bk.bids:
            if abs(lv.price - lim_px) < 1e-9:
                rest = lv.size
        variants[name] = {"filled": round(filled, 3),
                          "rest": round(rest, 3),
                          "nfills": len(fills)}
    return {"bids": bids, "asks": asks, "mid": round(mid, 2),
            "spread": round(book0.spread, 2), "sweeps": sweeps,
            "limPx": lim_px, "big": big, "variants": variants}
