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
