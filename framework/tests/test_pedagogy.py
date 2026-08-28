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


def test_current_pilot_contract_passes():
    assert validate_repository(ROOT) == []


def test_required_concept_before_introduction_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(
        pedagogy / "lessons/01.yml",
        lambda data: data["requires"]["concepts"].append("matching.atomicity"),
    )
    assert "PED-CHECK-01" in _checks(validate_repository(ROOT, pedagogy))


def test_method_to_property_regression_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)

    def change(data):
        next(item for item in data["api_surface"] if item["id"] == "orderbook.mid")["kind"] = "method"

    _mutate(pedagogy / "lessons/07.yml", change)
    assert "PED-CHECK-02" in _checks(validate_repository(ROOT, pedagogy))


def test_missing_distant_recall_is_detected(tmp_path):
    pedagogy = _copy_contract(tmp_path)
    _mutate(pedagogy / "lessons/10.yml", lambda data: data.update(recalls=[]))
    assert "PED-CHECK-04" in _checks(validate_repository(ROOT, pedagogy))


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
