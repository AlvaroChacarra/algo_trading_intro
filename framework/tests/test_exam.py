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
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EXAM = os.path.abspath(os.path.join(HERE, "..", "..", "15-final-exam"))
sys.path.insert(0, EXAM)

import question_bank as qb  # noqa: E402
import verify_result as vr  # noqa: E402


BLUEPRINT = os.path.abspath(os.path.join(HERE, "..", "..", "pedagogy",
                                         "assessment_blueprint.yml"))
CONTINUOUS_MANIFEST = os.path.join(
    ROOT, "pedagogy", "continuous_assessment_manifest.yml"
)


def _load_blueprint():
    with open(BLUEPRINT, encoding="utf-8") as fh:
        return json.load(fh)


def test_official_grading_weights_are_exact_and_sum_to_one_hundred():
    weights = _load_blueprint()["official_grading_weights_percent"]
    assert weights == {
        "attendance": 10,
        "participation": 20,
        "continuous_exams": 40,
        "final_exam": 30,
    }
    assert sum(weights.values()) == 100


def _load_lesson(number):
    path = os.path.join(ROOT, "pedagogy", "lessons", f"{number:02d}.yml")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _all_objective_semantics():
    result = {}
    for lesson_number in range(1, 16):
        lesson = _load_lesson(lesson_number)
        for objective in lesson["objectives"]:
            result[(lesson_number, objective["id"])] = {
                "concept_ids": set(objective.get("concepts", ())),
                "api_ids": set(objective.get("apis", ())),
                "notation_ids": set(objective.get("notation", ())),
                "route": objective["route"],
            }
    return result


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


def test_distribuciones_del_blueprint_suman_diez_y_cuarenta():
    blueprint = _load_blueprint()
    for lesson in blueprint["lesson_blueprints"]:
        expected = 40 if lesson["lesson"] == 15 else 10
        assert sum(lesson["question_distribution"].values()) == expected


def test_blueprint_cubre_exactamente_todos_los_objetivos_evaluables():
    blueprint = _load_blueprint()
    declared = {
        (entry["lesson"], objective["id"])
        for entry in blueprint["lesson_blueprints"]
        for objective in entry["objectives"]
        if objective["assessed"] is True
    }
    expected = {
        (lesson, objective["id"])
        for lesson in range(1, 16)
        for objective in _load_lesson(lesson)["objectives"]
        if objective["route"] in blueprint["allowed_routes"]
    }
    assert declared == expected
    trace_pairs = [
        (item["lesson"], item["objective"]) for item in blueprint["items"]
    ]
    assert len(trace_pairs) == len(set(trace_pairs))
    assert set(trace_pairs) == expected


def test_assessment_publico_no_se_presenta_como_banco_oficial():
    blueprint = _load_blueprint()
    assert blueprint["public_artifact_status"] == "PRACTICE_ONLY"
    assert blueprint["official_assessment_status"] == "BLOCKED_UNTIL_PRIVATE_BANK"

    with open(CONTINUOUS_MANIFEST, encoding="utf-8") as fh:
        continuous = json.load(fh)
    assert continuous["status"] == "BLOCKED_UNTIL_PRIVATE_SOURCE"
    assert continuous["confidentiality"]["fail_closed"] is True
    assert continuous["contract"] == {
        "questions_per_lesson": 10,
        "options": ["A", "B", "C", "D"],
        "minutes_per_lesson": 10,
        "combined_assessments_allowed": True,
        "optional_content_allowed": False,
    }
    assert [entry["lesson"] for entry in continuous["coverage"]] == list(range(1, 15))
    assert {entry["item_count"] for entry in continuous["coverage"]} == {10}


def test_canonical_cubre_l1_l14_y_todos_los_requisitos_semanticos_l15():
    assert {
        lesson
        for meta in qb.CANONICAL_METADATA
        for lesson in meta.lessons
        if lesson != 15
    } == set(range(1, 15))

    required = _load_lesson(15)["requires"]
    for field in ("concept_ids", "api_ids", "notation_ids"):
        actual = {
            value
            for meta in qb.CANONICAL_METADATA
            for value in getattr(meta, field)
        }
        source_field = {
            "concept_ids": "concepts",
            "api_ids": "apis",
            "notation_ids": "notation",
        }[field]
        assert set(required[source_field]) <= actual


def test_semantica_canonical_pertenece_a_sus_objetivos_y_no_a_optional():
    semantics = _all_objective_semantics()
    optional = {"concept_ids": set(), "api_ids": set(), "notation_ids": set()}
    for values in semantics.values():
        if values["route"] == "OPTIONAL":
            for field in optional:
                optional[field].update(values[field])

    for meta in qb.CANONICAL_METADATA:
        assert meta.concept_ids or meta.api_ids or meta.notation_ids
        linked = [semantics[link] for link in zip(meta.lessons, meta.objectives)]
        for field in optional:
            allowed = set().union(*(values[field] for values in linked))
            declared = set(getattr(meta, field))
            assert declared <= allowed, f"{meta.item_id}: {field} fuera de sus objetivos"
            assert declared.isdisjoint(optional[field]), (
                f"{meta.item_id}: {field} depende de OPTIONAL"
            )


def test_tipos_code_reading_y_debugging_tienen_evidencia_en_el_stem():
    for question, meta in zip(qb.CANONICAL, qb.CANONICAL_METADATA):
        stem = question[0]
        if meta.distribution_type == "code_reading":
            assert "`" in stem or "\n" in stem, meta.item_id
        if meta.distribution_type == "debugging":
            assert re.search(r"\b(?:bug|error|falla|incorrect[oa])\b", stem, re.I), meta.item_id


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


def _code(seed, right, wrong, blank, exid="L15P"):
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


def test_codigo_con_id_desconocido_falla_aunque_checksum_cuadre():
    code = _code(0, 34, 3, 3, exid="FAKE")
    with pytest.raises(ValueError, match="desconocido"):
        vr.verify(code)


@pytest.mark.parametrize("code", [
    "AT26-L15P-S0-R40-W0-B0-N10.01-00",
    "AT26-L15P-S-1-R40-W0-B0-N10.00-00",
    "AT26-L15P-S0-R-1-W0-B41-N0.00-00",
])
def test_codigo_rechaza_rangos_o_enteros_negativos(code):
    with pytest.raises(ValueError):
        vr.verify(code)


def test_formato_invalido_lanza():
    with pytest.raises(ValueError):
        vr.parse("esto-no-es-un-codigo")
