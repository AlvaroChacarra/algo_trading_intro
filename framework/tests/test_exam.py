"""Regresión del banco de preguntas, el muestreo por seed y el código de
resultado. Si esto pasa, generate_exam.py puede emitir variantes equilibradas y
verify_result.py valida los códigos que emite el examen."""

import collections
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(__file__)
EXAM = os.path.abspath(os.path.join(HERE, "..", "..", "15-final-exam"))
sys.path.insert(0, EXAM)

import question_bank as qb  # noqa: E402
import verify_result as vr  # noqa: E402


BLUEPRINT = os.path.abspath(os.path.join(HERE, "..", "..", "pedagogy",
                                         "assessment_blueprint.yml"))


def _load_blueprint():
    with open(BLUEPRINT, encoding="utf-8") as fh:
        return json.load(fh)


def _objective_index(blueprint):
    return {
        (entry["lesson"], objective["id"]): objective
        for entry in blueprint["lesson_blueprints"]
        for objective in entry["objectives"]
    }


def _course_block(lesson):
    if 1 <= lesson <= 6:
        return "FOUNDATIONS"
    if 7 <= lesson <= 10:
        return "ENGINE"
    if 11 <= lesson <= 14:
        return "STRATEGIES"
    if lesson == 15:
        return "ASSESSMENT"
    raise AssertionError(f"lección fuera del curso: {lesson}")


def test_canonical_es_40():
    assert len(qb.CANONICAL) == 40


def test_tuplas_bien_formadas():
    for q in qb.EXAM_POOL + qb.CHECKPOINT:
        assert len(q) == 6
        assert q[4] in ("A", "B", "C")
        assert q[1] and q[2] and q[3]  # tres opciones no vacías
        assert len(set(q[1:4])) == 3   # distractores inequívocos


def test_preguntas_y_metadatos_son_unicos_y_tienen_cobertura_total():
    all_stems = []
    all_ids = []
    expected_prefixes = {
        "CANONICAL": "L15-CAN-",
        "EXTRA": "L15-EXT-",
        "CHECKPOINT": "CK6-",
    }
    for bank_name, (questions, metadata) in qb.PUBLIC_BANKS.items():
        assert len(questions) == len(metadata) > 0
        assert tuple(m.item_id for m in metadata) == tuple(
            f"{expected_prefixes[bank_name]}{i:03d}"
            for i in range(1, len(questions) + 1)
        )
        for meta in metadata:
            assert len(meta.lessons) == len(meta.objectives) >= 1
            assert len(set(zip(meta.lessons, meta.objectives))) == len(meta.lessons)
            assert re.fullmatch(r"(?:L15-(?:CAN|EXT)|CK6)-\d{3}", meta.item_id)
        all_stems.extend(q[0] for q in questions)
        all_ids.extend(m.item_id for m in metadata)

    assert len(all_stems) == len(set(all_stems))
    assert len(all_ids) == len(set(all_ids))


def test_cada_metadata_enlaza_objetivos_evaluables_live_o_required():
    blueprint = _load_blueprint()
    objective_index = _objective_index(blueprint)
    allowed_routes = set(blueprint["allowed_routes"])
    distribution_types = {
        kind
        for lesson in blueprint["lesson_blueprints"]
        for kind in lesson["question_distribution"]
    }
    assert allowed_routes == {"LIVE", "REQUIRED"}

    for _, metadata in qb.PUBLIC_BANKS.values():
        for meta in metadata:
            assert meta.distribution_type in distribution_types
            assert meta.cognitive_level in {"understand", "apply", "analyze", "evaluate"}
            assert meta.difficulty in {"low", "medium", "hard"}
            for link in zip(meta.lessons, meta.objectives):
                objective = objective_index.get(link)
                assert objective is not None, f"objetivo inexistente: {meta.item_id} -> {link}"
                assert objective["assessed"] is True
                assert objective["route"] in allowed_routes
                assert objective["route"] != "OPTIONAL"


def test_canonical_cumple_distribucion_l15_y_ocho_integraciones_reales():
    blueprint = _load_blueprint()
    l15 = next(x for x in blueprint["lesson_blueprints"] if x["lesson"] == 15)
    actual = collections.Counter(m.distribution_type for m in qb.CANONICAL_METADATA)
    assert dict(actual) == l15["question_distribution"]

    integrations = [
        meta for meta in qb.CANONICAL_METADATA
        if meta.distribution_type == "integration"
    ]
    assert len(integrations) >= 8
    for meta in integrations:
        assert "l15-integrate-course" in meta.objectives
        source_lessons = {lesson for lesson in meta.lessons if lesson != 15}
        source_blocks = {_course_block(lesson) for lesson in source_lessons}
        assert len(source_lessons) >= 2
        assert len(source_blocks) >= 2
        assert meta.integration_rationale


def test_instancia_order_del_checkpoint_usa_firma_canonica():
    text = " ".join(question[0] for question in qb.CHECKPOINT)
    assert "Order('BTC', 'buy', 0.5, price=100)" in text
    assert "Order('BTC', 'buy', 100, 0.5)" not in text


def test_pool_cubre_los_targets():
    for pool, targets in [(qb.EXAM_POOL, qb.EXAM_TARGETS),
                          (qb.CHECKPOINT, qb.CHECKPOINT_TARGETS)]:
        c = collections.Counter(x[5] for x in pool)
        for topic, k in targets.items():
            assert c[topic] >= k, f"{topic}: {c[topic]} < {k}"


def test_banco_no_evalua_profundizaciones_optional():
    text = " ".join(
        str(field).lower()
        for question in qb.EXAM_POOL + qb.CHECKPOINT
        for field in question
    )
    forbidden = (
        "predicción dinámica de volumen",
        "media rolada",
        "factor de corrección",
        "matplotlib",
        "graficar la equity_curve",
        "visualizar la equity_curve",
    )
    assert not [marker for marker in forbidden if marker in text]


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
