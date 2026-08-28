#!/usr/bin/env python3
"""Validate the machine-readable pedagogical contract.

The ``.yml`` files deliberately use JSON-compatible YAML so the checker runs
with the Python standard library in CI and in the public course repository.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
PEDAGOGY = ROOT / "pedagogy"
API_FIELDS = ("name", "kind", "signature", "returns", "responsibility")
STRICT_STATUSES = {"pilot", "fixture", "contract-strict"}


@dataclass(frozen=True)
class Issue:
    check: str
    lesson: int | None
    message: str

    def label(self) -> str:
        where = f" L{self.lesson:02d}" if self.lesson is not None else ""
        return f"{self.check}{where}: {self.message}"


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"{path}: the pedagogical YAML must remain JSON-compatible: {exc}"
        ) from exc


def _ids(items: Iterable[dict[str, Any]]) -> list[str]:
    return [item["id"] for item in items]


def _source_dom(source: Path) -> tuple[set[str], set[int]]:
    text = source.read_text(encoding="utf-8")
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    stages = {int(value) for value in re.findall(r'\bdata-stage="(\d+)"', text)}
    return ids, stages


def _class_member_kinds(path: Path, class_name: str) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            out: dict[str, str] = {}
            for member in node.body:
                if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                decorators = {
                    d.id for d in member.decorator_list if isinstance(d, ast.Name)
                }
                if "property" in decorators:
                    kind = "property"
                elif "classmethod" in decorators:
                    kind = "classmethod"
                elif "staticmethod" in decorators:
                    kind = "staticmethod"
                else:
                    kind = "method"
                out[member.name] = kind
            return out
    return {}


def validate_repository(
    root: Path | str = ROOT,
    pedagogy_dir: Path | str | None = None,
) -> list[Issue]:
    root = Path(root)
    pedagogy = Path(pedagogy_dir) if pedagogy_dir else root / "pedagogy"
    graph = _load(pedagogy / "course_graph.yml")
    blueprint = _load(pedagogy / "assessment_blueprint.yml")
    exercise_routes = _load(pedagogy / "exercise_routes.yml")
    routes = set(graph["routes"])
    allowed_scene_types = set(graph["scene_types"])
    issues: list[Issue] = []

    lessons: list[dict[str, Any]] = []
    for relative in graph["lesson_files"]:
        lessons.append(_load(pedagogy / relative))
    lessons.sort(key=lambda item: item["lesson"])
    by_number = {item["lesson"]: item for item in lessons}

    # Exercise routes are explicit decisions for the migrated pilot lessons.
    declared_route_lessons = {
        int(value) for value in exercise_routes.get("lessons", {})
    }
    expected_route_lessons = set(
        graph["coverage"].get("explicit_exercise_route_lessons", [])
    )
    if declared_route_lessons != expected_route_lessons:
        issues.append(Issue(
            "PED-CHECK-05", None,
            f"explicit exercise route lessons are {sorted(declared_route_lessons)}; "
            f"expected {sorted(expected_route_lessons)}",
        ))
    for lesson_key, kinds in exercise_routes.get("lessons", {}).items():
        n = int(lesson_key)
        for kind in ("build", "aux"):
            items = kinds.get(kind)
            if items is None:
                issues.append(Issue("PED-CHECK-05", n, f"exercise routes miss {kind}"))
                continue
            titles = [item.get("title") for item in items]
            if len(titles) != len(set(titles)):
                issues.append(Issue("PED-CHECK-05", n, f"duplicate {kind} exercise title"))
            for item in items:
                if item.get("route") not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", n,
                        f"exercise {item.get('title')!r} has no valid route",
                    ))
                if not isinstance(item.get("minutes"), int) or item["minutes"] <= 0:
                    issues.append(Issue(
                        "PED-CHECK-08", n,
                        f"exercise {item.get('title')!r} has no positive load",
                    ))

    # PED-CHECK-03 — lesson references and source anchors must be current.
    actual_order = [item["lesson"] for item in lessons]
    if actual_order != graph["lesson_order"]:
        issues.append(Issue("PED-CHECK-03", None, f"lesson order is {actual_order}"))

    concept_intro: dict[str, tuple[int, str]] = {}
    api_intro: dict[str, int] = {}
    objectives: dict[str, tuple[int, str, set[str]]] = {}
    api_contract: dict[str, tuple[int, dict[str, Any]]] = {}

    for lesson in lessons:
        n = lesson["lesson"]
        for concept in lesson["introduces"]["concepts"]:
            cid = concept["id"]
            if cid in concept_intro:
                issues.append(Issue("PED-CHECK-01", n, f"concept {cid} introduced twice"))
            else:
                concept_intro[cid] = (n, concept.get("importance", "supporting"))
        for api_id in lesson["introduces"]["apis"]:
            if api_id in api_intro:
                issues.append(Issue("PED-CHECK-02", n, f"API {api_id} introduced twice"))
            else:
                api_intro[api_id] = n
        for objective in lesson.get("objectives", []):
            oid = objective["id"]
            if oid in objectives:
                issues.append(Issue("PED-CHECK-07", n, f"objective {oid} is duplicated"))
            objectives[oid] = (n, objective["route"], set(objective["concepts"]))

        for surface in lesson.get("api_surface", []):
            api_id = surface["id"]
            missing = [key for key in API_FIELDS if key not in surface]
            if missing:
                issues.append(Issue("PED-CHECK-02", n, f"API {api_id} misses {missing}"))
                continue
            if api_id not in api_contract:
                api_contract[api_id] = (n, surface)
                continue
            before_n, before = api_contract[api_id]
            changed = [key for key in API_FIELDS if before[key] != surface[key]]
            if changed:
                transitions = lesson.get("api_transitions", [])
                explicit = any(
                    transition.get("from_api") == api_id
                    and transition.get("to_api") == api_id
                    for transition in transitions
                )
                if not explicit:
                    issues.append(Issue(
                        "PED-CHECK-02",
                        n,
                        f"silent API change for {api_id} since L{before_n}: {changed}",
                    ))

        if lesson.get("source_path"):
            source = root / lesson["source_path"]
            if not source.exists():
                issues.append(Issue("PED-CHECK-03", n, f"missing source {source}"))
            else:
                dom_ids, dom_stages = _source_dom(source)
                for scene in lesson.get("scenes", []):
                    if scene["dom_id"] not in dom_ids:
                        issues.append(Issue(
                            "PED-CHECK-03", n,
                            f"scene {scene['id']} points to missing #{scene['dom_id']}",
                        ))
                    for stage in scene.get("stages", []):
                        dom_stage = stage.get("dom_stage")
                        if dom_stage is not None and dom_stage not in dom_stages:
                            issues.append(Issue(
                                "PED-CHECK-03", n,
                                f"stage {scene['id']}/{stage['id']} points to missing data-stage={dom_stage}",
                            ))

    # PED-CHECK-01 — prerequisites must exist strictly before use.
    for lesson in lessons:
        n = lesson["lesson"]
        for cid in lesson["requires"]["concepts"]:
            introduced = concept_intro.get(cid)
            if introduced is None:
                issues.append(Issue("PED-CHECK-01", n, f"required concept {cid} is never introduced"))
            elif introduced[0] >= n:
                issues.append(Issue(
                    "PED-CHECK-01", n,
                    f"required concept {cid} is introduced in L{introduced[0]}",
                ))
        for api_id in lesson["requires"]["apis"]:
            introduced = api_intro.get(api_id)
            if introduced is None:
                issues.append(Issue("PED-CHECK-01", n, f"required API {api_id} is never introduced"))
            elif introduced >= n:
                issues.append(Issue(
                    "PED-CHECK-01", n,
                    f"required API {api_id} is introduced in L{introduced}",
                ))
        for api_id in lesson["introduces"]["apis"]:
            if not any(item["id"] == api_id for item in lesson.get("api_surface", [])):
                issues.append(Issue(
                    "PED-CHECK-02", n,
                    f"introduced API {api_id} has no explicit surface contract",
                ))

    # PED-CHECK-04 — distant major prerequisites need an explicit recall.
    gap = int(graph["recall_policy"]["gap_lessons"])
    for lesson in lessons:
        n = lesson["lesson"]
        if lesson.get("status") not in STRICT_STATUSES:
            continue
        if (
            lesson.get("delivery") == "assessment-linear"
            and graph["recall_policy"].get("assessment_delivery_exempt")
        ):
            continue
        recalled = {item["concept"]: item for item in lesson.get("recalls", [])}
        for cid in lesson["requires"]["concepts"]:
            introduced = concept_intro.get(cid)
            if not introduced:
                continue
            introduced_in, importance = introduced
            if importance == graph["recall_policy"]["importance"] and n - introduced_in >= gap:
                recall = recalled.get(cid)
                if not recall:
                    issues.append(Issue(
                        "PED-CHECK-04", n,
                        f"major concept {cid} from L{introduced_in} needs an explicit recall",
                    ))
                elif recall.get("introduced_in") != introduced_in or not recall.get("mapping"):
                    issues.append(Issue(
                        "PED-CHECK-04", n,
                        f"recall for {cid} must identify L{introduced_in} and provide a mapping",
                    ))
        for cid, recall in recalled.items():
            introduced = concept_intro.get(cid)
            if not introduced or recall.get("introduced_in") != introduced[0]:
                issues.append(Issue("PED-CHECK-03", n, f"stale recall reference for {cid}"))

    # PED-CHECK-05 and PED-CHECK-08 — complete route and load classification.
    for lesson in lessons:
        n = lesson["lesson"]
        scenes = lesson.get("scenes", [])
        scene_ids = _ids(scenes)
        classified: list[str] = []
        for route, ids in lesson["routes"].items():
            if route not in routes:
                issues.append(Issue("PED-CHECK-05", n, f"unknown route {route}"))
            classified.extend(ids)
        if lesson.get("delivery") != "assessment-linear":
            if sorted(classified) != sorted(scene_ids) or len(classified) != len(set(classified)):
                issues.append(Issue(
                    "PED-CHECK-05", n,
                    "every scene must appear exactly once in LIVE/REQUIRED/OPTIONAL",
                ))
        for scene in scenes:
            if scene.get("route") not in routes:
                issues.append(Issue("PED-CHECK-05", n, f"scene {scene['id']} has no valid route"))
            if scene.get("type") not in allowed_scene_types:
                issues.append(Issue("PED-CHECK-05", n, f"scene {scene['id']} has unknown type"))
            if not scene.get("layout") or not scene.get("concepts") or scene.get("duration_minutes", 0) <= 0:
                issues.append(Issue("PED-CHECK-05", n, f"scene {scene['id']} misses semantic metadata"))
            for stage in scene.get("stages", []):
                if stage.get("route") not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", n,
                        f"stage {scene['id']}/{stage.get('id')} has no valid route",
                    ))
        load = lesson.get("load", {})
        required_load = (
            "live_presentation_minutes", "guided_minutes",
            "required_autonomous_minutes", "optional_minutes", "overflow_policy",
        )
        missing_load = [key for key in required_load if key not in load]
        if missing_load:
            issues.append(Issue("PED-CHECK-08", n, f"load contract misses {missing_load}"))
        if scenes and lesson.get("delivery") == "lesson":
            live_minutes = load.get("live_presentation_minutes", -1)
            if not 18 <= live_minutes <= 22:
                issues.append(Issue(
                    "PED-CHECK-08", n,
                    f"LIVE route is {live_minutes} minutes; expected 18–22",
                ))

    # PED-CHECK-06/07 — assessment metadata and optional exclusion.
    required_item_keys = {
        "id", "lesson", "objective", "concept", "cognitive_level", "difficulty",
    }
    for item in blueprint["items"]:
        missing = sorted(required_item_keys - set(item))
        n = item.get("lesson")
        if missing:
            issues.append(Issue("PED-CHECK-07", n, f"assessment item misses {missing}"))
            continue
        objective = objectives.get(item["objective"])
        if not objective:
            issues.append(Issue("PED-CHECK-07", n, f"unknown objective {item['objective']}"))
            continue
        owner, route, concepts = objective
        if owner != n or item["concept"] not in concepts:
            issues.append(Issue(
                "PED-CHECK-07", n,
                f"item {item['id']} does not map to its lesson/objective/concept",
            ))
        if route not in blueprint["allowed_routes"]:
            issues.append(Issue(
                "PED-CHECK-06", n,
                f"item {item['id']} depends on {route} content",
            ))

    # PED-CHECK-03 — reject the specific stale semantics observed in the audit.
    for relative in graph.get("text_audit", {}).get("strict_paths", []):
        path = root / relative
        if not path.exists():
            issues.append(Issue("PED-CHECK-03", None, f"text-audit path missing: {relative}"))
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in graph["text_audit"].get("forbidden_phrases", []):
            if phrase.casefold() in text:
                issues.append(Issue(
                    "PED-CHECK-03", None,
                    f"stale phrase {phrase!r} in {relative}",
                ))

    # PED-CHECK-09 — generated package surfaces must match the contract.
    for lesson in lessons:
        n = lesson["lesson"]
        for check in lesson.get("package_checks", []):
            path = root / check["path"]
            if not path.exists():
                issues.append(Issue("PED-CHECK-09", n, f"missing starter package {path}"))
                continue
            actual = _class_member_kinds(path, check["class"])
            for member, expected_kind in check["members"].items():
                if actual.get(member) != expected_kind:
                    issues.append(Issue(
                        "PED-CHECK-09", n,
                        f"{check['class']}.{member} is {actual.get(member)!r}, expected {expected_kind}",
                    ))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--pedagogy-dir", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        issues = validate_repository(args.root, args.pedagogy_dir)
    except ValueError as exc:
        print(f"PED-CHECK-LOAD: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps([asdict(issue) for issue in issues], ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(issue.label())
        print(f"FAIL — {len(issues)} pedagogical contract issue(s).")
    else:
        print("OK — PED-CHECK-01..09 passed for the declared pilot scope.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
