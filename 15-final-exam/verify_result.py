"""verify_result.py — valida el código de resultado que emiten el examen y el
checkpoint al corregirse.

Cuando un alumno termina el examen (examen.html) o el checkpoint
(06-oop-iii-inheritance/checkpoint.html), la página le da un código como:

    AT26-L15-S0-R34-W3-B3-N8.13-27

que puede enviar al profesor. Este script lo descifra y comprueba que el
checksum cuadra (detecta un código mal copiado o manipulado a mano) y que la
nota es coherente con aciertos/fallos. No es seguridad criptográfica: es una
forma honesta y sin capturas de pantalla de reportar un resultado.

Uso:
    python verify_result.py AT26-L15-S0-R34-W3-B3-N8.13-27
    python verify_result.py           # modo interactivo (pega el código)
"""

from __future__ import annotations

import sys

EXAM_IDS = {"L15": ("Examen final", 40), "CK6": ("Checkpoint L1-L6", 20)}


def _checksum(seed: int, right: int, wrong: int, blank: int, total: int) -> str:
    # DEBE coincidir con checksum() del JS en generate_exam.py
    return str((right * 7 + wrong * 13 + blank * 17 + seed * 3 + total * 5) % 97).zfill(2)


def parse(code: str) -> dict:
    code = code.strip().upper()
    parts = code.split("-")
    if len(parts) != 8 or parts[0] != "AT26":
        raise ValueError("formato inesperado: se esperaba "
                         "AT26-<ID>-S<seed>-R<n>-W<n>-B<n>-N<nota>-<chk>")
    _, exid, s, r, w, b, n, chk = parts
    try:
        seed = int(s[1:]); right = int(r[1:]); wrong = int(w[1:])
        blank = int(b[1:]); nota = float(n[1:])
    except (ValueError, IndexError):
        raise ValueError("no pude leer los números del código")
    return {"exid": exid, "seed": seed, "right": right, "wrong": wrong,
            "blank": blank, "nota": nota, "chk": chk}


def verify(code: str) -> tuple[bool, str]:
    d = parse(code)
    name, total_expected = EXAM_IDS.get(d["exid"], ("Desconocido", None))
    total = d["right"] + d["wrong"] + d["blank"]
    problems = []

    good_chk = _checksum(d["seed"], d["right"], d["wrong"], d["blank"], total)
    if good_chk != d["chk"]:
        problems.append(f"checksum no cuadra (código dice {d['chk']}, debería ser {good_chk}): "
                        "código mal copiado o alterado")

    if total_expected is not None and total != total_expected:
        problems.append(f"suma {total} preguntas, pero {name} tiene {total_expected}")

    score = d["right"] - 0.5 * d["wrong"]
    nota_calc = max(0.0, score / total * 10) if total else 0.0
    if abs(nota_calc - d["nota"]) > 0.01:
        problems.append(f"la nota {d['nota']:.2f} no cuadra con "
                        f"{d['right']}✓/{d['wrong']}✗ (debería ser {nota_calc:.2f})")

    lines = [
        f"  Prueba     : {name} ({d['exid']})" + (f" · variante s{d['seed']}" if d["seed"] else ""),
        f"  Aciertos   : {d['right']}",
        f"  Fallos     : {d['wrong']}   (−0.5 c/u)",
        f"  En blanco  : {d['blank']}",
        f"  Puntuación : {score:.1f} / {total}",
        f"  Nota       : {nota_calc:.2f} / 10",
    ]
    ok = not problems
    if ok:
        lines.append("  Estado     : ✅ VÁLIDO — el código es consistente")
    else:
        lines.append("  Estado     : ❌ SOSPECHOSO")
        lines += [f"               · {p}" for p in problems]
    return ok, "\n".join(lines)


def main() -> None:
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = input("Pega el código de resultado: ").strip()
    try:
        ok, report = verify(code)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(2)
    print(report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
