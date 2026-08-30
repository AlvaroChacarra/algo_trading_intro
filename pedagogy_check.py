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


def _is_integer(value: Any) -> bool:
    """Return True for contract integers, excluding JSON booleans."""
    return type(value) is int


def _is_positive_integer(value: Any) -> bool:
    return _is_integer(value) and value > 0


def _is_overlap_id(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _object_list(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


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
        out: dict[str, dict[str, Any]] = {
            "__class__": {
                "bases": [ast.unparse(base) for base in node.bases],
            },
        }
        constructor = _dataclass_constructor(node)
        if constructor is not None:
            out["__init__"] = constructor
        for member in node.body:
            if isinstance(member, ast.Assign):
                for target in member.targets:
                    if isinstance(target, ast.Name):
                        out[target.id] = {
                            "kind": "assignment",
                            "parameters": [],
                            "returns": None,
                        }
                continue
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
            is_async = isinstance(member, ast.AsyncFunctionDef)
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
            if is_async:
                kind = f"async_{kind}"
            parameters = _function_parameters(member)
            if parameters and parameters[0]["name"] in {"self", "cls"}:
                parameters = parameters[1:]
            out[member.name] = {
                "kind": kind,
                "parameters": parameters,
                "returns": returns,
                "abstract": "abstractmethod" in decorators,
            }
        return out
    return {}


def _module_symbol_surface(path: Path, symbol: str) -> dict[str, Any] | None:
    """Return the AST surface of a public function, class, or type alias."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    surface: dict[str, Any] | None = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
            surface = {
                "kind": (
                    "async_function"
                    if isinstance(node, ast.AsyncFunctionDef)
                    else "function"
                ),
                "parameters": _function_parameters(node),
                "source_returns": _annotation(node.returns),
            }
            continue
        if isinstance(node, ast.ClassDef) and node.name == symbol:
            surface = {"kind": "type", "returns": symbol}
            continue
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == symbol for target in node.targets):
                surface = {"kind": "type_alias", "returns": ast.unparse(node.value)}
                continue
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == symbol
            and node.value is not None
        ):
            surface = {"kind": "type_alias", "returns": ast.unparse(node.value)}
            continue
        if isinstance(node, ast.Delete) and any(
            isinstance(target, ast.Name) and target.id == symbol
            for target in node.targets
        ):
            surface = None
    return surface


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
    rendered: list[str] = []
    emitted_keyword_separator = False
    has_var_positional = any(
        parameter.get("kind") == "var_positional" for parameter in parameters
    )
    for index, parameter in enumerate(parameters):
        parameter_kind = parameter["kind"]
        if (
            parameter_kind == "keyword_only"
            and not has_var_positional
            and not emitted_keyword_separator
        ):
            rendered.append("*")
            emitted_keyword_separator = True
        part = parameter["name"]
        if parameter_kind == "var_positional":
            part = f"*{part}"
        elif parameter_kind == "var_keyword":
            part = f"**{part}"
        if parameter.get("annotation"):
            part += f": {parameter['annotation']}"
        if "default" in parameter:
            part += f" = {parameter['default']}"
        rendered.append(part)
        if (
            parameter_kind == "positional_only"
            and (
                index + 1 == len(parameters)
                or parameters[index + 1].get("kind") != "positional_only"
            )
        ):
            rendered.append("/")
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


def _autonomous_scene_contract(
    lesson: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return every autonomous document/quiz state that needs load metadata.

    A top-level REQUIRED/OPTIONAL scene is one component with the scene's
    declared duration.  In a mixed LIVE scene, each stage whose effective
    route changes becomes its own explicit component because the top-level
    duration cannot honestly apportion that autonomous work.
    """
    expected: dict[str, dict[str, Any]] = {}
    for scene in _object_list(lesson.get("scenes", [])):
        scene_route = scene.get("route")
        kind = "quiz" if scene.get("type") == "diagnostic-quiz" else "document"
        scene_id = scene.get("id")
        if (
            isinstance(scene_route, str)
            and scene_route in {"REQUIRED", "OPTIONAL"}
            and _is_identifier(scene_id)
        ):
            expected[scene_id] = {
                "kind": kind,
                "route": scene_route,
                "minutes": scene.get("duration_minutes"),
            }
            continue
        for stage in _object_list(scene.get("stages", [])):
            effective_route = stage.get("route", scene_route)
            stage_id = stage.get("id")
            if (
                isinstance(effective_route, str)
                and effective_route in {"REQUIRED", "OPTIONAL"}
                and effective_route != scene_route
                and _is_identifier(scene_id)
                and _is_identifier(stage_id)
            ):
                expected[f"{scene_id}/{stage_id}"] = {
                    "kind": kind,
                    "route": effective_route,
                    "minutes": stage.get("duration_minutes"),
                }
    return expected


def _timed_scene_states(lesson: dict[str, Any]) -> list[dict[str, Any]]:
    """Return additive time budgets keyed by their effective route.

    ``scene.duration_minutes`` budgets the scene's base route; it is not a
    wall-clock total shared by route overrides. Every override contributes its
    own canonical ``stage.duration_minutes`` budget on the effective route.
    """
    states: list[dict[str, Any]] = []
    for scene in _object_list(lesson.get("scenes", [])):
        scene_route = scene.get("route")
        states.append({
            "id": scene.get("id"),
            "route": scene_route,
            "minutes": scene.get("duration_minutes"),
        })
        for stage in _object_list(scene.get("stages", [])):
            effective_route = stage.get("route", scene_route)
            if effective_route != scene_route:
                states.append({
                    "id": f"{scene.get('id')}/{stage.get('id')}",
                    "route": effective_route,
                    "minutes": stage.get("duration_minutes"),
                })
    return states


def _component_total(
    components: list[dict[str, Any]], route: str,
) -> int:
    """Deduplicate overlap groups after their global contract is validated."""
    selected = [item for item in components if item.get("route") == route]
    total = sum(
        item["minutes"]
        for item in selected
        if not _is_overlap_id(item.get("overlap_id"))
        and _is_positive_integer(item.get("minutes"))
    )
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in selected:
        overlap_id = item.get("overlap_id")
        if _is_overlap_id(overlap_id):
            grouped.setdefault(overlap_id, []).append(item)
    for overlap_id, members in grouped.items():
        valid_minutes = [
            item["minutes"]
            for item in members
            if _is_positive_integer(item.get("minutes"))
        ]
        total += valid_minutes[0] if valid_minutes else 0
    return total


def _overlap_contract_errors(components: list[dict[str, Any]]) -> list[str]:
    """Validate each overlap once across routes and component kinds."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in components:
        overlap_id = item.get("overlap_id")
        if _is_overlap_id(overlap_id):
            grouped.setdefault(overlap_id, []).append(item)
    errors: list[str] = []
    for overlap_id, members in grouped.items():
        kinds = [item.get("kind") for item in members]
        routes = {item.get("route") for item in members}
        minutes = {
            item.get("minutes")
            for item in members
            if _is_positive_integer(item.get("minutes"))
        }
        if (
            len(members) < 2
            or len(set(kinds)) != len(members)
            or len(routes) != 1
            or len(minutes) != 1
            or any(
                not _is_positive_integer(item.get("minutes"))
                for item in members
            )
        ):
            errors.append(
                f"overlap_id {overlap_id!r} must join one component per "
                "different kind, on one route, with equal minutes"
            )
    return errors


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
    exercise_lesson_contract = exercise_routes.get("lessons", {})
    if not isinstance(exercise_lesson_contract, dict):
        issues.append(Issue(
            "PED-CHECK-05", None,
            "exercise route lessons must be an object with canonical numeric keys",
        ))
        exercise_lesson_contract = {}
    exercise_lesson_items: list[tuple[int, dict[str, Any]]] = []
    declared_route_lessons: set[int] = set()
    for key, value in exercise_lesson_contract.items():
        if (
            not isinstance(key, str)
            or not re.fullmatch(r"[1-9]\d*", key)
            or str(int(key)) != key
        ):
            issues.append(Issue(
                "PED-CHECK-05", None,
                f"exercise route lesson key {key!r} is not canonical",
            ))
            continue
        number = int(key)
        if number not in number_set:
            issues.append(Issue(
                "PED-CHECK-03", number,
                "exercise routes reference a missing lesson",
            ))
            continue
        if not isinstance(value, dict):
            issues.append(Issue(
                "PED-CHECK-05", number,
                "exercise route lesson entry must be an object",
            ))
            continue
        declared_route_lessons.add(number)
        exercise_lesson_items.append((number, value))
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
                or not _is_integer(recall.get("introduced_in"))
                or recall.get("introduced_in") != introduced[0]
                or introduced[0] >= number
            ):
                issues.append(Issue(
                    "PED-CHECK-03", number,
                    f"stale recall reference for {item_id}",
                ))
            if not isinstance(recall.get("mapping"), dict) or not all(
                isinstance(recall["mapping"].get(field), str)
                and recall["mapping"][field].strip()
                for field in ("before", "now")
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

    recall_policy = graph.get("recall_policy", {})
    if not isinstance(recall_policy, dict):
        issues.append(Issue(
            "PED-CHECK-04", None,
            "recall policy must be an object",
        ))
        recall_policy = {}
    allowed_recall_fields = {"mode", "required_edges", "rationale"}
    unknown_recall_fields = sorted(set(recall_policy) - allowed_recall_fields)
    if recall_policy.get("mode") != "explicit-required-edges":
        issues.append(Issue(
            "PED-CHECK-04", None,
            "recall policy must declare mode='explicit-required-edges'",
        ))
    if unknown_recall_fields:
        issues.append(Issue(
            "PED-CHECK-04", None,
            f"recall policy contains inert fields {unknown_recall_fields}",
        ))
    if not (
        isinstance(recall_policy.get("rationale"), str)
        and recall_policy["rationale"].strip()
    ):
        issues.append(Issue(
            "PED-CHECK-04", None,
            "explicit recall policy needs a rationale",
        ))
    required_recall_edges = recall_policy.get("required_edges")
    if not isinstance(required_recall_edges, list) or not required_recall_edges:
        issues.append(Issue(
            "PED-CHECK-04", None,
            "explicit recall policy needs a nonempty required_edges list",
        ))
        required_recall_edges = []
    seen_recall_edges: set[tuple[int, str]] = set()
    for edge in required_recall_edges:
        if not isinstance(edge, dict):
            issues.append(Issue(
                "PED-CHECK-04", None,
                "required recall edges must be lesson/concept objects",
            ))
            continue
        number = edge.get("lesson")
        concept = edge.get("concept")
        if (
            set(edge) != {"lesson", "concept"}
            or not _is_integer(number)
            or not isinstance(concept, str)
            or not concept
        ):
            issues.append(Issue(
                "PED-CHECK-04", number if _is_integer(number) else None,
                "required recall edges need integer lesson/nonempty concept pairs",
            ))
            continue
        marker = (number, concept)
        if marker in seen_recall_edges:
            issues.append(Issue(
                "PED-CHECK-04", number,
                "required recall edges need unique lesson/concept pairs",
            ))
        seen_recall_edges.add(marker)
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
        raw_scenes = lesson.get("scenes", [])
        if not isinstance(raw_scenes, list) or any(
            not isinstance(scene, dict) for scene in raw_scenes
        ):
            issues.append(Issue(
                "PED-CHECK-05", number,
                "scenes must be a list of objects",
            ))
        scenes = _object_list(raw_scenes)
        raw_declared_routes = lesson.get("routes", {})
        if not isinstance(raw_declared_routes, dict):
            issues.append(Issue(
                "PED-CHECK-05", number,
                "routes must be an object",
            ))
        route_manifest = (
            raw_declared_routes if isinstance(raw_declared_routes, dict) else {}
        )
        if number <= 14 and (
            delivery != "lesson"
            or not scenes
            or not lesson.get("objectives")
            or not all(route_manifest.get(route) for route in ("LIVE", "REQUIRED"))
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

        expected_route_ids = {route: [] for route in ROUTE_FIELDS}
        if delivery != "assessment-linear":
            seen_scene_ids: set[str] = set()
            for scene in scenes:
                scene_id = scene.get("id")
                if (
                    not _is_identifier(scene_id)
                    or scene_id in seen_scene_ids
                ):
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"scene id {scene_id!r} must be unique and nonempty",
                    ))
                else:
                    seen_scene_ids.add(scene_id)
                scene_route = scene.get("route")
                if (
                    isinstance(scene_route, str)
                    and scene_route in expected_route_ids
                    and _is_identifier(scene_id)
                ):
                    expected_route_ids[scene_route].append(scene_id)
                raw_stages = scene.get("stages", [])
                if not isinstance(raw_stages, list) or any(
                    not isinstance(stage, dict) for stage in raw_stages
                ):
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"scene {scene_id!r} stages must be a list of objects",
                    ))
                seen_stage_ids: set[str] = set()
                for stage in _object_list(raw_stages):
                    stage_id = stage.get("id")
                    if (
                        not _is_identifier(stage_id)
                        or stage_id in seen_stage_ids
                    ):
                        issues.append(Issue(
                            "PED-CHECK-05", number,
                            f"stage id {scene_id!r}/{stage_id!r} must be unique and nonempty",
                        ))
                    else:
                        seen_stage_ids.add(stage_id)
                    effective_route = stage.get("route", scene_route)
                    if (
                        isinstance(effective_route, str)
                        and effective_route in expected_route_ids
                        and effective_route != scene_route
                        and _is_identifier(scene_id)
                        and _is_identifier(stage_id)
                    ):
                        expected_route_ids[effective_route].append(
                            f"{scene_id}/{stage_id}"
                        )
            declared_routes = route_manifest
            if set(declared_routes) != set(ROUTE_FIELDS):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    "routes must declare exactly LIVE, REQUIRED, and OPTIONAL",
                ))
            for route in ROUTE_FIELDS:
                if declared_routes.get(route) != expected_route_ids[route]:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"routes.{route} does not match scene.route and effective stage routes; "
                        f"expected {expected_route_ids[route]}",
                    ))
            for scene in scenes:
                scene_route = scene.get("route")
                if (
                    not isinstance(scene_route, str)
                    or scene_route not in {"REQUIRED", "OPTIONAL"}
                ):
                    continue
                mixed_stages = [
                    stage.get("id")
                    for stage in _object_list(scene.get("stages", []))
                    if stage.get("route", scene_route) != scene_route
                ]
                if mixed_stages:
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"autonomous scene {scene.get('id')!r} mixes effective stage "
                        f"routes at {mixed_stages}; split the scene so its duration can be "
                        "accounted without overlap",
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
            route_is_mandatory = (
                isinstance(route, str) and route in mandatory_routes
            )
            dom_id = scene.get("dom_id")
            if not isinstance(dom_id, str) or dom_id not in dom_ids:
                issues.append(Issue(
                    "PED-CHECK-03", number,
                    f"scene {scene.get('id')} points to missing #{scene.get('dom_id')}",
                ))
            if (
                not isinstance(route, str)
                or route not in routes
                or not isinstance(scene.get("type"), str)
                or scene.get("type") not in scene_types
            ):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"scene {scene.get('id')} has invalid route/type",
                ))
            if (
                not scene.get("layout")
                or not scene.get("concepts")
                or not _is_positive_integer(scene.get("duration_minutes"))
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
                elif route_is_mandatory and introduced[1] not in mandatory_routes:
                    issues.append(Issue(
                        "PED-CHECK-06", number,
                        f"scene {scene.get('id')} depends on OPTIONAL concept {concept}",
                    ))
                elif (
                    introduced[0] == number
                    and route_is_mandatory
                    and introduced[1] == "REQUIRED"
                    and route == "LIVE"
                ):
                    issues.append(Issue(
                        "PED-CHECK-06", number,
                        f"LIVE scene {scene.get('id')} uses REQUIRED-only concept {concept}",
                    ))
            for stage in _object_list(scene.get("stages", [])):
                effective_route = stage.get("route", route)
                if not isinstance(effective_route, str) or effective_route not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"stage {scene.get('id')}/{stage.get('id')} has invalid effective route",
                    ))
                if effective_route != route and not _is_positive_integer(
                    stage.get("duration_minutes")
                ):
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"route override {scene.get('id')}/{stage.get('id')} "
                        "needs positive integer duration_minutes",
                    ))
                if effective_route == route and "duration_minutes" in stage:
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"inherited-route stage {scene.get('id')}/{stage.get('id')} "
                        "must use its scene base-route duration",
                    ))
                dom_stage = stage.get("dom_stage")
                if dom_stage is not None and (
                    not _is_integer(dom_stage) or dom_stage not in dom_stages
                ):
                    issues.append(Issue(
                        "PED-CHECK-03", number,
                        f"stage {scene.get('id')}/{stage.get('id')} points to missing data-stage={dom_stage}",
                    ))

        for objective in lesson.get("objectives", []):
            route = objective.get("route")
            route_is_mandatory = (
                isinstance(route, str) and route in mandatory_routes
            )
            if not isinstance(route, str) or route not in routes:
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
                    elif route_is_mandatory and introduced[1] not in mandatory_routes:
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
        if not isinstance(load, dict):
            issues.append(Issue(
                "PED-CHECK-08", number,
                "load must be an object",
            ))
            load = {}
        load_fields = [
            "live_presentation_minutes", "guided_minutes",
            "required_autonomous_minutes", "optional_minutes", "overflow_policy",
        ]
        if delivery == "lesson":
            load_fields.append("autonomous_components")
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
                _is_integer(live)
                and _is_integer(policy.get("minimum"))
                and _is_integer(policy.get("maximum"))
                and policy["minimum"] <= live <= policy["maximum"]
            ):
                issues.append(Issue(
                    "PED-CHECK-08", number,
                    f"LIVE presentation is {live}; expected {policy.get('minimum')}–{policy.get('maximum')}",
                ))
            live_scene_minutes = sum(
                state["minutes"]
                for state in _timed_scene_states(lesson)
                if state.get("route") == "LIVE"
                and _is_positive_integer(state.get("minutes"))
            )
            if not _is_integer(live) or live != live_scene_minutes:
                issues.append(Issue(
                    "PED-CHECK-08", number,
                    f"LIVE scene durations total {live_scene_minutes}, "
                    f"live_presentation_minutes is {live}; exact equality is required",
                ))

    # Explicit notebook exercise classification and complete autonomous load.
    guided = graph.get("load_policy", {}).get("guided_practice_minutes", {})
    autonomous_policy = graph.get("load_policy", {}).get("autonomous_components", {})
    mixed_duration_policy = graph.get("load_policy", {}).get("mixed_route_duration", {})
    if mixed_duration_policy != {
        "scene_duration_scope": "scene_route",
        "override_duration_scope": "effective_stage_route",
        "aggregation": "additive",
        "autonomous_component_role": "exact_mirror",
    }:
        issues.append(Issue(
            "PED-CHECK-08", None,
            "load policy must define additive base-scene and route-override duration semantics",
        ))
    if autonomous_policy != {
        "kinds": ["document", "exercise", "quiz", "project"],
        "overlap_rule": "same overlap_id means the same timed activity; equal minutes count once",
        "default": "additive",
    }:
        issues.append(Issue(
            "PED-CHECK-08", None,
            "load policy must define document/exercise/quiz/project components and explicit overlap semantics",
        ))
    for number, kinds in exercise_lesson_items:
        notebooks = _resolve_lesson_notebooks(root, number)
        all_declared: list[str] = []
        route_minutes = {route: 0 for route in ("LIVE", "REQUIRED", "OPTIONAL")}
        exercise_components: list[dict[str, Any]] = []
        for kind in ("build", "aux"):
            raw_items = kinds.get(kind)
            if not isinstance(raw_items, list):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"exercise routes miss {kind}",
                ))
                continue
            if any(not isinstance(item, dict) for item in raw_items):
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"{kind} exercise routes must contain only objects",
                ))
            items = _object_list(raw_items)
            titles = [item.get("title") for item in items]
            all_declared.extend(titles)
            invalid_titles = [title for title in titles if not _is_identifier(title)]
            if invalid_titles:
                issues.append(Issue(
                    "PED-CHECK-05", number,
                    f"{kind} exercise titles must be nonempty strings",
                ))
            valid_titles = [title for title in titles if _is_identifier(title)]
            if len(valid_titles) != len(set(valid_titles)):
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
                if not isinstance(route, str) or route not in routes:
                    issues.append(Issue(
                        "PED-CHECK-05", number,
                        f"exercise {item.get('title')!r} has invalid route",
                    ))
                if not _is_positive_integer(minutes):
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"exercise {item.get('title')!r} has no positive load",
                    ))
                elif isinstance(route, str) and route in route_minutes:
                    route_minutes[route] += minutes
                    if route in {"REQUIRED", "OPTIONAL"}:
                        exercise_components.append({
                            "id": f"{kind}:{item.get('title')}",
                            "kind": "exercise",
                            "route": route,
                            "minutes": minutes,
                            "overlap_id": item.get("overlap_id"),
                        })
                overlap_id = item.get("overlap_id")
                if overlap_id is not None and not _is_overlap_id(overlap_id):
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"exercise {item.get('title')!r} has invalid overlap_id",
                    ))
        valid_declared = [title for title in all_declared if _is_identifier(title)]
        if len(valid_declared) != len(set(valid_declared)):
            issues.append(Issue(
                "PED-CHECK-05", number,
                "an exercise appears in both build and aux classifications",
            ))
        minimum = guided.get("minimum")
        maximum = guided.get("maximum")
        delta = guided.get("allowed_delta_from_declared")
        lesson_load = by_number.get(number, {}).get("load", {})
        if not isinstance(lesson_load, dict):
            lesson_load = {}
        live_minutes = route_minutes["LIVE"]
        declared = lesson_load.get("guided_minutes")
        if not (
            _is_integer(minimum)
            and _is_integer(maximum)
            and minimum <= live_minutes <= maximum
        ):
            issues.append(Issue(
                "PED-CHECK-08", number,
                f"LIVE exercises total {live_minutes}; expected {minimum}–{maximum}",
            ))
        if not _is_integer(declared) or not _is_integer(delta):
            issues.append(Issue(
                "PED-CHECK-08", number,
                "guided_minutes and allowed delta must be integers",
            ))
        elif abs(live_minutes - declared) > delta:
            issues.append(Issue(
                "PED-CHECK-08", number,
                f"LIVE exercises total {live_minutes}, guided_minutes is {declared}, allowed delta {delta}",
            ))
        if "required_project_minutes" in lesson_load:
            issues.append(Issue(
                "PED-CHECK-08", number,
                "required_project_minutes is legacy; declare a project component instead",
            ))

        expected_scene_components = _autonomous_scene_contract(by_number[number])
        component_contract = lesson_load.get("autonomous_components")
        declared_components: list[dict[str, Any]] = []
        if not isinstance(component_contract, dict) or set(component_contract) != {
            "documents", "quizzes", "projects"
        }:
            issues.append(Issue(
                "PED-CHECK-08", number,
                "autonomous_components must declare exactly documents, quizzes, and projects",
            ))
            component_contract = {}
        declared_ids: set[str] = set()
        declared_scene_ids: set[str] = set()
        for field, kind_name in (
            ("documents", "document"),
            ("quizzes", "quiz"),
            ("projects", "project"),
        ):
            values = component_contract.get(field, [])
            if not isinstance(values, list):
                issues.append(Issue(
                    "PED-CHECK-08", number,
                    f"autonomous_components.{field} must be a list",
                ))
                continue
            for item in values:
                if not isinstance(item, dict):
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"autonomous_components.{field} contains a non-object",
                    ))
                    continue
                item_id = item.get("id")
                route = item.get("route")
                minutes = item.get("minutes")
                if not _is_identifier(item_id) or item_id in declared_ids:
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"autonomous component id {item_id!r} must be unique and nonempty",
                    ))
                else:
                    declared_ids.add(item_id)
                if (
                    not isinstance(route, str)
                    or route not in {"REQUIRED", "OPTIONAL"}
                ):
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"autonomous component {item_id!r} has invalid route {route!r}",
                    ))
                if not _is_positive_integer(minutes):
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"autonomous component {item_id!r} needs positive integer minutes",
                    ))
                overlap_id = item.get("overlap_id")
                if overlap_id is not None and not _is_overlap_id(overlap_id):
                    issues.append(Issue(
                        "PED-CHECK-08", number,
                        f"autonomous component {item_id!r} has invalid overlap_id",
                    ))
                normalized = dict(item)
                normalized["kind"] = kind_name
                declared_components.append(normalized)
                if kind_name != "project" and isinstance(item_id, str):
                    declared_scene_ids.add(item_id)
                    expected = expected_scene_components.get(item_id)
                    if expected is None:
                        issues.append(Issue(
                            "PED-CHECK-08", number,
                            f"{kind_name} component {item_id!r} has no REQUIRED/OPTIONAL scene state",
                        ))
                    else:
                        if expected["kind"] != kind_name or expected["route"] != route:
                            issues.append(Issue(
                                "PED-CHECK-08", number,
                                f"component {item_id!r} disagrees with its scene kind/effective route",
                            ))
                        if expected["minutes"] is not None and expected["minutes"] != minutes:
                            issues.append(Issue(
                                "PED-CHECK-08", number,
                                f"component {item_id!r} must use canonical state duration {expected['minutes']}",
                            ))
        missing_scene_components = sorted(
            set(expected_scene_components) - declared_scene_ids
        )
        if missing_scene_components:
            issues.append(Issue(
                "PED-CHECK-08", number,
                f"autonomous load ignores REQUIRED/OPTIONAL scene states {missing_scene_components}",
            ))

        all_components = exercise_components + declared_components
        for message in _overlap_contract_errors(all_components):
            issues.append(Issue("PED-CHECK-08", number, message))
        for route, field in (
            ("REQUIRED", "required_autonomous_minutes"),
            ("OPTIONAL", "optional_minutes"),
        ):
            actual = _component_total(all_components, route)
            declared = lesson_load.get(field)
            if not _is_integer(declared) or declared != actual:
                breakdown = {
                    kind_name: sum(
                        item["minutes"]
                        for item in all_components
                        if item.get("route") == route and item.get("kind") == kind_name
                        and _is_positive_integer(item.get("minutes"))
                    )
                    for kind_name in ("document", "exercise", "quiz", "project")
                }
                issues.append(Issue(
                    "PED-CHECK-08", number,
                    f"{route} autonomous total {actual} from {breakdown}, "
                    f"{field} is {declared}; exact equality is required",
                ))

    # Assessment traceability and OPTIONAL exclusion.
    required_item_keys = {
        "id", "lesson", "objective", "concept", "cognitive_level", "difficulty",
    }
    item_ids: set[str] = set()
    item_objective_pairs: list[tuple[object, object]] = []
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
        item_objective_pairs.append((number, item["objective"]))
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
        declared_objectives = entry.get("objectives", [])
        declared_ids = [objective.get("id") for objective in declared_objectives]
        expected_ids = {
            objective_id
            for objective_id, (owner, route, _refs) in objectives.items()
            if owner == number and route in blueprint.get("allowed_routes", [])
        }
        if len(declared_ids) != len(set(declared_ids)):
            issues.append(Issue(
                "PED-CHECK-07", number,
                "assessment blueprint contains duplicate objectives",
            ))
        if set(declared_ids) != expected_ids:
            issues.append(Issue(
                "PED-CHECK-07", number,
                "assessment blueprint objectives do not exactly cover every "
                f"LIVE/REQUIRED objective: declared={sorted(set(declared_ids), key=repr)}, "
                f"expected={sorted(expected_ids)}",
            ))
        for objective in declared_objectives:
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
            elif objective.get("assessed") is not True:
                issues.append(Issue(
                    "PED-CHECK-07", number,
                    f"blueprint objective {objective.get('id')} must be explicitly assessed",
                ))
    if blueprint_lessons != number_set:
        issues.append(Issue(
            "PED-CHECK-07", None,
            f"assessment blueprint covers lessons {sorted(blueprint_lessons)}, expected L1-L15",
        ))
    expected_item_pairs = {
        (entry.get("lesson"), objective.get("id"))
        for entry in blueprint.get("lesson_blueprints", [])
        for objective in entry.get("objectives", [])
        if objective.get("assessed") is True
    }
    item_pair_counts = {
        pair: item_objective_pairs.count(pair) for pair in set(item_objective_pairs)
    }
    if (set(item_objective_pairs) != expected_item_pairs
            or any(count != 1 for count in item_pair_counts.values())):
        issues.append(Issue(
            "PED-CHECK-07", None,
            "assessment trace items must cover every assessed objective exactly once",
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
            missing = [
                key for key in ("path", "symbol", "api", "kind", "returns")
                if key not in check
            ]
            if check.get("kind") == "function" and "parameters" not in check:
                missing.append("parameters")
            if missing:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"symbol binding misses {sorted(set(missing))}",
                ))
                continue
            path = root / check["path"]
            if not path.exists():
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"missing starter package {path}",
                ))
                continue
            api_id = check["api"]
            if api_id in bound:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"API {api_id} has duplicate AST bindings",
                ))
            bound.add(api_id)
            try:
                actual = _module_symbol_surface(path, check["symbol"])
            except (OSError, SyntaxError, UnicodeError) as exc:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"cannot parse starter symbol source {check['path']}: {exc}",
                ))
                continue
            if check["kind"] == "function":
                expected = {
                    "kind": "function",
                    "parameters": check["parameters"],
                    "source_returns": check.get("source_returns"),
                }
                render_parameters = check["parameters"]
            else:
                expected = {"kind": check["kind"], "returns": check["returns"]}
                render_parameters = []
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
                canonical["name"], check["kind"], render_parameters,
                check.get("source_returns") or check["returns"],
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
            try:
                actual = _class_member_surfaces(path, check["class"])
            except (OSError, SyntaxError, UnicodeError) as exc:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"cannot parse starter package {check['path']}: {exc}",
                ))
                continue
            if not actual:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"missing class {check['class']} in {check['path']}",
                ))
                continue
            if "bases" in check and actual.get("__class__", {}).get("bases") != check["bases"]:
                issues.append(Issue(
                    "PED-CHECK-09", number,
                    f"{check['class']} bases are "
                    f"{actual.get('__class__', {}).get('bases')!r}, expected {check['bases']!r}",
                ))
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
                if "abstract" in expected:
                    expected_member["abstract"] = expected["abstract"]
                actual_contract = (
                    {
                        key: actual_member.get(key)
                        for key in expected_member
                    }
                    if isinstance(actual_member, dict)
                    else actual_member
                )
                if actual_contract != expected_member:
                    issues.append(Issue(
                        "PED-CHECK-09", number,
                        f"{check['class']}.{member} is {actual_contract!r}, expected {expected_member!r}",
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
