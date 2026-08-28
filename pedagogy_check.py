#!/usr/bin/env python3
"""Validate the full-course machine-readable pedagogical contract.

The .yml files use JSON-compatible YAML so this checker needs only the Python
standard library.  It proves that LIVE + REQUIRED prior knowledge is sufficient
for every later mandatory route and audits the student-facing API surface.
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
CATEGORIES = ("concepts", "apis", "notation")
API_FIELDS = ("name", "kind", "signature", "returns", "responsibility", "qualified_name")
ROUTE_FIELDS = ("LIVE", "REQUIRED", "OPTIONAL")


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


def _function_parameters(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[dict[str, Any]]:
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


def _decorator_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return None


def _dataclass_constructor(node: ast.ClassDef) -> dict[str, Any] | None:
    decorators = {_decorator_name(item) for item in node.decorator_list}
    if "dataclass" not in decorators:
        return None
    parameters: list[dict[str, Any]] = []
    for member in node.body:
        if not (
            isinstance(member, ast.AnnAssign)
            and isinstance(member.target, ast.Name)
        ):
            continue
        item: dict[str, Any] = {
            "name": member.target.id,
            "kind": "positional_or_keyword",
            "annotation": _annotation(member.annotation),
        }
        if member.value is not None:
            item["default"] = ast.unparse(member.value)
        parameters.append(item)
    return {"kind": "constructor", "parameters": parameters, "returns": node.name}


def _class_member_surfaces(
    path: Path,
    class_name: str,
) -> dict[str, dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        out: dict[str, dict[str, Any]] = {}
        constructor = _dataclass_constructor(node)
        if constructor is not None:
            out["__init__"] = constructor
        for member in node.body:
            if (
                isinstance(member, ast.AnnAssign)
                and isinstance(member.target, ast.Name)
            ):
                out[member.target.id] = {
                    "kind": "attribute",
                    "parameters": [],
                    "returns": _annotation(member.annotation),
                }
                continue
            if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorators = {_decorator_name(item) for item in member.decorator_list}
            if member.name == "__init__":
                kind = "constructor"
                returns = class_name
            elif "property" in decorators:
                kind = "property"
                returns = _annotation(member.returns)
            elif "setter" in decorators:
                # The public contract is the property getter; assignment support
                # must not overwrite its typed surface with the setter function.
                continue
            elif "classmethod" in decorators:
                kind = "classmethod"
                returns = _annotation(member.returns)
            elif "staticmethod" in decorators:
                kind = "staticmethod"
                returns = _annotation(member.returns)
            else:
                kind = "method"
                returns = _annotation(member.returns)
            parameters = _function_parameters(member)
            if parameters and parameters[0]["name"] in {"self", "cls"}:
                parameters = parameters[1:]
            out[member.name] = {
                "kind": kind,
                "parameters": parameters,
                "returns": returns,
            }
        return out
    return {}


def _module_symbol_surface(path: Path, symbol: str) -> dict[str, Any] | None:
    """Return the typed surface of a public class/type alias in one module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == symbol:
            return {"kind": "type", "returns": symbol}
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == symbol for target in node.targets):
                return {"kind": "type_alias", "returns": ast.unparse(node.value)}
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == symbol
            and node.value is not None
        ):
            return {"kind": "type_alias", "returns": ast.unparse(node.value)}
    return None


def _render_signature(
    name: str,
    kind: str,
    parameters: list[dict[str, Any]],
    returns: str,
) -> str:
    if kind == "property":
        return f"{name} -> {returns}"
    if kind == "attribute":
        return f"{name}: {returns}"
    if kind == "type":
        return f"{name}: type"
    if kind == "type_alias":
        return f"{name} = {returns}"
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


def _lesson_introductions(
    lesson: dict[str, Any],
    category: str,
) -> list[tuple[str, str, str]]:
    if category == "concepts":
        return [
            (
                item["id"],
                item.get("route", ""),
                item.get("importance", "supporting"),
            )
            for item in lesson.get("introduces", {}).get(category, [])
        ]
    ids = lesson.get("introduces", {}).get(category, [])
    routes = lesson.get("introduction_routes", {}).get(category, {})
    return [(item_id, routes.get(item_id, ""), "supporting") for item_id in ids]


def _registry_ids(graph: dict[str, Any], category: str) -> list[str]:
    return _ids(graph.get("registries", {}).get(category, []))


def _exercise_titles(notebook: Path) -> list[str]:
    data = json.loads(notebook.read_text(encoding="utf-8"))
    excluded = {"Cómo funciona este cuaderno", "El gimnasio"}
    titles: list[str] = []
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        for line in source.splitlines():
            match = re.match(r"^###\s+(.+?)\s*$", line)
            if match and match.group(1) not in excluded:
                titles.append(match.group(1))
    return titles


def _resolve_lesson_notebooks(root: Path, lesson: int) -> dict[str, Path]:
    folders = sorted(path for path in root.glob(f"{lesson:02d}-*") if path.is_dir())
    if len(folders) != 1:
        return {}
    exercises = folders[0] / "exercises"
    return {
        "build": exercises / f"{lesson:02d}_build_exercises.ipynb",
        "aux": exercises / f"{lesson:02d}_auxiliary.ipynb",
    }


def _available(
    introductions: dict[str, tuple[int, str, str]],
    item_id: str,
    lesson: int,
) -> bool:
    introduced = introductions.get(item_id)
    return introduced is not None and introduced[0] <= lesson


def build_course_inventory(
    root: Path | str = ROOT,
    pedagogy_dir: Path | str | None = None,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Return first introduction, route, later requirements, and recalls by ID."""
    root = Path(root)
    pedagogy = Path(pedagogy_dir) if pedagogy_dir else root / "pedagogy"
    graph = _load(pedagogy / "course_graph.yml")
    lessons = sorted(
        (_load(pedagogy / relative) for relative in graph["lesson_files"]),
        key=lambda item: item["lesson"],
    )
    inventory: dict[str, dict[str, dict[str, Any]]] = {
        category: {} for category in CATEGORIES
    }
    for lesson in lessons:
        number = lesson["lesson"]
        for category in CATEGORIES:
            for item_id, route, importance in _lesson_introductions(
                lesson, category,
            ):
                inventory[category][item_id] = {
                    "introduced_in": number,
                    "route": route,
                    "importance": importance,
                    "required_by": [],
                    "recalled_by": [],
                }
    for lesson in lessons:
        number = lesson["lesson"]
        for category in CATEGORIES:
            route_map = lesson.get("requirement_routes", {}).get(category, {})
            for item_id in lesson.get("requires", {}).get(category, []):
                if item_id in inventory[category]:
                    inventory[category][item_id]["required_by"].append({
                        "lesson": number,
                        "route": route_map.get(item_id),
                    })
        for recall in lesson.get("recalls", []):
            for category, key in (
                ("concepts", "concept"), ("apis", "api"), ("notation", "notation"),
            ):
                item_id = recall.get(key)
                if item_id in inventory[category]:
                    inventory[category][item_id]["recalled_by"].append(number)
    return inventory


def validate_repository(
    root: Path | str = ROOT,
    pedagogy_dir: Path | str | None = None,
) -> list[Issue]:
    root = Path(root)
    pedagogy = Path(pedagogy_dir) if pedagogy_dir else root / "pedagogy"
    graph = _load(pedagogy / "course_graph.yml")
    blueprint = _load(pedagogy / "assessment_blueprint.yml")
    exercise_routes = _load(pedagogy / "exercise_routes.yml")
    routes = set(graph.get("routes", []))
    mandatory_routes = set(graph.get("required_knowledge_routes", []))
    scene_types = set(graph.get("scene_types", []))
    issues: list[Issue] = []

    lessons = sorted(
        (_load(pedagogy / relative) for relative in graph["lesson_files"]),
        key=lambda item: item["lesson"],
    )
    numbers = [item["lesson"] for item in lessons]
    by_number = {item["lesson"]: item for item in lessons}
    number_set = set(numbers)

    # Full-course coverage is a contract, not a pilot flag.
    expected_all = list(range(1, 16))
    expected_runtime = list(range(1, 15))
    coverage = graph.get("coverage", {})
    if numbers != expected_all or graph.get("lesson_order") != expected_all:
        issues.append(Issue(
            "PED-CHECK-03", None,
            f"lesson order/manifest coverage must be L1-L15, got {numbers}",
        ))
    if (
        coverage.get("mode") != "full-course"
        or coverage.get("runtime_lessons") != expected_runtime
        or coverage.get("contract_strict_lessons") != expected_all
        or coverage.get("legacy_unmigrated_lessons")
    ):
        issues.append(Issue(
            "PED-CHECK-05", None,
            "coverage must declare full-course runtime L1-L14, strict L1-L15, and no legacy lessons",
        ))
    expected_route_lessons = set(expected_runtime)
    declared_route_lessons = {
        int(value) for value in exercise_routes.get("lessons", {})
    }
    if declared_route_lessons != expected_route_lessons:
        issues.append(Issue(
            "PED-CHECK-05", None,
            f"exercise routes cover {sorted(declared_route_lessons)}; expected L1-L14",
        ))
    if set(coverage.get("explicit_exercise_route_lessons", [])) != expected_route_lessons:
        issues.append(Issue(
            "PED-CHECK-05", None,
            "course coverage does not mark every L1-L14 exercise manifest explicit",
        ))

    # Stable central registries and explicit introduction routes.
    registry_sets: dict[str, set[str]] = {}
    for category in CATEGORIES:
        ids = _registry_ids(graph, category)
        registry_sets[category] = set(ids)
        if len(ids) != len(set(ids)):
            issues.append(Issue(
                "PED-CHECK-03", None, f"{category} registry contains duplicate IDs",
            ))

    introductions: dict[str, dict[str, tuple[int, str, str]]] = {
        category: {} for category in CATEGORIES
    }
    api_registry = {
        item["id"]: item for item in graph.get("registries", {}).get("apis", [])
    }
    for api_id, item in api_registry.items():
        missing = [key for key in API_FIELDS if key not in item]
        if missing:
            issues.append(Issue(
                "PED-CHECK-02", None,
                f"API registry entry {api_id} misses {missing}",
            ))

    objectives: dict[str, tuple[int, str, dict[str, set[str]]]] = {}
    for lesson in lessons:
        number = lesson["lesson"]
        for category in CATEGORIES:
            declared = _lesson_introductions(lesson, category)
            local_ids = [item[0] for item in declared]
            if len(local_ids) != len(set(local_ids)):
                issues.append(Issue(
                    "PED-CHECK-03", number,
                    f"{category} has duplicate introductions",
                ))
            if category != "concepts":
                route_keys = set(
                    lesson.get("introduction_routes", {}).get(category, {})
                )
                if route_keys != set(local_ids):
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"{category} introduction routes do not match introduced IDs",
                    ))
            for item_id, route, importance in declared:
                if route not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"{category} introduction {item_id} has invalid route {route!r}",
                    ))
                if item_id not in registry_sets[category]:
                    issues.append(Issue(
                        "PED-CHECK-03", number,
                        f"{category} introduction {item_id} is not registered",
                    ))
                if item_id in introductions[category]:
                    first = introductions[category][item_id][0]
                    issues.append(Issue(
                        "PED-CHECK-01", number,
                        f"{category[:-1]} {item_id} was already introduced in L{first}",
                    ))
                else:
                    introductions[category][item_id] = (
                        number, route, importance,
                    )

        for objective in lesson.get("objectives", []):
            objective_id = objective["id"]
            if objective_id in objectives:
                issues.append(Issue(
                    "PED-CHECK-07", number,
                    f"objective {objective_id} is duplicated",
                ))
            refs = {
                category: set(objective.get(category, []))
                for category in CATEGORIES
            }
            objectives[objective_id] = (
                number, objective.get("route"), refs,
            )

    for category in CATEGORIES:
        introduced_ids = set(introductions[category])
        if introduced_ids != registry_sets[category]:
            missing = sorted(registry_sets[category] - introduced_ids)
            unregistered = sorted(introduced_ids - registry_sets[category])
            issues.append(Issue(
                "PED-CHECK-03", None,
                f"{category} registry mismatch; never introduced={missing}, unregistered={unregistered}",
            ))

    # used_later is a deterministic projection of future requirements,
    # recalls, and objectives.  Keeping it in each manifest makes the learner
    # journey inspectable without allowing a second hand-maintained truth.
    for index, lesson in enumerate(lessons):
        number = lesson["lesson"]
        own = {
            category: {
                item_id for item_id, _, _ in _lesson_introductions(
                    lesson, category,
                )
            }
            for category in CATEGORIES
        }
        expected = {category: set() for category in CATEGORIES}
        for later in lessons[index + 1:]:
            for category in CATEGORIES:
                expected[category].update(
                    own[category]
                    & set(later.get("requires", {}).get(category, []))
                )
                for objective in later.get("objectives", []):
                    expected[category].update(
                        own[category] & set(objective.get(category, []))
                    )
            for recall in later.get("recalls", []):
                for category, key in (
                    ("concepts", "concept"),
                    ("apis", "api"),
                    ("notation", "notation"),
                ):
                    item_id = recall.get(key)
                    if item_id in own[category]:
                        expected[category].add(item_id)
        declared = lesson.get("used_later", {})
        if set(declared) != set(CATEGORIES):
            issues.append(Issue(
                "PED-CHECK-03", number,
                "used_later must declare concepts, APIs, and notation",
            ))
        for category in CATEGORIES:
            actual = declared.get(category, [])
            wanted = sorted(expected[category])
            if actual != wanted:
                issues.append(Issue(
                    "PED-CHECK-03", number,
                    f"used_later.{category} is {actual}; expected {wanted}",
                ))

    # KNOWN(n): all prior LIVE + REQUIRED introductions, route-aware in all categories.
    for lesson in lessons:
        number = lesson["lesson"]
        for category in CATEGORIES:
            required_ids = lesson.get("requires", {}).get(category, [])
            route_map = lesson.get("requirement_routes", {}).get(category, {})
            if set(route_map) != set(required_ids):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"{category} requirement routes do not match required IDs",
                ))
            for item_id in required_ids:
                requirement_route = route_map.get(item_id)
                if requirement_route not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"{category} requirement {item_id} has invalid route {requirement_route!r}",
                    ))
                if item_id not in registry_sets[category]:
                    issues.append(Issue(
                        "PED-CHECK-01", number,
                        f"required {category[:-1]} {item_id} is not registered",
                    ))
                    continue
                introduced = introductions[category].get(item_id)
                if introduced is None:
                    issues.append(Issue(
                        "PED-CHECK-01", number,
                        f"required {category[:-1]} {item_id} is never introduced",
                    ))
                elif introduced[0] >= number:
                    issues.append(Issue(
                        "PED-CHECK-01", number,
                        f"required {category[:-1]} {item_id} is introduced in L{introduced[0]}",
                    ))
                elif (
                    requirement_route in mandatory_routes
                    and introduced[1] not in mandatory_routes
                ):
                    issues.append(Issue(
                        "PED-CHECK-06", number,
                        f"{requirement_route} depends on OPTIONAL {category[:-1]} {item_id} from L{introduced[0]}",
                    ))

    # API registry is the canonical public surface; any local drift is silent change.
    for lesson in lessons:
        number = lesson["lesson"]
        surfaces = lesson.get("api_surface", [])
        surface_ids = _ids(surfaces)
        material = set(lesson.get("requires", {}).get("apis", [])) | set(
            lesson.get("introduces", {}).get("apis", [])
        )
        if set(surface_ids) != material or len(surface_ids) != len(set(surface_ids)):
            issues.append(Issue(
                "PED-CHECK-02", number,
                "api_surface must declare every required/introduced API exactly once",
            ))
        for surface in surfaces:
            api_id = surface["id"]
            canonical = api_registry.get(api_id)
            if canonical is None:
                issues.append(Issue(
                    "PED-CHECK-02", number,
                    f"API {api_id} has no central contract",
                ))
                continue
            changed = [
                key for key in API_FIELDS
                if surface.get(key) != canonical.get(key)
            ]
            if changed:
                issues.append(Issue(
                    "PED-CHECK-02", number,
                    f"silent API change for {api_id}: {changed}",
                ))
        for transition in lesson.get("api_transitions", []):
            missing = [
                field for field in ("from_api", "to_api", "kind", "reason")
                if not transition.get(field)
            ]
            if missing:
                issues.append(Issue(
                    "PED-CHECK-02", number,
                    f"API transition misses {missing}",
                ))
                continue
            canonical_target = api_registry.get(transition["to_api"])
            if canonical_target is None:
                issues.append(Issue(
                    "PED-CHECK-02", number,
                    f"API transition targets unknown {transition['to_api']}",
                ))
            elif (
                transition.get("to_signature") is not None
                and transition["to_signature"] != canonical_target.get("signature")
            ):
                issues.append(Issue(
                    "PED-CHECK-02", number,
                    "API transition to_signature must match its canonical target",
                ))
            if transition["from_api"] not in api_registry:
                missing_signatures = [
                    field for field in ("from_signature", "to_signature")
                    if not transition.get(field)
                ]
                if missing_signatures:
                    issues.append(Issue(
                        "PED-CHECK-02", number,
                        "a pedagogical API transition needs explicit before/after signatures",
                    ))

    # Recall references and the explicit high-value recovery edges.
    for lesson in lessons:
        number = lesson["lesson"]
        seen_recalls: set[tuple[str, str]] = set()
        for recall in lesson.get("recalls", []):
            keys = [
                (category, key)
                for category, key in (
                    ("concepts", "concept"), ("apis", "api"), ("notation", "notation"),
                )
                if recall.get(key)
            ]
            if len(keys) != 1:
                issues.append(Issue(
                    "PED-CHECK-04", number,
                    "each recall must identify exactly one concept, API, or notation ID",
                ))
                continue
            category, key = keys[0]
            item_id = recall[key]
            introduced = introductions[category].get(item_id)
            if (
                introduced is None
                or recall.get("introduced_in") != introduced[0]
                or introduced[0] >= number
            ):
                issues.append(Issue(
                    "PED-CHECK-03", number,
                    f"stale recall reference for {item_id}",
                ))
            if not isinstance(recall.get("mapping"), dict) or not all(
                recall["mapping"].get(field) for field in ("before", "now")
            ):
                issues.append(Issue(
                    "PED-CHECK-04", number,
                    f"recall for {item_id} needs before/now mapping",
                ))
            marker = (category, item_id)
            if marker in seen_recalls:
                issues.append(Issue(
                    "PED-CHECK-04", number,
                    f"duplicate recall for {item_id}",
                ))
            seen_recalls.add(marker)

    for edge in graph.get("recall_policy", {}).get("required_edges", []):
        number = edge.get("lesson")
        concept = edge.get("concept")
        if number not in number_set:
            issues.append(Issue(
                "PED-CHECK-03", None,
                f"recall policy references missing lesson {number}",
            ))
            continue
        matching = [
            recall for recall in by_number[number].get("recalls", [])
            if recall.get("concept") == concept
        ]
        if not matching:
            issues.append(Issue(
                "PED-CHECK-04", number,
                f"required recovery edge for {concept} is missing",
            ))

    # Complete scene, objective, bridge, source-anchor, and load manifests.
    for lesson in lessons:
        number = lesson["lesson"]
        delivery = lesson.get("delivery")
        scenes = lesson.get("scenes", [])
        if number <= 14 and (
            delivery != "lesson"
            or not scenes
            or not lesson.get("objectives")
            or not all(lesson.get("routes", {}).get(route) for route in ("LIVE", "REQUIRED"))
        ):
            issues.append(Issue(
                "PED-CHECK-05", number,
                "L1-L14 need nonempty scenes, LIVE/REQUIRED routes, and objectives",
            ))
        if number == 15 and delivery != "assessment-linear":
            issues.append(Issue(
                "PED-CHECK-05", number,
                "L15 must preserve assessment-linear delivery",
            ))

        scene_ids = _ids(scenes)
        classified: list[str] = []
        for route, ids in lesson.get("routes", {}).items():
            if route not in routes:
                issues.append(Issue(
                    "PED-CHECK-05", number, f"unknown route {route}",
                ))
            classified.extend(ids)
        if delivery != "assessment-linear" and (
            sorted(classified) != sorted(scene_ids)
            or len(classified) != len(set(classified))
        ):
            issues.append(Issue(
                "PED-CHECK-05", number,
                "every scene must appear exactly once in LIVE/REQUIRED/OPTIONAL",
            ))

        source_path = lesson.get("source_path")
        dom_ids: set[str] = set()
        dom_stages: set[int] = set()
        if number <= 14:
            source = root / source_path if source_path else None
            if source is None or not source.exists():
                issues.append(Issue(
                    "PED-CHECK-03", number,
                    f"missing source {source_path!r}",
                ))
            else:
                dom_ids, dom_stages = _source_dom(source)

        for scene in scenes:
            route = scene.get("route")
            if scene.get("dom_id") not in dom_ids:
                issues.append(Issue(
                    "PED-CHECK-03", number,
                    f"scene {scene.get('id')} points to missing #{scene.get('dom_id')}",
                ))
            if route not in routes or scene.get("type") not in scene_types:
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"scene {scene.get('id')} has invalid route/type",
                ))
            if (
                not scene.get("layout")
                or not scene.get("concepts")
                or not isinstance(scene.get("duration_minutes"), int)
                or scene.get("duration_minutes", 0) <= 0
            ):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"scene {scene.get('id')} misses semantic metadata",
                ))
            for concept in scene.get("concepts", []):
                introduced = introductions["concepts"].get(concept)
                if introduced is None or introduced[0] > number:
                    issues.append(Issue(
                        "PED-CHECK-01", number,
                        f"scene {scene.get('id')} uses unavailable concept {concept}",
                    ))
                elif route in mandatory_routes and introduced[1] not in mandatory_routes:
                    issues.append(Issue(
                        "PED-CHECK-06", number,
                        f"scene {scene.get('id')} depends on OPTIONAL concept {concept}",
                    ))
                elif (
                    introduced[0] == number
                    and route in mandatory_routes
                    and introduced[1] == "REQUIRED"
                    and route == "LIVE"
                ):
                    issues.append(Issue(
                        "PED-CHECK-06", number,
                        f"LIVE scene {scene.get('id')} uses REQUIRED-only concept {concept}",
                    ))
            for stage in scene.get("stages", []):
                if stage.get("route") not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"stage {scene.get('id')}/{stage.get('id')} has invalid route",
                    ))
                dom_stage = stage.get("dom_stage")
                if dom_stage is not None and dom_stage not in dom_stages:
                    issues.append(Issue(
                        "PED-CHECK-03", number,
                        f"stage {scene.get('id')}/{stage.get('id')} points to missing data-stage={dom_stage}",
                    ))

        for objective in lesson.get("objectives", []):
            route = objective.get("route")
            if route not in routes:
                issues.append(Issue(
                    "PED-CHECK-07", number,
                    f"objective {objective.get('id')} has invalid route",
                ))
            for category in CATEGORIES:
                for item_id in objective.get(category, []):
                    introduced = introductions[category].get(item_id)
                    if introduced is None or introduced[0] > number:
                        issues.append(Issue(
                            "PED-CHECK-07", number,
                            f"objective {objective.get('id')} uses unavailable {item_id}",
                        ))
                    elif route in mandatory_routes and introduced[1] not in mandatory_routes:
                        issues.append(Issue(
                            "PED-CHECK-06", number,
                            f"objective {objective.get('id')} depends on OPTIONAL {item_id}",
                        ))
                    local_route = None
                    if introduced is not None and introduced[0] == number:
                        local_route = introduced[1]
                    elif item_id in lesson.get("requires", {}).get(category, []):
                        local_route = lesson.get("requirement_routes", {}).get(
                            category, {},
                        ).get(item_id)
                    if (
                        route == "LIVE" and local_route in {"REQUIRED", "OPTIONAL"}
                    ) or (
                        route == "REQUIRED" and local_route == "OPTIONAL"
                    ):
                        issues.append(Issue(
                            "PED-CHECK-06", number,
                            f"{route} objective {objective.get('id')} uses "
                            f"{local_route}-only {category[:-1]} {item_id}",
                        ))

        bridge = lesson.get("bridge")
        if number <= 14:
            if not isinstance(bridge, dict):
                issues.append(Issue(
                    "PED-CHECK-03", number, "lesson has no causal bridge",
                ))
            else:
                target = bridge.get("target_lesson")
                if target not in number_set or target != number + 1:
                    issues.append(Issue(
                        "PED-CHECK-03", number,
                        f"bridge must target the next existing lesson L{number + 1}, got {target}",
                    ))
                if not bridge.get("limitation") or not bridge.get("need"):
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        "bridge needs limitation and need fields",
                    ))
                known = bridge.get("known", {})
                for category in CATEGORIES:
                    for item_id in known.get(category, []):
                        introduced = introductions[category].get(item_id)
                        if introduced is None or introduced[0] > number:
                            issues.append(Issue(
                                "PED-CHECK-03", number,
                                f"bridge claims unavailable {category[:-1]} {item_id}",
                            ))
                        elif introduced[1] not in mandatory_routes:
                            issues.append(Issue(
                                "PED-CHECK-06", number,
                                f"bridge knowledge includes OPTIONAL {item_id}",
                            ))
        elif bridge is not None:
            issues.append(Issue(
                "PED-CHECK-03", number, "assessment lesson must not target another lesson",
            ))

        load = lesson.get("load", {})
        load_fields = (
            "live_presentation_minutes", "guided_minutes",
            "required_autonomous_minutes", "optional_minutes", "overflow_policy",
        )
        missing_load = [field for field in load_fields if field not in load]
        if missing_load:
            issues.append(Issue(
                "PED-CHECK-08", number,
                f"load contract misses {missing_load}",
            ))
        if delivery == "lesson":
            policy = graph.get("load_policy", {}).get(
                "live_presentation_minutes", {}
            )
            live = load.get("live_presentation_minutes")
            if not (
                isinstance(live, int)
                and isinstance(policy.get("minimum"), int)
                and isinstance(policy.get("maximum"), int)
                and policy["minimum"] <= live <= policy["maximum"]
            ):
                issues.append(Issue(
                    "PED-CHECK-08", number,
                    f"LIVE presentation is {live}; expected {policy.get('minimum')}–{policy.get('maximum')}",
                ))

    # Explicit notebook exercise classification and guided-practice load.
    guided = graph.get("load_policy", {}).get("guided_practice_minutes", {})
    for key, kinds in exercise_routes.get("lessons", {}).items():
        number = int(key)
        notebooks = _resolve_lesson_notebooks(root, number)
        all_declared: list[str] = []
        route_minutes = {route: 0 for route in ("LIVE", "REQUIRED", "OPTIONAL")}
        for kind in ("build", "aux"):
            items = kinds.get(kind)
            if not isinstance(items, list):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"exercise routes miss {kind}",
                ))
                continue
            titles = [item.get("title") for item in items]
            all_declared.extend(titles)
            if len(titles) != len(set(titles)):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"duplicate {kind} exercise title",
                ))
            notebook = notebooks.get(kind)
            if notebook is None or not notebook.exists():
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"missing {kind} notebook for route audit",
                ))
            else:
                actual_titles = _exercise_titles(notebook)
                if titles != actual_titles:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"{kind} route titles do not exactly match notebook exercises",
                    ))
            for item in items:
                route = item.get("route")
                minutes = item.get("minutes")
                if route not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"exercise {item.get('title')!r} has invalid route",
                    ))
                if not isinstance(minutes, int) or minutes <= 0:
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"exercise {item.get('title')!r} has no positive load",
                    ))
                elif route in route_minutes:
                    route_minutes[route] += minutes
        if len(all_declared) != len(set(all_declared)):
            issues.append(Issue(
                "PED-CHECK-05", number,
                "an exercise appears in both build and aux classifications",
            ))
        minimum = guided.get("minimum")
        maximum = guided.get("maximum")
        delta = guided.get("allowed_delta_from_declared")
        lesson_load = by_number.get(number, {}).get("load", {})
        live_minutes = route_minutes["LIVE"]
        declared = lesson_load.get("guided_minutes")
        if not (
            isinstance(minimum, int)
            and isinstance(maximum, int)
            and minimum <= live_minutes <= maximum
        ):
            issues.append(Issue(
                "PED-CHECK-08", number,
                f"LIVE exercises total {live_minutes}; expected {minimum}–{maximum}",
            ))
        if not isinstance(declared, int) or not isinstance(delta, int):
            issues.append(Issue(
                "PED-CHECK-08", number,
                "guided_minutes and allowed delta must be integers",
            ))
        elif abs(live_minutes - declared) > delta:
            issues.append(Issue(
                "PED-CHECK-08", number,
                f"LIVE exercises total {live_minutes}, guided_minutes is {declared}, allowed delta {delta}",
            ))
        for route, field in (
            ("REQUIRED", "required_autonomous_minutes"),
            ("OPTIONAL", "optional_minutes"),
        ):
            project = lesson_load.get("required_project_minutes", 0) if route == "REQUIRED" else 0
            if not isinstance(project, int) or project < 0:
                issues.append(Issue(
                    "PED-CHECK-08", number,
                    "required_project_minutes must be a non-negative integer",
                ))
                project = 0
            actual = route_minutes[route] + project
            declared = lesson_load.get(field)
            if not isinstance(declared, int) or declared != actual:
                issues.append(Issue(
                    "PED-CHECK-08", number,
                    f"{route} autonomous total {actual} "
                    f"(exercises {route_minutes[route]} + project {project}), "
                    f"{field} is {declared}; exact equality is required",
                ))

    # Assessment traceability and OPTIONAL exclusion.
    required_item_keys = {
        "id", "lesson", "objective", "concept", "cognitive_level", "difficulty",
    }
    item_ids: set[str] = set()
    for item in blueprint.get("items", []):
        missing = sorted(required_item_keys - set(item))
        number = item.get("lesson")
        if missing:
            issues.append(Issue(
                "PED-CHECK-07", number,
                f"assessment item misses {missing}",
            ))
            continue
        if item["id"] in item_ids:
            issues.append(Issue(
                "PED-CHECK-07", number,
                f"assessment item {item['id']} is duplicated",
            ))
        item_ids.add(item["id"])
        if number not in number_set:
            issues.append(Issue(
                "PED-CHECK-03", number,
                f"assessment item targets nonexistent lesson {number}",
            ))
            continue
        objective = objectives.get(item["objective"])
        if objective is None:
            issues.append(Issue(
                "PED-CHECK-07", number,
                f"unknown objective {item['objective']}",
            ))
            continue
        owner, route, refs = objective
        if owner != number or item["concept"] not in refs["concepts"]:
            issues.append(Issue(
                "PED-CHECK-07", number,
                f"item {item['id']} does not map to its lesson/objective/concept",
            ))
        if route not in blueprint.get("allowed_routes", []):
            issues.append(Issue(
                "PED-CHECK-06", number,
                f"item {item['id']} depends on {route} content",
            ))
        concept_intro = introductions["concepts"].get(item["concept"])
        if concept_intro and concept_intro[1] == "OPTIONAL":
            issues.append(Issue(
                "PED-CHECK-06", number,
                f"item {item['id']} assesses OPTIONAL concept {item['concept']}",
            ))

    blueprint_lessons: set[int] = set()
    for entry in blueprint.get("lesson_blueprints", []):
        number = entry.get("lesson")
        if number not in number_set:
            issues.append(Issue(
                "PED-CHECK-03", number,
                f"blueprint references nonexistent lesson {number}",
            ))
            continue
        blueprint_lessons.add(number)
        for objective in entry.get("objectives", []):
            record = objectives.get(objective.get("id"))
            if record is None or record[0] != number:
                issues.append(Issue(
                    "PED-CHECK-07", number,
                    f"blueprint has unknown objective {objective.get('id')}",
                ))
            elif objective.get("route") != record[1]:
                issues.append(Issue(
                    "PED-CHECK-07", number,
                    f"blueprint route drift for {objective.get('id')}",
                ))
            elif objective.get("assessed") and record[1] not in blueprint.get("allowed_routes", []):
                issues.append(Issue(
                    "PED-CHECK-06", number,
                    f"blueprint assesses OPTIONAL objective {objective.get('id')}",
                ))
    if blueprint_lessons != number_set:
        issues.append(Issue(
            "PED-CHECK-07", None,
            f"assessment blueprint covers lessons {sorted(blueprint_lessons)}, expected L1-L15",
        ))

    # Future-proof text and lesson-reference audit.
    text_audit = graph.get("text_audit", {})
    exemptions = text_audit.get("exemptions", [])
    for exemption in exemptions:
        if not all(exemption.get(key) for key in ("path", "pattern_id", "reason")):
            issues.append(Issue(
                "PED-CHECK-03", None,
                "text-audit exemptions require path, pattern_id, and reason",
            ))
    for relative in text_audit.get("strict_paths", []):
        path = root / relative
        if not path.exists():
            issues.append(Issue(
                "PED-CHECK-03", None,
                f"text-audit path missing: {relative}",
            ))
            continue
        text = path.read_text(encoding="utf-8")
        folded = text.casefold()
        for phrase in text_audit.get("forbidden_phrases", []):
            if phrase.casefold() in folded:
                issues.append(Issue(
                    "PED-CHECK-03", None,
                    f"stale phrase {phrase!r} in {relative}",
                ))
        for rule in text_audit.get("forbidden_patterns", []):
            matches = list(re.finditer(rule["pattern"], text, re.IGNORECASE))
            if not matches:
                continue
            exempt = any(
                item.get("path") == relative
                and item.get("pattern_id") == rule.get("id")
                for item in exemptions
            )
            if not exempt:
                issues.append(Issue(
                    "PED-CHECK-03", None,
                    f"{rule.get('message', rule.get('id'))} in {relative}",
                ))
        for rule in text_audit.get("reference_patterns", []):
            for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
                try:
                    targets = [int(match.group("lesson"))]
                    end = match.groupdict().get("lesson_end")
                    if end is not None:
                        targets.append(int(end))
                except (IndexError, TypeError, ValueError):
                    issues.append(Issue(
                        "PED-CHECK-03", None,
                        f"reference rule {rule.get('id')} must expose named group 'lesson'",
                    ))
                    break
                for target in targets:
                    if target not in number_set:
                        issues.append(Issue(
                            "PED-CHECK-03", None,
                            f"nonexistent L{target} reference in {relative}",
                        ))

    # Exact package binding for selected cumulative snapshots.
    bound_by_lesson: dict[int, set[str]] = {}
    for lesson in lessons:
        number = lesson["lesson"]
        bound = bound_by_lesson.setdefault(number, set())
        for check in lesson.get("symbol_checks", []):
            path = root / check["path"]
            if not path.exists():
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"missing starter package {path}",
                ))
                continue
            missing = [key for key in ("symbol", "api", "kind", "returns") if key not in check]
            if missing:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"symbol binding in {check['path']} misses {missing}",
                ))
                continue
            api_id = check["api"]
            bound.add(api_id)
            actual = _module_symbol_surface(path, check["symbol"])
            expected = {"kind": check["kind"], "returns": check["returns"]}
            if actual != expected:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"symbol {check['symbol']} is {actual!r}, expected {expected!r}",
                ))
                continue
            canonical = api_registry.get(api_id)
            if canonical is None:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"symbol {check['symbol']} binds unknown API {api_id}",
                ))
                continue
            rendered = _render_signature(
                canonical["name"], check["kind"], [], check["returns"],
            )
            if (
                canonical["kind"] != check["kind"]
                or canonical["returns"] != check["returns"]
                or canonical["signature"] != rendered
            ):
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"starter binding for {api_id} renders {rendered!r}, contract declares {canonical['signature']!r}",
                ))
        for check in lesson.get("package_checks", []):
            path = root / check["path"]
            if not path.exists():
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"missing starter package {path}",
                ))
                continue
            actual = _class_member_surfaces(path, check["class"])
            if not actual:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"missing class {check['class']} in {check['path']}",
                ))
                continue
            for member, expected in check.get("members", {}).items():
                if not isinstance(expected, dict):
                    issues.append(Issue(
                        "PED-CHECK-09", number,
                        f"{check['class']}.{member} binding must be structured",
                    ))
                    continue
                missing = [
                    key for key in ("api", "kind", "parameters", "returns")
                    if key not in expected
                ]
                if missing:
                    issues.append(Issue(
                        "PED-CHECK-09", number,
                        f"{check['class']}.{member} binding misses {missing}",
                    ))
                    continue
                api_id = expected["api"]
                bound.add(api_id)
                actual_member = actual.get(member)
                expected_member = {
                    "kind": expected["kind"],
                    "parameters": expected["parameters"],
                    "returns": expected["returns"],
                }
                if actual_member != expected_member:
                    issues.append(Issue(
                        "PED-CHECK-09", number,
                        f"{check['class']}.{member} is {actual_member!r}, expected {expected_member!r}",
                    ))
                    continue
                canonical = api_registry.get(api_id)
                if canonical is None:
                    issues.append(Issue(
                        "PED-CHECK-09", number,
                        f"{check['class']}.{member} binds unknown API {api_id}",
                    ))
                    continue
                rendered = _render_signature(
                    canonical["name"], expected["kind"],
                    expected["parameters"], expected["returns"],
                )
                if (
                    canonical["kind"] != expected["kind"]
                    or canonical["returns"] != expected["returns"]
                    or canonical["signature"] != rendered
                ):
                    issues.append(Issue(
                        "PED-CHECK-09", number,
                        f"starter binding for {api_id} renders {rendered!r}, contract declares {canonical['signature']!r}",
                    ))

    for number in coverage.get("typed_package_binding_lessons", []):
        lesson = by_number.get(number)
        if lesson is None:
            issues.append(Issue(
                "PED-CHECK-03", None,
                f"typed package scope references missing lesson {number}",
            ))
            continue
        material = set(lesson.get("requires", {}).get("apis", [])) | set(
            lesson.get("introduces", {}).get("apis", [])
        )
        missing = sorted(material - bound_by_lesson.get(number, set()))
        if missing:
            issues.append(Issue(
                "PED-CHECK-09", number,
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
        print(json.dumps(
            [asdict(issue) for issue in issues],
            ensure_ascii=False, indent=2,
        ))
    elif issues:
        for issue in issues:
            print(issue.label())
        print(f"FAIL — {len(issues)} pedagogical contract issue(s).")
    else:
        print("OK — full-course PED-CHECK-01..09 passed for L1–L15.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
