"""leaderboard.py — ranking del capstone a partir de los códigos de resultado.

Lee un archivo de texto con una línea por alumno:

    Ada Lovelace    AT26-CAP-N90.3-P2.448-I0.080-XX
    Alan Turing     AT26-CAP-N62.1-P2.237-I0.183-YY

(el nombre, luego espacios/tab, luego el código). Valida el checksum de cada
código y ordena por nota. Marca en rojo los códigos que no cuadran (mal
copiados o alterados a mano) — para esos, pide reejecutar mi_estrategia.py.

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
            out.append({"name": name, **d, "bad": False})
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python leaderboard.py <archivo_de_entregas.txt>")
        sys.exit(2)
    rows = parse_file(sys.argv[1])
    rows.sort(key=lambda r: r["total"], reverse=True)

    print("\n  🏆 CAPSTONE · leaderboard")
    print("  " + "─" * 58)
    print(f"  {'#':>2}  {'alumno':<22}{'nota':>7}{'PnL':>9}{'inv':>8}  ")
    print("  " + "─" * 58)
    rank = 0
    for r in rows:
        if r.get("bad"):
            print(f"      {r['name']:<22}{'—':>7}   código ilegible")
            continue
        rank += 1
        flag = "" if r["valid"] else "  ⚠ checksum no cuadra (reejecutar)"
        print(f"  {rank:>2}  {r['name']:<22}{r['total']:>7.1f}"
              f"{r['pnl']:>9.3f}{r['inv']:>8.3f}{flag}")
    print("  " + "─" * 58 + "\n")


if __name__ == "__main__":
    main()
