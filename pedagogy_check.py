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


def _annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ast.unparse(node)


def _parameter(
    node: ast.arg,
    kind: str,
    default: ast.expr | None = None,
    *,
    has_default: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": node.arg,
        "kind": kind,
        "annotation": _annotation(node.annotation),
    }
    if has_default:
        result["default"] = ast.unparse(default) if default is not None else None
    return result


def _function_parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, Any]]:
    positional = [
        (arg, "positional_only") for arg in node.args.posonlyargs
    ] + [
        (arg, "positional_or_keyword") for arg in node.args.args
    ]
    default_offset = len(positional) - len(node.args.defaults)
    parameters: list[dict[str, Any]] = []
    for index, (arg, kind) in enumerate(positional):
        has_default = index >= default_offset
        default = node.args.defaults[index - default_offset] if has_default else None
        parameters.append(_parameter(
            arg, kind, default, has_default=has_default,
        ))
    if node.args.vararg:
        parameters.append(_parameter(node.args.vararg, "var_positional"))
    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        parameters.append(_parameter(
            arg, "keyword_only", default, has_default=default is not None,
        ))
    if node.args.kwarg:
        parameters.append(_parameter(node.args.kwarg, "var_keyword"))
    return parameters


def _class_member_surfaces(path: Path, class_name: str) -> dict[str, dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            out: dict[str, dict[str, Any]] = {}
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
                parameters = _function_parameters(member)
                if parameters and parameters[0]["name"] in {"self", "cls"}:
                    parameters = parameters[1:]
                out[member.name] = {
                    "kind": kind,
                    "parameters": parameters,
                    "returns": _annotation(member.returns),
                }
            return out
    return {}


def _render_signature(
    name: str,
    kind: str,
    parameters: list[dict[str, Any]],
    returns: str,
) -> str:
    if kind == "property":
        return f"{name} -> {returns}"
    rendered = []
    for parameter in parameters:
        part = parameter["name"]
        if parameter["kind"] == "var_positional":
            part = f"*{part}"
        elif parameter["kind"] == "var_keyword":
            part = f"**{part}"
        if parameter.get("annotation"):
            part += f": {parameter['annotation']}"
        if "default" in parameter:
            part += f" = {parameter['default']}"
        rendered.append(part)
    return f"{name}({', '.join(rendered)}) -> {returns}"


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
    guided_policy = graph.get("load_policy", {}).get("guided_practice_minutes", {})
    guided_minimum = guided_policy.get("minimum")
    guided_maximum = guided_policy.get("maximum")
    guided_delta = guided_policy.get("allowed_delta_from_declared")
    if not all(isinstance(value, int) for value in (
        guided_minimum, guided_maximum, guided_delta,
    )):
        issues.append(Issue(
            "PED-CHECK-08", None,
            "guided practice policy must declare integer minimum, maximum, and allowed delta",
        ))
    for lesson_key, kinds in exercise_routes.get("lessons", {}).items():
        n = int(lesson_key)
        all_titles: list[str | None] = []
        live_minutes = 0
        for kind in ("build", "aux"):
            items = kinds.get(kind)
            if items is None:
                issues.append(Issue("PED-CHECK-05", n, f"exercise routes miss {kind}"))
                continue
            titles = [item.get("title") for item in items]
            all_titles.extend(titles)
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
                elif item.get("route") == "LIVE":
                    live_minutes += item["minutes"]
        if len(all_titles) != len(set(all_titles)):
            issues.append(Issue(
                "PED-CHECK-05", n,
                "an exercise appears more than once across build/aux classifications",
            ))
        guided_minutes = by_number.get(n, {}).get("load", {}).get("guided_minutes")
        if isinstance(guided_minimum, int) and isinstance(guided_maximum, int):
            if not guided_minimum <= live_minutes <= guided_maximum:
                issues.append(Issue(
                    "PED-CHECK-08", n,
                    f"LIVE exercises total {live_minutes} minutes; "
                    f"expected {guided_minimum}–{guided_maximum}",
                ))
        if not isinstance(guided_minutes, int) or guided_minutes <= 0:
            issues.append(Issue(
                "PED-CHECK-08", n,
                "guided_minutes must be a positive integer",
            ))
        elif isinstance(guided_delta, int) and abs(live_minutes - guided_minutes) > guided_delta:
            issues.append(Issue(
                "PED-CHECK-08", n,
                f"LIVE exercises total {live_minutes} minutes but guided_minutes is "
                f"{guided_minutes}; allowed delta is {guided_delta}",
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
            presentation_policy = graph.get("load_policy", {}).get(
                "live_presentation_minutes", {}
            )
            minimum = presentation_policy.get("minimum")
            maximum = presentation_policy.get("maximum")
            if not (
                isinstance(live_minutes, int)
                and isinstance(minimum, int)
                and isinstance(maximum, int)
                and minimum <= live_minutes <= maximum
            ):
                issues.append(Issue(
                    "PED-CHECK-08", n,
                    f"LIVE route is {live_minutes} minutes; expected {minimum}–{maximum}",
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

    # PED-CHECK-09 — material APIs must bind to exact generated starter surfaces.
    bound_apis_by_lesson: dict[int, set[str]] = {}
    for lesson in lessons:
        n = lesson["lesson"]
        lesson_bound_apis = bound_apis_by_lesson.setdefault(n, set())
        for check in lesson.get("package_checks", []):
            path = root / check["path"]
            if not path.exists():
                issues.append(Issue("PED-CHECK-09", n, f"missing starter package {path}"))
                continue
            actual = _class_member_surfaces(path, check["class"])
            if not actual:
                issues.append(Issue(
                    "PED-CHECK-09", n,
                    f"missing class {check['class']} in {check['path']}",
                ))
                continue
            for member, expected in check["members"].items():
                if not isinstance(expected, dict):
                    issues.append(Issue(
                        "PED-CHECK-09", n,
                        f"{check['class']}.{member} binding must declare api, kind, parameters, and returns",
                    ))
                    continue
                missing = [
                    key for key in ("api", "kind", "parameters", "returns")
                    if key not in expected
                ]
                if missing:
                    issues.append(Issue(
                        "PED-CHECK-09", n,
                        f"{check['class']}.{member} binding misses {missing}",
                    ))
                    continue
                api_id = expected["api"]
                lesson_bound_apis.add(api_id)
                actual_member = actual.get(member)
                expected_member = {
                    "kind": expected["kind"],
                    "parameters": expected["parameters"],
                    "returns": expected["returns"],
                }
                if actual_member != expected_member:
                    issues.append(Issue(
                        "PED-CHECK-09", n,
                        f"{check['class']}.{member} is {actual_member!r}, "
                        f"expected {expected_member!r}",
                    ))
                    continue
                contract_entry = api_contract.get(api_id)
                if contract_entry is None:
                    issues.append(Issue(
                        "PED-CHECK-09", n,
                        f"{check['class']}.{member} binds unknown API {api_id}",
                    ))
                    continue
                _, surface = contract_entry
                rendered = _render_signature(
                    member,
                    expected["kind"],
                    expected["parameters"],
                    expected["returns"],
                )
                if (
                    surface["name"] != member
                    or surface["kind"] != expected["kind"]
                    or surface["returns"] != expected["returns"]
                    or surface["signature"] != rendered
                ):
                    issues.append(Issue(
                        "PED-CHECK-09", n,
                        f"starter binding for {api_id} renders {rendered!r}, "
                        f"contract declares {surface['signature']!r}",
                    ))

    for lesson in lessons:
        n = lesson["lesson"]
        if lesson.get("status") not in STRICT_STATUSES:
            continue
        material_apis = set(lesson["requires"]["apis"]) | set(
            lesson["introduces"]["apis"]
        )
        missing = sorted(material_apis - bound_apis_by_lesson.get(n, set()))
        if missing:
            issues.append(Issue(
                "PED-CHECK-09", n,
                f"material APIs have no typed starter binding: {missing}",
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
