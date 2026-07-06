"""capstone_check.py — corrige TU market maker del capstone.

Ejecuta `MiEstrategia` (de mi_estrategia.py) en las 3 semillas oficiales,
aplica el baremo público (capstone_scoring.py) y te da la nota desglosada más
un código de resultado copiable para el leaderboard / el profe.

    python capstone_check.py

No edites este archivo ni capstone_scoring.py: son el contrato de la nota.
Tu trabajo vive entero en mi_estrategia.py.
"""

from __future__ import annotations

import os
import sys

# el paquete exchange y los módulos hermanos viven junto a este archivo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import capstone_scoring as sc  # noqa: E402


def _bar(pts: float, mx: float, width: int = 24) -> str:
    n = int(round(width * pts / mx)) if mx else 0
    return "█" * n + "·" * (width - n)


def main() -> None:
    try:
        from mi_estrategia import MiEstrategia
    except Exception as e:  # noqa: BLE001
        print(f"❌ No pude importar MiEstrategia de mi_estrategia.py: {e}")
        sys.exit(2)

    try:
        avg_pnl, avg_inv, rows = sc.run_metrics(MiEstrategia)
    except Exception as e:  # noqa: BLE001
        print(f"❌ Tu estrategia reventó al simularse: {type(e).__name__}: {e}")
        sys.exit(2)

    d = sc.score(avg_pnl, avg_inv)

    print("\n  CAPSTONE · tu market maker en 3 semillas oficiales")
    print("  " + "─" * 52)
    for s, pnl, inv in rows:
        print(f"    seed {s:>4}   PnL {pnl:8.3f}   max|inv| {inv:6.3f}")
    print("  " + "─" * 52)
    print(f"    media      PnL {avg_pnl:8.3f}   max|inv| {avg_inv:6.3f}   "
          f"ratio {d['ra']:.3f}")
    print()
    print(f"    PnL            {d['pnl_pts']:5.1f} / 30   {_bar(d['pnl_pts'], 30)}")
    print(f"    Riesgo-ajust.  {d['ra_pts']:5.1f} / 40   {_bar(d['ra_pts'], 40)}")
    print(f"    Inventario     {d['inv_pts']:5.1f} / 30   {_bar(d['inv_pts'], 30)}")
    print("  " + "─" * 52)
    print(f"    NOTA           {d['total']:5.1f} / 100")
    print()
    code = sc.result_code(d["total"], avg_pnl, avg_inv)
    print(f"    código de resultado:  {code}")
    print("    (envíalo al profe / al leaderboard: certifica tu nota)\n")


if __name__ == "__main__":
    main()
