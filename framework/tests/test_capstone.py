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
import leaderboard  # noqa: E402


def test_semillas_y_referencias_publicas():
    assert sc.SEEDS == (2026, 7, 314) and sc.STEPS == 500
    assert sc.ARRIVAL_INTENSITY == 630.0
    assert sc.PNL_REF > 0 and sc.INV_CAP > 0 and sc.RA_REF > 0


def test_referencias_del_baremo_corresponden_al_simulador_calibrado():
    from exchange.strategies import MarketMaker

    pnl, inv, rows = sc.run_metrics(
        lambda: MarketMaker("BTC", half_spread=1.0, inventory_skew=2.0)
    )
    assert len(rows) == len(sc.SEEDS)
    assert pnl == pytest.approx(2.483, abs=0.001)
    assert inv == pytest.approx(0.090, abs=0.001)
    assert sc.score(pnl, inv)["total"] > 85


def test_baremo_acotado_0_100():
    for pnl, inv in [(-5, 5), (0, 0), (2.5, 0), (100, 0), (2.5, 1.0)]:
        d = sc.score(pnl, inv)
        assert 0 <= d["total"] <= 100


@pytest.mark.parametrize("pnl,inv", [(float("inf"), 0.1), (float("nan"), 0.1), (1.0, -0.1)])
def test_baremo_rechaza_metricas_no_finitas_o_imposibles(pnl, inv):
    with pytest.raises(ValueError):
        sc.score(pnl, inv)


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


def test_errores_humanos_lo_presentan_como_puntuacion_formativa():
    """El wire code conserva ``N`` por compatibilidad, no su semántica de nota."""
    with pytest.raises(ValueError, match="puntuación"):
        sc.result_code(float("nan"), 0.0, 0.0)
    with pytest.raises(ValueError, match="puntuación"):
        sc.parse_code("codigo-invalido")


def test_codigo_roundtrip_admite_pnl_negativo():
    d = sc.score(-1.250, 0.080)
    code = sc.result_code(d["total"], -1.250, 0.080)
    parsed = sc.parse_code(code)
    assert parsed["valid"]
    assert parsed["pnl"] == pytest.approx(-1.250)


def test_checksum_autentica_signo_y_parseo_recalcula_nota():
    d = sc.score(-1.250, 0.080)
    code = sc.result_code(d["total"], -1.250, 0.080)
    sign_flip = code.replace("P-1.250", "P1.250")
    assert sign_flip != code
    assert not sc.parse_code(sign_flip)["valid"]

    positive = sc.score(1.250, 0.080)
    valid = sc.result_code(positive["total"], 1.250, 0.080)
    inflated = valid.replace(f"N{positive['total']:.1f}", "N99.9")
    assert not sc.parse_code(inflated)["score_valid"]


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


def test_plantilla_no_aprueba_sin_trabajo_del_alumno():
    """El starter intacto no puede acreditar trabajo autónomo."""
    from mi_estrategia import MiEstrategia
    with pytest.raises(NotImplementedError, match="implementa reservation_price"):
        sc.run_metrics(MiEstrategia)


def test_una_reserva_que_ignora_inventario_no_es_elegible():
    from exchange.strategies import MarketMaker

    class Trivial(MarketMaker):
        def reservation_price(self, mid):
            return mid

    with pytest.raises(sc.StrategyEligibilityError, match="inventario"):
        sc.validate_strategy(lambda: Trivial("BTC", half_spread=1.0))


def test_market_maker_con_feedback_direccional_es_elegible():
    from exchange.strategies import MarketMaker
    probe = sc.validate_strategy(
        lambda: MarketMaker("BTC", half_spread=1.0, inventory_skew=2.0)
    )
    assert probe["short_center"] > probe["flat_center"] > probe["long_center"]


def test_leaderboard_no_asigna_rango_a_codigos_publicos_sin_reejecucion(tmp_path):
    valid_score = sc.score(1.0, 0.1)
    valid = sc.result_code(valid_score["total"], 1.0, 0.1)
    invalid = valid.replace(f"N{valid_score['total']:.1f}", "N99.9")
    submissions = tmp_path / "entregas.txt"
    submissions.write_text(f"Ada {valid}\nMallory {invalid}\n", encoding="utf-8")

    rows = leaderboard.parse_file(str(submissions))
    ranked, rejected = leaderboard.partition_rows(rows)
    assert ranked == []
    assert [row["name"] for row in rejected] == ["Ada", "Mallory"]


def test_codigo_fabricable_consistente_sigue_siendo_autoinforme_no_verificado(tmp_path):
    fabricated = "AT26-CAP-N100.0-P1000.000-I0.000-7366"
    assert sc.parse_code(fabricated)["valid"]
    submissions = tmp_path / "entregas.txt"
    submissions.write_text(f"Mallory {fabricated}\n", encoding="utf-8")
    ranked, unranked = leaderboard.partition_rows(leaderboard.parse_file(str(submissions)))
    assert ranked == []
    assert unranked[0]["verified"] is False
