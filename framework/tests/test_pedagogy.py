import json
from pathlib import Path
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(ROOT))
from pedagogy_check import validate_repository  # noqa: E402


def _copy_contract(tmp_path: Path) -> Path:
    target = tmp_path / "pedagogy"
    shutil.copytree(ROOT / "pedagogy", target)
    return target


def _mutate(path: Path, fn) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    fn(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _checks(issues):
    return {issue.check for issue in issues}


def _rebind_package_check(
    tmp_path: Path,
    pedagogy: Path,
    lesson: int,
    class_name: str,
    member: str,
    source: str,
) -> Path:
    target = tmp_path / Path(source).name
    shutil.copy2(ROOT / source, target)

    def change(data):
        check = next(
            item for item in data["package_checks"]
            if item["class"] == class_name and member in item["members"]
        )
        check["path"] = str(target)

    _mutate(pedagogy / f"lessons/{lesson:02d}.yml", change)
    return target


def _rebind_symbol_check(
    tmp_path: Path,
    pedagogy: Path,
    lesson: int,
    symbol: str,
    source: str,
) -> Path:
    target = tmp_path / f"symbol-{Path(source).name}"
    shutil.copy2(ROOT / source, target)

    def change(data):
        check = next(
            item for item in data["symbol_checks"] if item["symbol"] == symbol
        )
        check["path"] = str(target)

    _mutate(pedagogy / f"lessons/{lesson:02d}.yml", change)
    return target


def _rebind_module_symbol_checks(
    tmp_path: Path,
    pedagogy: Path,
    lesson: int,
    source: str,
) -> Path:
    target = tmp_path / f"module-{Path(source).name}"
    shutil.copy2(ROOT / source, target)

    def change(data):
        for check in data["symbol_checks"]:
            if check["path"] == source:
                check["path"] = str(target)

    _mutate(pedagogy / f"lessons/{lesson:02d}.yml", change)
    return target


def test_t8_current_full_course_contract_passes():
    assert validate_repository(ROOT) == []


def test_equity_curve_core_and_optional_visualization_are_not_conflated():
    l9 = json.loads((ROOT / "pedagogy/lessons/09.yml").read_text(encoding="utf-8"))
    l10 = json.loads((ROOT / "pedagogy/lessons/10.yml").read_text(encoding="utf-8"))
    l11 = json.loads((ROOT / "pedagogy/lessons/11.yml").read_text(encoding="utf-8"))
    routes = json.loads(
        (ROOT / "pedagogy/exercise_routes.yml").read_text(encoding="utf-8")
    )["lessons"]

    introduced = {
        item["id"]: item["route"] for item in l9["introduces"]["concepts"]
    }
    assert introduced["metrics.equity_curve"] == "REQUIRED"
    assert l10["introduction_routes"]["apis"]["backtest_result.equity_curve"] == "LIVE"
    assert l11["requirement_routes"]["apis"]["backtest_result.equity_curve"] == "OPTIONAL"
    optional_titles = {
        item["title"] for item in routes["11"]["aux"]
        if item["route"] == "OPTIONAL"
    }
    assert "A6. Graficar la curva de equity" in optional_titles


def test_t1_future_dependency_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "lessons/01.yml",
        lambda data: data["requires"]["concepts"].append("matching.atomicity"),
    )
    assert "PED-CHECK-01" in _checks(validate_repository(ROOT, pedagogy))


def test_t2_silent_method_to_property_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        next(item for item in data["api_surface"] if item["id"] == "orderbook.mid")["kind"] = "method"

    _mutate(pedagogy / "lessons/07.yml", change)
    assert "PED-CHECK-02" in _checks(validate_repository(ROOT, pedagogy))


def test_missing_distant_recall_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(pedagogy / "lessons/10.yml", lambda data: data.update(recalls=[]))
    assert "PED-CHECK-04" in _checks(validate_repository(ROOT, pedagogy))


def test_t3_required_cannot_depend_on_optional(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def make_optional(data):
        concept = next(
            item for item in data["introduces"]["concepts"]
            if item["id"] == "python.control_flow"
        )
        concept["route"] = "OPTIONAL"

    _mutate(pedagogy / "lessons/01.yml", make_optional)
    assert "PED-CHECK-06" in _checks(validate_repository(ROOT, pedagogy))


def test_t3_required_api_cannot_depend_on_optional(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def make_optional(data):
        data["introduction_routes"]["apis"]["matching.process"] = "OPTIONAL"

    _mutate(pedagogy / "lessons/08.yml", make_optional)
    assert "PED-CHECK-06" in _checks(validate_repository(ROOT, pedagogy))


def test_t3_required_notation_cannot_depend_on_optional(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def make_optional(data):
        data["introduction_routes"]["notation"]["notation.vwap"] = "OPTIONAL"

    _mutate(pedagogy / "lessons/12.yml", make_optional)
    assert "PED-CHECK-06" in _checks(validate_repository(ROOT, pedagogy))


@pytest.mark.parametrize(
    ("lesson", "concept"),
    [
        (1, "python.fstring"),
        (1, "python.dict_get"),
        (2, "python.generator_expression"),
    ],
)
def test_required_python_idiom_cannot_leak_from_optional(
    tmp_path, lesson, concept,
):
    pedagogy = _copy_contract(tmp_path)

    def make_optional(data):
        introduction = next(
            item for item in data["introduces"]["concepts"]
            if item["id"] == concept
        )
        introduction["route"] = "OPTIONAL"

    _mutate(pedagogy / f"lessons/{lesson:02d}.yml", make_optional)
    assert "PED-CHECK-06" in _checks(validate_repository(ROOT, pedagogy))


def test_t4_nonexistent_bridge_lesson_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "lessons/09.yml",
        lambda data: data["bridge"].update(target_lesson=99),
    )
    assert "PED-CHECK-03" in _checks(validate_repository(ROOT, pedagogy))


def test_causal_bridge_cannot_skip_the_next_lesson(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "lessons/09.yml",
        lambda data: data["bridge"].update(target_lesson=11),
    )
    assert "PED-CHECK-03" in _checks(validate_repository(ROOT, pedagogy))


def test_t5_assessment_on_optional_objective_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def make_optional(data):
        objective = next(
            item for item in data["objectives"]
            if item["id"] == "l12-run-vwap-strategy"
        )
        objective["route"] = "OPTIONAL"

    _mutate(pedagogy / "lessons/12.yml", make_optional)
    assert "PED-CHECK-06" in _checks(validate_repository(ROOT, pedagogy))


def test_assessment_blueprint_cannot_omit_a_live_or_required_objective(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def omit_required(data):
        lesson = next(
            item for item in data["lesson_blueprints"] if item["lesson"] == 9
        )
        lesson["objectives"] = [
            objective for objective in lesson["objectives"]
            if objective["id"] != "l09-track-equity-over-time"
        ]

    _mutate(pedagogy / "assessment_blueprint.yml", omit_required)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-07"
        and issue.lesson == 9
        and "exactly cover every LIVE/REQUIRED objective" in issue.message
        for issue in issues
    )


def test_assessment_trace_cannot_omit_an_assessed_objective(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "assessment_blueprint.yml",
        lambda data: data.update(items=[
            item for item in data["items"] if item["id"] != "TRACE-L13-04"
        ]),
    )
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-07"
        and "trace items must cover every assessed objective exactly once" in issue.message
        for issue in issues
    )


def test_t6_removing_used_introduction_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def remove_atomicity(data):
        data["introduces"]["concepts"] = [
            item for item in data["introduces"]["concepts"]
            if item["id"] != "matching.atomicity"
        ]

    _mutate(pedagogy / "lessons/08.yml", remove_atomicity)
    assert "PED-CHECK-01" in _checks(validate_repository(ROOT, pedagogy))


def test_t7_valid_recall_configuration_passes(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def add_recall(data):
        data["recalls"].append({
            "concept": "functional.order_book",
            "introduced_in": 2,
            "mapping": {
                "before": "un book compartido alimenta funciones",
                "now": "un módulo reutiliza el mismo estado funcional",
            },
        })

    _mutate(pedagogy / "lessons/03.yml", add_recall)
    assert validate_repository(ROOT, pedagogy) == []


def test_constructor_surface_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        surface = next(
            item for item in data["api_surface"]
            if item["id"] == "order.constructor"
        )
        surface["signature"] = surface["signature"].replace(
            "size: float", "quantity: float"
        )

    _mutate(pedagogy / "lessons/04.yml", change)
    assert "PED-CHECK-02" in _checks(validate_repository(ROOT, pedagogy))


def test_pedagogical_constructor_transition_needs_source_signature(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["api_transitions"][0].pop("from_signature")

    _mutate(pedagogy / "lessons/04.yml", change)
    assert "PED-CHECK-02" in _checks(validate_repository(ROOT, pedagogy))


def test_pedagogical_constructor_transition_rejects_target_signature_drift(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["api_transitions"][0]["to_signature"] = "Order(symbol, side) -> Order"

    _mutate(pedagogy / "lessons/04.yml", change)
    assert "PED-CHECK-02" in _checks(validate_repository(ROOT, pedagogy))


def test_used_later_projection_drift_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "lessons/10.yml",
        lambda data: data["used_later"]["apis"].remove("strategy.on_fill"),
    )
    assert "PED-CHECK-03" in _checks(validate_repository(ROOT, pedagogy))


def test_nonexistent_lesson_reference_in_declared_source_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = tmp_path / "synthetic-teaching-source.md"
    source.write_text("El puente estable apunta a L99.\n", encoding="utf-8")

    def use_fixture(data):
        data["text_audit"]["strict_paths"] = [str(source)]
        data["text_audit"]["forbidden_phrases"] = []
        data["text_audit"]["forbidden_patterns"] = []

    _mutate(pedagogy / "course_graph.yml", use_fixture)
    assert "PED-CHECK-03" in _checks(validate_repository(ROOT, pedagogy))


def test_stale_forty_minute_course_plan_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = tmp_path / "stale-plan.md"
    source.write_text("15 clases de 40 min.\n", encoding="utf-8")

    def use_fixture(data):
        data["text_audit"]["strict_paths"] = [str(source)]
        data["text_audit"]["forbidden_phrases"] = []
        data["text_audit"]["reference_patterns"] = []

    _mutate(pedagogy / "course_graph.yml", use_fixture)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-03"
        and "approximately 50-minute duration" in issue.message
        for issue in issues
    )


def test_unclassified_scene_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["routes"]["LIVE"].remove("l08-simulator")

    _mutate(pedagogy / "lessons/08.yml", change)
    assert "PED-CHECK-05" in _checks(validate_repository(ROOT, pedagogy))


def test_scene_route_list_cannot_keep_the_right_ids_under_the_wrong_route(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def swap_route(data):
        data["routes"]["REQUIRED"].remove("l08-order-policies")
        data["routes"]["LIVE"].append("l08-order-policies")

    _mutate(pedagogy / "lessons/08.yml", swap_route)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-05"
        and "routes.LIVE does not match scene.route" in issue.message
        for issue in issues
    )


def test_effective_stage_route_must_match_route_inventory(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change_stage(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-plan-validate-commit")
        stage = next(item for item in scene["stages"] if item["id"] == "remainder")
        stage["route"] = "LIVE"

    _mutate(pedagogy / "lessons/08.yml", change_stage)
    assert "PED-CHECK-05" in _checks(validate_repository(ROOT, pedagogy))


def test_route_override_requires_its_own_positive_duration(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def remove_duration(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-plan-validate-commit")
        stage = next(item for item in scene["stages"] if item["id"] == "remainder")
        stage.pop("duration_minutes")

    _mutate(pedagogy / "lessons/08.yml", remove_duration)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "route override l08-plan-validate-commit/remainder" in issue.message
        for issue in issues
    )


def test_route_override_duration_must_equal_autonomous_load_mirror(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def inflate_component(data):
        component = next(
            item for item in data["load"]["autonomous_components"]["documents"]
            if item["id"] == "l08-plan-validate-commit/remainder"
        )
        component["minutes"] = 30
        data["load"]["required_autonomous_minutes"] += 29

    _mutate(pedagogy / "lessons/08.yml", inflate_component)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "must use canonical state duration 1" in issue.message
        for issue in issues
    )


@pytest.mark.parametrize("bad", [0, -1, 1.0, "1", True])
def test_route_override_duration_rejects_non_positive_or_non_integer_values(tmp_path, bad):
    pedagogy = _copy_contract(tmp_path)

    def invalidate(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-plan-validate-commit")
        stage = next(item for item in scene["stages"] if item["id"] == "remainder")
        stage["duration_minutes"] = bad

    _mutate(pedagogy / "lessons/08.yml", invalidate)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08" and "positive integer duration_minutes" in issue.message
        for issue in issues
    )


def test_inherited_route_stage_cannot_declare_a_second_duration_budget(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def add_duplicate_budget(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-plan-validate-commit")
        stage = next(item for item in scene["stages"] if item["id"] == "signature")
        stage["duration_minutes"] = 1

    _mutate(pedagogy / "lessons/08.yml", add_duplicate_budget)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08" and "inherited-route stage" in issue.message
        for issue in issues
    )


def test_current_route_override_duration_inventory_is_exact():
    identities = []
    for lesson in range(1, 15):
        data = json.loads((ROOT / f"pedagogy/lessons/{lesson:02d}.yml").read_text(encoding="utf-8"))
        for scene in data["scenes"]:
            for stage in scene.get("stages", []):
                if stage.get("route", scene["route"]) != scene["route"]:
                    identities.append((lesson, f"{scene['id']}/{stage['id']}",
                                       stage["route"], stage["duration_minutes"]))
    assert len(identities) == 14
    assert sum(item[3] for item in identities if item[2] == "REQUIRED") == 13
    assert sum(item[3] for item in identities if item[2] == "OPTIONAL") == 1


def test_live_budget_outside_policy_fails_even_if_declared_total_is_recomputed(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def inflate(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-simulator")
        scene["duration_minutes"] += 3
        data["load"]["live_presentation_minutes"] += 3

    _mutate(pedagogy / "lessons/08.yml", inflate)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08" and "expected 18–22" in issue.message
        for issue in issues
    )


def test_market_from_csv_classmethod_signature_is_canonical(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_package_check(
        tmp_path, pedagogy, 9, "Market", "from_csv",
        "09-market-simulation-loop/exercises/exchange/market.py",
    )
    text = source.read_text(encoding="utf-8")
    source.write_text(
        text.replace("    @classmethod\n    def from_csv", "    def from_csv", 1),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_duplicate_scene_ids_cannot_match_a_duplicated_route_inventory(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def duplicate_scene(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-simulator")
        data["scenes"].append(dict(scene))
        data["routes"]["LIVE"].append("l08-simulator")

    _mutate(pedagogy / "lessons/08.yml", duplicate_scene)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-05" and "scene id" in issue.message
        for issue in issues
    )


def test_stage_ids_must_be_nonempty_even_without_a_route_override(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def remove_stage_id(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-simulator")
        scene["stages"][0].pop("id")

    _mutate(pedagogy / "lessons/08.yml", remove_stage_id)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-05" and "stage id" in issue.message
        for issue in issues
    )


def test_non_string_effective_stage_route_is_reported_without_crashing(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def invalidate_stage_route(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-plan-validate-commit")
        stage = next(item for item in scene["stages"] if item["id"] == "remainder")
        stage["route"] = []
        data["routes"]["REQUIRED"].remove("l08-plan-validate-commit/remainder")

    _mutate(pedagogy / "lessons/08.yml", invalidate_stage_route)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-05" and "invalid effective route" in issue.message
        for issue in issues
    )


def test_autonomous_scene_cannot_hide_a_different_effective_stage_route(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def mix_route(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l10-first-strategy")
        scene["stages"][0]["route"] = "OPTIONAL"
        data["routes"]["OPTIONAL"].append("l10-first-strategy/main")

    _mutate(pedagogy / "lessons/10.yml", mix_route)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "mixes effective stage routes" in issue.message
        for issue in issues
    )


def test_unclassified_exercise_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["lessons"]["8"]["build"][0].pop("route")

    _mutate(pedagogy / "exercise_routes.yml", change)
    assert "PED-CHECK-05" in _checks(validate_repository(ROOT, pedagogy))


def test_exercise_route_lesson_keys_must_be_canonical(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def duplicate_numeric_key(data):
        data["lessons"]["01"] = dict(data["lessons"]["1"])

    _mutate(pedagogy / "exercise_routes.yml", duplicate_numeric_key)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-05" and "not canonical" in issue.message
        for issue in issues
    )


def test_exercise_routes_for_a_missing_lesson_report_an_issue(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def add_missing_lesson(data):
        data["lessons"]["99"] = dict(data["lessons"]["1"])

    _mutate(pedagogy / "exercise_routes.yml", add_missing_lesson)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-03"
        and issue.lesson == 99
        and "exercise routes" in issue.message
        for issue in issues
    )


def test_exercise_load_is_mandatory(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["lessons"]["14"]["aux"][0]["minutes"] = 0

    _mutate(pedagogy / "exercise_routes.yml", change)
    assert "PED-CHECK-08" in _checks(validate_repository(ROOT, pedagogy))


def test_live_exercise_overload_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def overload(data):
        data["lessons"]["8"]["build"][3]["route"] = "LIVE"

    _mutate(pedagogy / "exercise_routes.yml", overload)
    assert "PED-CHECK-08" in _checks(validate_repository(ROOT, pedagogy))


def test_missing_exercise_minutes_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "exercise_routes.yml",
        lambda data: data["lessons"]["1"]["build"][0].pop("minutes"),
    )
    assert "PED-CHECK-08" in _checks(validate_repository(ROOT, pedagogy))


def test_required_exercise_load_must_equal_manifest(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["load"]["required_autonomous_minutes"] += 1

    _mutate(pedagogy / "lessons/10.yml", change)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "REQUIRED autonomous total" in issue.message
        for issue in issues
    )


def test_required_quiz_cannot_disappear_from_load_accounting(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def hide_quiz(data):
        data["load"]["autonomous_components"]["quizzes"] = []
        data["load"]["required_autonomous_minutes"] -= 8

    _mutate(pedagogy / "lessons/10.yml", hide_quiz)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "ignores REQUIRED/OPTIONAL scene states" in issue.message
        and "l10-quiz" in issue.message
        for issue in issues
    )


def test_invalid_component_minutes_report_an_issue_instead_of_crashing(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def invalidate_minutes(data):
        data["load"]["autonomous_components"]["quizzes"][0]["minutes"] = "8"

    _mutate(pedagogy / "lessons/10.yml", invalidate_minutes)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "needs positive integer minutes" in issue.message
        for issue in issues
    )


def test_boolean_minutes_are_not_contract_integers(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def use_boolean_minutes(data):
        data["load"]["autonomous_components"]["quizzes"][0]["minutes"] = True

    _mutate(pedagogy / "lessons/10.yml", use_boolean_minutes)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08" and "positive integer minutes" in issue.message
        for issue in issues
    )


def test_non_string_overlap_id_is_reported_without_crashing(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def invalidate_overlap(data):
        for field in ("documents", "projects"):
            data["load"]["autonomous_components"][field][0]["overlap_id"] = []

    _mutate(pedagogy / "lessons/14.yml", invalidate_overlap)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08" and "invalid overlap_id" in issue.message
        for issue in issues
    )


def test_overlap_cannot_collapse_two_exercises_of_the_same_kind(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def overlap_exercises(data):
        optional = [
            item for item in data["lessons"]["14"]["aux"]
            if item["route"] == "OPTIONAL"
        ]
        for item in optional:
            item["overlap_id"] = "fake-shared-work"

    def add_project(data):
        data["load"]["autonomous_components"]["projects"].append({
            "id": "fake-shared-project",
            "route": "OPTIONAL",
            "minutes": 5,
            "overlap_id": "fake-shared-work",
        })
        data["load"]["optional_minutes"] = 5

    _mutate(pedagogy / "exercise_routes.yml", overlap_exercises)
    _mutate(pedagogy / "lessons/14.yml", add_project)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "one component per different kind" in issue.message
        for issue in issues
    )


def test_overlap_id_cannot_span_required_and_optional_routes(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def reuse_required_overlap(data):
        optional = next(
            item for item in data["lessons"]["14"]["aux"]
            if item["route"] == "OPTIONAL"
        )
        optional["overlap_id"] = "l14-capstone-project"

    _mutate(pedagogy / "exercise_routes.yml", reuse_required_overlap)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "on one route" in issue.message
        for issue in issues
    )


def test_live_scene_minutes_must_equal_the_declared_presentation_load(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def inflate_scene(data):
        scene = next(item for item in data["scenes"] if item["id"] == "l08-simulator")
        scene["duration_minutes"] = 200

    _mutate(pedagogy / "lessons/08.yml", inflate_scene)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08" and "LIVE scene durations total" in issue.message
        for issue in issues
    )


def test_project_scene_overlap_cannot_be_broken_silently(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def break_overlap(data):
        data["load"]["autonomous_components"]["projects"][0].pop("overlap_id")

    _mutate(pedagogy / "lessons/14.yml", break_overlap)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "overlap_id 'l14-capstone-project'" in issue.message
        for issue in issues
    )


def test_optional_exercise_load_must_equal_manifest(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["load"]["optional_minutes"] += 1

    _mutate(pedagogy / "lessons/12.yml", change)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-08"
        and "OPTIONAL autonomous total" in issue.message
        for issue in issues
    )


def test_live_objective_cannot_use_required_only_api(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        objective = next(
            item for item in data["objectives"]
            if item["id"] == "l13-inspect-pnl-path"
        )
        objective["route"] = "LIVE"

    _mutate(pedagogy / "lessons/13.yml", change)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-06"
        and "LIVE objective l13-inspect-pnl-path" in issue.message
        and "REQUIRED-only api sim_result.pnl" in issue.message
        for issue in issues
    )


def test_double_exercise_classification_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def duplicate(data):
        data["lessons"]["7"]["aux"].append(
            dict(data["lessons"]["7"]["build"][0])
        )

    _mutate(pedagogy / "exercise_routes.yml", duplicate)
    assert "PED-CHECK-05" in _checks(validate_repository(ROOT, pedagogy))


def test_l8_starter_default_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_package_check(
        tmp_path, pedagogy, 8, "MatchingEngine", "process",
        "08-order-types-matching/exercises/exchange/matching.py",
    )
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "timestamp: int | None = None", "timestamp: int | None = 0"
        ),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


@pytest.mark.parametrize(
    ("symbol", "old", "new"),
    [
        ("make_order", "def make_order(symbol, side, price, size):", "def make_order(symbol, side, price, quantity):"),
        ("add_order", "def add_order(book, order):", "def add_order(order, book):"),
        ("cancel_order", "def cancel_order(book, order_id):", "def cancel_order(book, id_to_cancel):"),
        ("mid", "def mid(book):", "def mid(book, fallback=None):"),
    ],
)
def test_l2_real_function_signature_mutations_are_detected(
    tmp_path, symbol, old, new,
):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 2, symbol,
        "02-python-ii-functional-book/exercises/order_book.py",
    )
    text = source.read_text(encoding="utf-8")
    assert old in text
    source.write_text(text.replace(old, new, 1), encoding="utf-8")
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l2_async_function_mutation_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 2, "mid",
        "02-python-ii-functional-book/exercises/order_book.py",
    )
    text = source.read_text(encoding="utf-8")
    source.write_text(text.replace("def mid(book):", "async def mid(book):", 1), encoding="utf-8")
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l2_late_redefinition_controls_the_checked_runtime_binding(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 2, "mid",
        "02-python-ii-functional-book/exercises/order_book.py",
    )
    source.write_text(
        source.read_text(encoding="utf-8") + "\n\ndef mid(one):\n    return one\n",
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l6_async_method_mutation_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_package_check(
        tmp_path, pedagogy, 6, "Strategy", "decide",
        "06-oop-iii-inheritance/exercises/strategies_toy.py",
    )
    text = source.read_text(encoding="utf-8")
    source.write_text(
        text.replace("    def decide(self, imbalance: float)", "    async def decide(self, imbalance: float)", 1),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l6_binding_enforces_abc_and_abstractmethod(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_package_check(
        tmp_path, pedagogy, 6, "Strategy", "decide",
        "06-oop-iii-inheritance/exercises/strategies_toy.py",
    )
    text = source.read_text(encoding="utf-8")
    text = text.replace("class Strategy(ABC):", "class Strategy:", 1)
    text = text.replace("    @abstractmethod\n", "", 1)
    source.write_text(text, encoding="utf-8")
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_positional_only_function_cannot_masquerade_as_canonical(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 2, "mid",
        "02-python-ii-functional-book/exercises/order_book.py",
    )
    text = source.read_text(encoding="utf-8")
    source.write_text(text.replace("def mid(book):", "def mid(book, /):", 1), encoding="utf-8")

    def accept_mutated_ast(data):
        check = next(item for item in data["symbol_checks"] if item["symbol"] == "mid")
        check["parameters"][0]["kind"] = "positional_only"

    _mutate(pedagogy / "lessons/02.yml", accept_mutated_ast)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-09" and "renders 'mid(book, /)" in issue.message
        for issue in issues
    )


def test_source_return_annotation_must_match_the_canonical_signature(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 2, "mid",
        "02-python-ii-functional-book/exercises/order_book.py",
    )
    text = source.read_text(encoding="utf-8")
    source.write_text(text.replace("def mid(book):", "def mid(book) -> str:", 1), encoding="utf-8")

    def accept_mutated_ast(data):
        check = next(item for item in data["symbol_checks"] if item["symbol"] == "mid")
        check["source_returns"] = "str"

    _mutate(pedagogy / "lessons/02.yml", accept_mutated_ast)
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_all_four_early_api_signature_mutations_fail_together(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_module_symbol_checks(
        tmp_path, pedagogy, 2,
        "02-python-ii-functional-book/exercises/order_book.py",
    )
    text = source.read_text(encoding="utf-8")
    mutations = {
        "def make_order(symbol, side, price, size):": "def make_order(symbol, side, price, quantity):",
        "def add_order(book, order):": "def add_order(order, book):",
        "def cancel_order(book, order_id):": "def cancel_order(book, id_to_cancel):",
        "def mid(book):": "def mid(book, fallback=None):",
    }
    for old, new in mutations.items():
        assert old in text
        text = text.replace(old, new, 1)
    source.write_text(text, encoding="utf-8")
    issues = validate_repository(ROOT, pedagogy)
    broken = {
        issue.message.split()[1]
        for issue in issues
        if issue.check == "PED-CHECK-09" and issue.message.startswith("symbol ")
    }
    assert {"make_order", "add_order", "cancel_order", "mid"} <= broken


def test_l3_cannot_drop_mid_from_the_reused_module(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 3, "mid",
        "03-python-iii-modules/exercises/order_book.py",
    )
    text = source.read_text(encoding="utf-8")
    source.write_text(text.replace("def mid(book):", "def midpoint(book):", 1), encoding="utf-8")
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_inert_global_recall_gap_is_rejected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "course_graph.yml",
        lambda data: data["recall_policy"].update(gap_lessons=99),
    )
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-04" and "inert fields" in issue.message
        for issue in issues
    )


def test_explicit_global_recall_edges_cannot_be_emptied(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "course_graph.yml",
        lambda data: data["recall_policy"].update(required_edges=[]),
    )
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-04" and "nonempty required_edges" in issue.message
        for issue in issues
    )


def test_recall_policy_must_be_an_object(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "course_graph.yml",
        lambda data: data.update(recall_policy=None),
    )
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-04" and "must be an object" in issue.message
        for issue in issues
    )


def test_l8_starter_argument_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_package_check(
        tmp_path, pedagogy, 8, "MatchingEngine", "process",
        "08-order-types-matching/exercises/exchange/matching.py",
    )
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "order: Order, book: OrderBook", "order: Order"
        ),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l10_starter_type_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_package_check(
        tmp_path, pedagogy, 10, "Strategy", "on_book_update",
        "10-strategy-framework/exercises/exchange/strategy.py",
    )
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "book: OrderBook", "book: object"
        ),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l10_starter_return_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_package_check(
        tmp_path, pedagogy, 10, "Strategy", "on_book_update",
        "10-strategy-framework/exercises/exchange/strategy.py",
    )
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "-> list[Action]", "-> tuple[Action, ...]"
        ),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l10_action_alias_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 10, "Action",
        "10-strategy-framework/exercises/exchange/strategy.py",
    )
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "Action = NewOrder | Cancel", "Action = NewOrder"
        ),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_l4_public_type_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    source = _rebind_symbol_check(
        tmp_path, pedagogy, 4, "Side",
        "04-oop-i-order-trade/exercises/exchange/orders.py",
    )
    source.write_text(
        source.read_text(encoding="utf-8").replace("class Side", "class HiddenSide"),
        encoding="utf-8",
    )
    assert "PED-CHECK-09" in _checks(validate_repository(ROOT, pedagogy))


def test_strict_lesson_cannot_borrow_an_api_binding_from_an_earlier_lesson(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def remove_local_mid(data):
        check = next(
            item for item in data["package_checks"]
            if item["class"] == "OrderBook"
        )
        check["members"].pop("mid")

    _mutate(pedagogy / "lessons/08.yml", remove_local_mid)
    issues = validate_repository(ROOT, pedagogy)
    assert any(
        issue.check == "PED-CHECK-09"
        and issue.lesson == 8
        and "orderbook.mid" in issue.message
        for issue in issues
    )


def test_official_item_cannot_depend_on_optional(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def make_optional(data):
        objective = next(item for item in data["objectives"] if item["id"] == "l01-explain-execution")
        objective["route"] = "OPTIONAL"

    _mutate(pedagogy / "lessons/01.yml", make_optional)
    assert "PED-CHECK-06" in _checks(validate_repository(ROOT, pedagogy))


@pytest.mark.parametrize("key", ["objective", "concept", "cognitive_level", "difficulty"])
def test_assessment_mapping_fields_are_mandatory(tmp_path, key):
    pedagogy = _copy_contract(tmp_path)
    _mutate(pedagogy / "assessment_blueprint.yml", lambda data: data["items"][0].pop(key))
    assert "PED-CHECK-07" in _checks(validate_repository(ROOT, pedagogy))
