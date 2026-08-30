"""capstone_scoring.py — baremo público de feedback formativo del capstone.
NO lo edites: es el contrato de esta puntuación de práctica, no una nota oficial.

Se ejecuta tu estrategia en 3 semillas reproducibles de práctica y se promedian dos números:
    pnl  = PnL final marcado a mercado (más = mejor)
    inv  = inventario máximo |q| alcanzado (menos = mejor: es tu riesgo)

Baremo sobre 100 (rúbrica 30 / 40 / 30):
    · PnL          (30):  cuánto spread capturas
    · Riesgo-ajust.(40):  PnL por unidad de inventario (el corazón del MM)
    · Inventario   (30):  cómo de plano te mantienes

Todas las referencias son PÚBLICAS: optimiza contra ellas sin sorpresas.
Antes de puntuar, una sonda pública exige que las cotizaciones reaccionen de
forma finita y direccional al inventario. El código de resultado solo detecta
errores de transcripción; no autentica autoría ni procedencia.
"""

from __future__ import annotations

import math
import re

# semillas reproducibles de práctica del capstone (fijas y públicas)
SEEDS = (2026, 7, 314)
STEPS = 500
# Intensidad por horizonte calibrada para que las referencias públicas de la
# rúbrica correspondan a cientos de oportunidades, no a una o dos llegadas.
ARRIVAL_INTENSITY = 630.0

# referencias del baremo (calibradas con market makers de referencia)
PNL_REF = 2.5      # un PnL de 2.5 ya satura la componente de PnL
INV_CAP = 0.30     # a partir de 0.30 de inventario, 0 puntos de control
RA_REF = 1.4       # ratio PnL/(1+10·inv) que satura la componente riesgo-ajustada
RA_INV_W = 10.0    # peso del inventario en el ratio riesgo-ajustado
INVENTORY_PROBE = 0.20
MIN_CENTER_SHIFT = 1e-4


class StrategyEligibilityError(ValueError):
    """La estrategia corre, pero no cumple el contrato mínimo del capstone."""


def _clamp(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def score(avg_pnl: float, avg_inv: float) -> dict:
    """Devuelve el feedback puntuado a partir de (pnl medio, inv medio)."""
    avg_pnl, avg_inv = float(avg_pnl), float(avg_inv)
    if not math.isfinite(avg_pnl) or not math.isfinite(avg_inv):
        raise ValueError("pnl e inventario deben ser finitos")
    if avg_inv < 0:
        raise ValueError("el inventario máximo no puede ser negativo")
    ra = avg_pnl / (1 + avg_inv * RA_INV_W)
    pnl_pts = 30 * _clamp(avg_pnl / PNL_REF)
    ra_pts = 40 * _clamp(ra / RA_REF)
    inv_pts = 30 * _clamp(1 - avg_inv / INV_CAP)
    total = pnl_pts + ra_pts + inv_pts
    return {"pnl": avg_pnl, "inv": avg_inv, "ra": ra,
            "pnl_pts": pnl_pts, "ra_pts": ra_pts, "inv_pts": inv_pts,
            "total": total}


def validate_strategy(make_strategy) -> dict:
    """Prueba que el centro de cotización controla inventario en ambas direcciones.

    La sonda usa tres instancias nuevas para aislar estado. A inventario largo
    el centro debe bajar; a inventario corto debe subir. Se aceptan overrides de
    ``quotes`` o ``reservation_price`` siempre que su conducta sea equivalente.
    """
    from exchange.book import Level, OrderBook

    def quote_center(inventory: float) -> float:
        strategy = make_strategy()
        try:
            strategy.inventory = inventory
            book = OrderBook(strategy.symbol,
                             [Level(99.0, 1.0)], [Level(101.0, 1.0)])
            bid, ask = strategy.quotes(book)
            bid, ask = float(bid), float(ask)
        except NotImplementedError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise StrategyEligibilityError(
                f"no se pudo sondear la decisión de inventario: {exc}"
            ) from exc
        if not all(math.isfinite(px) and px > 0 for px in (bid, ask)):
            raise StrategyEligibilityError("las cotizaciones deben ser finitas y positivas")
        if bid >= ask:
            raise StrategyEligibilityError("el bid debe quedar estrictamente por debajo del ask")
        return (bid + ask) / 2

    short_center = quote_center(-INVENTORY_PROBE)
    flat_center = quote_center(0.0)
    long_center = quote_center(INVENTORY_PROBE)
    if not (short_center >= flat_center + MIN_CENTER_SHIFT
            and long_center <= flat_center - MIN_CENTER_SHIFT):
        raise StrategyEligibilityError(
            "el centro debe subir con inventario corto y bajar con inventario largo"
        )
    return {"short_center": short_center, "flat_center": flat_center,
            "long_center": long_center}


def run_metrics(make_strategy) -> tuple[float, float, list]:
    """Corre la estrategia (make_strategy() -> instancia nueva) en las 3 semillas.
    Devuelve (pnl medio, inv medio, detalle por semilla)."""
    from exchange.simulation import MMSimulation
    validate_strategy(make_strategy)
    rows = []
    for s in SEEDS:
        res = MMSimulation(make_strategy(), steps=STEPS,
                           A=ARRIVAL_INTENSITY, seed=s).run()
        rows.append((s, res.final_pnl, res.max_inventory))
    # Los mismos tres decimales que viajan en el código son los que se puntúan;
    # así parsear y recomputar nunca depende de cifras ocultas.
    avg_pnl = round(sum(r[1] for r in rows) / len(rows), 3)
    avg_inv = round(sum(r[2] for r in rows) / len(rows), 3)
    return avg_pnl, avg_inv, rows


def result_code(total: float, avg_pnl: float, avg_inv: float) -> str:
    total, avg_pnl, avg_inv = map(float, (total, avg_pnl, avg_inv))
    if not all(math.isfinite(value) for value in (total, avg_pnl, avg_inv)):
        raise ValueError("puntuación, pnl e inventario deben ser finitos")
    avg_pnl, avg_inv = round(avg_pnl, 3), round(avg_inv, 3)
    canonical_total = round(score(avg_pnl, avg_inv)["total"], 1)
    if round(total, 1) != canonical_total:
        raise ValueError("la puntuación no coincide con el PnL/inventario declarados")
    chk = checksum(canonical_total, avg_pnl, avg_inv)
    return (f"AT26-CAP-N{canonical_total:.1f}-P{avg_pnl:.3f}-"
            f"I{avg_inv:.3f}-{chk}")


def checksum(total: float, avg_pnl: float, avg_inv: float) -> str:
    # Huella pública de transcripción, no firma criptográfica. Incluye el signo
    # del PnL; la autoridad sigue siendo reejecutar ``mi_estrategia.py``.
    a = round(total * 10)
    b = round(avg_pnl * 1000)
    c = round(avg_inv * 1000)
    return str((a * 131 + b * 17 + c * 19 + 7) % 9973).zfill(4)


def parse_code(code: str) -> dict:
    match = re.fullmatch(
        r"AT26-CAP-N(?P<total>\d+(?:\.\d)?)-"
        r"P(?P<pnl>[+-]?\d+(?:\.\d{1,3})?)-"
        r"I(?P<inv>\d+(?:\.\d{1,3})?)-(?P<chk>\d{4})",
        code.strip().upper(),
    )
    if match is None:
        raise ValueError("formato: AT26-CAP-N<puntuación>-P<pnl>-I<inv>-<chk>")
    total = float(match.group("total"))
    pnl = float(match.group("pnl"))
    inv = float(match.group("inv"))
    chk = match.group("chk")
    if not all(math.isfinite(value) for value in (total, pnl, inv)):
        raise ValueError("puntuación, pnl e inventario deben ser finitos")
    if not 0.0 <= total <= 100.0 or inv < 0.0:
        raise ValueError("puntuación fuera de [0,100] o inventario negativo")
    checksum_valid = checksum(total, pnl, inv) == chk
    score_valid = total == round(score(pnl, inv)["total"], 1)
    return {"total": total, "pnl": pnl, "inv": inv, "chk": chk,
            "checksum_valid": checksum_valid, "score_valid": score_valid,
            "valid": checksum_valid and score_valid}
