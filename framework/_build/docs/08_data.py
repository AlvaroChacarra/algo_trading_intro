"""Escenarios de L8 calculados por el MatchingEngine canónico.

El JS solo representa estos resultados: fills, planes y books finales salen del
motor Python de referencia para evitar dos implementaciones numéricas divergentes.
"""
from exchange.market import Market
from exchange.matching import MatchingEngine
from exchange.orders import Order, OrderType


def build() -> dict:
    m = Market.sample(depth=5)
    m.step()
    book0 = m.book
    mid = book0.mid
    engine = MatchingEngine()

    asks = [[lv.price, round(lv.size, 6)] for lv in book0.asks[:5]]
    bids = [[lv.price, round(lv.size, 6)] for lv in book0.bids[:5]]
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
    size_options = [
        round(c1 * 0.5, 6),
        round(c1 + book0.asks[1].size * 0.6, 6),
        round(c3 * 1.2, 6),
    ]
    scenarios = []
    for side in ("buy", "sell"):
        levels = book0.asks if side == "buy" else book0.bids
        limit_prices = [levels[i].price for i in range(3)]
        for otype in (OrderType.MARKET, OrderType.LIMIT, OrderType.IOC, OrderType.FOK):
            for size_i, size in enumerate(size_options):
                price_indexes = [-1] if otype is OrderType.MARKET else range(3)
                for price_i in price_indexes:
                    price = None if price_i == -1 else limit_prices[price_i]
                    before = book0.copy()
                    after = book0.copy()
                    order = Order("BTCUSDT", side, size, price=price, order_type=otype)

                    opposite = before.asks if side == "buy" else before.bids
                    remaining = size
                    planned = []
                    for lv in opposite:
                        if remaining <= 1e-12:
                            break
                        crosses = (otype is OrderType.MARKET or
                                   (price >= lv.price if side == "buy" else price <= lv.price))
                        if not crosses:
                            break
                        take = min(remaining, lv.size)
                        planned.append([lv.price, round(take, 6)])
                        remaining -= take

                    fills = engine.process(order, after)
                    scenarios.append({
                        "key": f"{side}:{otype.value}:{size_i}:{price_i}",
                        "side": side, "type": otype.value, "sizeI": size_i,
                        "priceI": price_i, "size": size, "price": price,
                        "planned": planned, "remaining": round(remaining, 6),
                        "fills": [[f.price, round(f.size, 6)] for f in fills],
                        "before": {
                            "bids": [[x.price, round(x.size, 6)] for x in before.bids[:5]],
                            "asks": [[x.price, round(x.size, 6)] for x in before.asks[:5]],
                        },
                        "after": {
                            "bids": [[x.price, round(x.size, 6)] for x in after.bids[:6]],
                            "asks": [[x.price, round(x.size, 6)] for x in after.asks[:6]],
                        },
                    })

    # Contraejemplo pedagógico calculado, no hardcodeado: una FOK BUY que no
    # cabe al precio del tercer ask. La implementación canónica deja el libro
    # intacto; la versión ingenua aplica el plan antes de validar y lo corrompe.
    fok_key = "buy:fok:2:2"
    fok_scenario = next(s for s in scenarios if s["key"] == fok_key)
    naive_book = book0.copy()
    for price, take in fok_scenario["planned"]:
        naive_book.reduce("sell", price, take)
    fok_bug = {
        "key": fok_key,
        "size": fok_scenario["size"],
        "price": fok_scenario["price"],
        "planned": fok_scenario["planned"],
        "remaining": fok_scenario["remaining"],
        "before": fok_scenario["before"],
        "canonicalAfter": fok_scenario["after"],
        "naiveAfter": {
            "bids": [[x.price, round(x.size, 6)] for x in naive_book.bids[:6]],
            "asks": [[x.price, round(x.size, 6)] for x in naive_book.asks[:6]],
        },
    }

    return {"bids": bids, "asks": asks, "mid": round(mid, 2),
            "spread": round(book0.spread, 2), "sweeps": sweeps,
            "limPx": lim_px, "big": big, "variants": variants,
            "sizes": size_options,
            "limitPrices": {"buy": [x.price for x in book0.asks[:3]],
                            "sell": [x.price for x in book0.bids[:3]]},
            "scenarios": scenarios, "fokBug": fok_bug}
