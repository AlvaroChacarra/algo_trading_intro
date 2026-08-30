"""leaderboard.py — lector de autoinformes del capstone.

Lee un archivo de texto con una línea por alumno:

    Ada Lovelace    AT26-CAP-N90.3-P2.448-I0.080-XX
    Alan Turing     AT26-CAP-N62.1-P2.237-I0.183-YY

(el nombre, luego espacios/tab, luego el código). El checksum solo comprueba
consistencia/transcripción: cualquiera puede fabricarlo porque la fórmula es
pública. Por eso ningún código recibe rango ni acredita una nota. La validación
docente exige reejecutar ``mi_estrategia.py`` en un entorno controlado.

    python leaderboard.py entregas.txt
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import capstone_scoring as sc  # noqa: E402


def parse_file(path: str) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            *name_parts, code = ln.split()
            name = " ".join(name_parts) or "(sin nombre)"
            try:
                d = sc.parse_code(code)
            except ValueError:
                out.append({"name": name, "total": -1, "valid": False, "bad": True})
                continue
            out.append({"name": name, **d, "bad": not d["valid"], "verified": False})
    return out


def partition_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Rank only externally verified rows; public codes remain unranked."""
    verified = sorted(
        (row for row in rows if not row.get("bad") and row.get("verified") is True),
        key=lambda row: row["total"], reverse=True,
    )
    unranked = [row for row in rows if row not in verified]
    return verified, unranked


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python leaderboard.py <archivo_de_entregas.txt>")
        sys.exit(2)
    rows = parse_file(sys.argv[1])
    ranked, invalid = partition_rows(rows)

    print("\n  CAPSTONE · autoinformes (sin rango automático)")
    print("  " + "─" * 58)
    print(f"  {'#':>2}  {'alumno':<22}{'puntos':>7}{'PnL':>9}{'inv':>8}  ")
    print("  " + "─" * 58)
    for rank, r in enumerate(ranked, start=1):
        print(f"  {rank:>2}  {r['name']:<22}{r['total']:>7.1f}"
              f"{r['pnl']:>9.3f}{r['inv']:>8.3f}")
    for r in invalid:
        reason = "código inválido" if r.get("bad") else "autoinforme no verificado"
        print(f"      {r['name']:<22}{'—':>7}   {reason}; reejecutar")
    print("  " + "─" * 58 + "\n")


if __name__ == "__main__":
    main()
