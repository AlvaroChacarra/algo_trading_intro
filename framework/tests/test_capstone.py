"""Regresión del capstone: el baremo es monótono en lo que debe, el código de
resultado es reproducible y su checksum detecta manipulaciones. Importa los
módulos generados en la carpeta de ejercicios de L14."""

import os
import sys

import pytest

HERE = os.path.dirname(__file__)
EXER = os.path.abspath(os.path.join(HERE, "..", "..",
                                    "14-avellaneda-stoikov", "exercises"))
sys.path.insert(0, EXER)

import capstone_scoring as sc  # noqa: E402


def test_semillas_y_referencias_publicas():
    assert sc.SEEDS == (2026, 7, 314) and sc.STEPS == 500
    assert sc.PNL_REF > 0 and sc.INV_CAP > 0 and sc.RA_REF > 0


def test_baremo_acotado_0_100():
    for pnl, inv in [(-5, 5), (0, 0), (2.5, 0), (100, 0), (2.5, 1.0)]:
        d = sc.score(pnl, inv)
        assert 0 <= d["total"] <= 100


def test_mas_pnl_no_baja_la_nota():
    a = sc.score(1.0, 0.1)["total"]
    b = sc.score(2.0, 0.1)["total"]
    assert b >= a


def test_menos_inventario_no_baja_la_nota():
    a = sc.score(2.0, 0.20)["total"]
    b = sc.score(2.0, 0.05)["total"]
    assert b >= a


def test_codigo_roundtrip_valido():
    d = sc.score(2.448, 0.080)
    code = sc.result_code(d["total"], 2.448, 0.080)
    parsed = sc.parse_code(code)
    assert parsed["valid"]
    assert parsed["total"] == pytest.approx(d["total"], abs=0.05)


def test_checksum_detecta_nota_inflada():
    d = sc.score(2.448, 0.080)
    code = sc.result_code(d["total"], 2.448, 0.080)
    tampered = code.replace(f"N{d['total']:.1f}", "N99.9")
    assert tampered != code
    assert not sc.parse_code(tampered)["valid"]


def test_sin_colisiones_de_nota_en_el_rango():
    seen = {}
    for t in range(0, 1001):
        c = sc.checksum(t / 10, 2.448, 0.080)
        assert c not in seen, f"colisión de checksum entre {seen.get(c)} y {t}"
        seen[c] = t


def test_plantilla_corre_y_puntua():
    """La plantilla de mi_estrategia.py debe simular sin reventar y dar una nota
    razonable (un MM naive bien ajustado ronda los 90)."""
    from mi_estrategia import MiEstrategia
    avg_pnl, avg_inv, rows = sc.run_metrics(MiEstrategia)
    assert len(rows) == 3
    d = sc.score(avg_pnl, avg_inv)
    assert d["total"] > 50, "la plantilla de partida debería aprobar con holgura"
