"""Regresión del banco de preguntas, el muestreo por seed y el código de
resultado. Si esto pasa, generate_exam.py puede emitir variantes equilibradas y
verify_result.py valida los códigos que emite el examen."""

import collections
import os
import sys

import pytest

HERE = os.path.dirname(__file__)
EXAM = os.path.abspath(os.path.join(HERE, "..", "..", "15-final-exam"))
sys.path.insert(0, EXAM)

import question_bank as qb  # noqa: E402
import verify_result as vr  # noqa: E402


def test_canonical_es_40():
    assert len(qb.CANONICAL) == 40


def test_tuplas_bien_formadas():
    for q in qb.EXAM_POOL + qb.CHECKPOINT:
        assert len(q) == 6
        assert q[4] in ("A", "B", "C")
        assert q[1] and q[2] and q[3]  # tres opciones no vacías


def test_pool_cubre_los_targets():
    for pool, targets in [(qb.EXAM_POOL, qb.EXAM_TARGETS),
                          (qb.CHECKPOINT, qb.CHECKPOINT_TARGETS)]:
        c = collections.Counter(x[5] for x in pool)
        for topic, k in targets.items():
            assert c[topic] >= k, f"{topic}: {c[topic]} < {k}"


def test_muestreo_equilibrado_y_reproducible():
    a = qb.sample_balanced(qb.EXAM_POOL, qb.EXAM_TARGETS, 7)
    b = qb.sample_balanced(qb.EXAM_POOL, qb.EXAM_TARGETS, 7)
    assert a == b                      # misma seed -> mismo examen
    assert len(a) == sum(qb.EXAM_TARGETS.values()) == 40
    c = collections.Counter(x[5] for x in a)
    assert dict(c) == qb.EXAM_TARGETS  # reparto exacto por tema
    # sin repetición
    assert len({x[0] for x in a}) == len(a)


def test_seeds_distintas_dan_examenes_distintos():
    a = qb.sample_balanced(qb.EXAM_POOL, qb.EXAM_TARGETS, 1)
    b = qb.sample_balanced(qb.EXAM_POOL, qb.EXAM_TARGETS, 2)
    assert [x[0] for x in a] != [x[0] for x in b]


def _code(seed, right, wrong, blank, exid="L15"):
    total = right + wrong + blank
    score = right - 0.5 * wrong
    nota = max(0.0, score / total * 10) if total else 0.0
    chk = vr._checksum(seed, right, wrong, blank, total)
    return f"AT26-{exid}-S{seed}-R{right}-W{wrong}-B{blank}-N{nota:.2f}-{chk}"


def test_codigo_valido_pasa():
    ok, _ = vr.verify(_code(0, 34, 3, 3))
    assert ok


def test_codigo_con_nota_inflada_falla():
    bad = _code(0, 1, 0, 39).replace("N0.25", "N9.99")
    ok, report = vr.verify(bad)
    assert not ok and "nota" in report.lower()


def test_codigo_con_checksum_alterado_falla():
    good = _code(0, 20, 10, 10)
    bad = good[:-2] + ("00" if good[-2:] != "00" else "11")
    ok, report = vr.verify(bad)
    assert not ok and "checksum" in report.lower()


def test_formato_invalido_lanza():
    with pytest.raises(ValueError):
        vr.parse("esto-no-es-un-codigo")
