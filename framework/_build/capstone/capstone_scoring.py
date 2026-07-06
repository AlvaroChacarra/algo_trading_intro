"""capstone_scoring.py — baremo público del capstone (compartido por el
corrector y el leaderboard). NO lo edites: es el contrato de la nota.

Se ejecuta tu estrategia en 3 semillas oficiales y se promedian dos números:
    pnl  = PnL final marcado a mercado (más = mejor)
    inv  = inventario máximo |q| alcanzado (menos = mejor: es tu riesgo)

Baremo sobre 100 (rúbrica 30 / 40 / 30):
    · PnL          (30):  cuánto spread capturas
    · Riesgo-ajust.(40):  PnL por unidad de inventario (el corazón del MM)
    · Inventario   (30):  cómo de plano te mantienes

Todas las referencias son PÚBLICAS: optimiza contra ellas sin sorpresas.
"""

from __future__ import annotations

# semillas oficiales del capstone (fijas y públicas)
SEEDS = (2026, 7, 314)
STEPS = 500

# referencias del baremo (calibradas con market makers de referencia)
PNL_REF = 2.5      # un PnL de 2.5 ya satura la componente de PnL
INV_CAP = 0.30     # a partir de 0.30 de inventario, 0 puntos de control
RA_REF = 1.4       # ratio PnL/(1+10·inv) que satura la componente riesgo-ajustada
RA_INV_W = 10.0    # peso del inventario en el ratio riesgo-ajustado


def _clamp(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def score(avg_pnl: float, avg_inv: float) -> dict:
    """Devuelve el desglose de la nota a partir de (pnl medio, inv medio)."""
    ra = avg_pnl / (1 + avg_inv * RA_INV_W)
    pnl_pts = 30 * _clamp(avg_pnl / PNL_REF)
    ra_pts = 40 * _clamp(ra / RA_REF)
    inv_pts = 30 * _clamp(1 - avg_inv / INV_CAP)
    total = pnl_pts + ra_pts + inv_pts
    return {"pnl": avg_pnl, "inv": avg_inv, "ra": ra,
            "pnl_pts": pnl_pts, "ra_pts": ra_pts, "inv_pts": inv_pts,
            "total": total}


def run_metrics(make_strategy) -> tuple[float, float, list]:
    """Corre la estrategia (make_strategy() -> instancia nueva) en las 3 semillas.
    Devuelve (pnl medio, inv medio, detalle por semilla)."""
    from exchange.simulation import MMSimulation
    rows = []
    for s in SEEDS:
        res = MMSimulation(make_strategy(), steps=STEPS, seed=s).run()
        rows.append((s, res.final_pnl, res.max_inventory))
    avg_pnl = sum(r[1] for r in rows) / len(rows)
    avg_inv = sum(r[2] for r in rows) / len(rows)
    return avg_pnl, avg_inv, rows


def result_code(total: float, avg_pnl: float, avg_inv: float) -> str:
    chk = checksum(total, avg_pnl, avg_inv)
    return f"AT26-CAP-N{total:.1f}-P{avg_pnl:.3f}-I{avg_inv:.3f}-{chk}"


def checksum(total: float, avg_pnl: float, avg_inv: float) -> str:
    # módulo primo grande: una colisión exigiría ±997 puntos de nota (imposible),
    # así que detecta cualquier nota/pnl/inv retocado a mano dentro del rango real.
    a = round(total * 10)
    b = abs(round(avg_pnl * 1000))
    c = abs(round(avg_inv * 1000))
    return str((a * 131 + b * 17 + c * 19 + 7) % 9973).zfill(4)


def parse_code(code: str) -> dict:
    parts = code.strip().upper().split("-")
    if len(parts) != 6 or parts[0] != "AT26" or parts[1] != "CAP":
        raise ValueError("formato: AT26-CAP-N<nota>-P<pnl>-I<inv>-<chk>")
    total = float(parts[2][1:]); pnl = float(parts[3][1:])
    inv = float(parts[4][1:]); chk = parts[5]
    ok = checksum(total, pnl, inv) == chk
    return {"total": total, "pnl": pnl, "inv": inv, "chk": chk, "valid": ok}
