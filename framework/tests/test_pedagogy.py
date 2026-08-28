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


def test_unclassified_scene_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["routes"]["LIVE"].remove("l08-simulator")

    _mutate(pedagogy / "lessons/08.yml", change)
    assert "PED-CHECK-05" in _checks(validate_repository(ROOT, pedagogy))


def test_unclassified_exercise_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        data["lessons"]["8"]["build"][0].pop("route")

    _mutate(pedagogy / "exercise_routes.yml", change)
    assert "PED-CHECK-05" in _checks(validate_repository(ROOT, pedagogy))


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
