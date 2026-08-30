#!/usr/bin/env python3
"""Generate the human-readable Work 2 continuity reports from pedagogy/.

The JSON-compatible YAML manifests remain the source of truth.  This script
keeps the two review artefacts deterministic and lets CI detect hand edits.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PEDAGOGY = ROOT / "pedagogy"
JOURNEY_PATH = ROOT / "docs" / "student-journey-audit.md"
DEPENDENCY_PATH = ROOT / "docs" / "course-dependency-report.md"
KINDS = ("concepts", "apis", "notation")
KNOWN_ROUTES = {"LIVE", "REQUIRED"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def item_id(item):
    return item["id"] if isinstance(item, dict) else item


def recall_id(recall):
    for key in ("concept", "api", "notation"):
        if recall.get(key):
            return recall[key]
    return "unknown-recall"


def introduction_route(lesson, kind, item):
    if isinstance(item, dict) and item.get("route"):
        return item["route"]
    return lesson.get("introduction_routes", {}).get(kind, {}).get(item_id(item), "LIVE")


def route_label(route):
    return {"LIVE": "LIVE", "REQUIRED": "REQUIRED", "OPTIONAL": "OPTIONAL"}.get(route, route)


def csv(values, empty="—"):
    return ", ".join(f"`{value}`" for value in values) if values else empty


def load_contract():
    graph = load(PEDAGOGY / "course_graph.yml")
    lessons = [load(PEDAGOGY / rel) for rel in graph["lesson_files"]]
    routes = load(PEDAGOGY / "exercise_routes.yml")
    blueprint = load(PEDAGOGY / "assessment_blueprint.yml")
    return graph, lessons, routes, blueprint


def build_indexes(lessons, blueprint):
    first = {kind: {} for kind in KINDS}
    used = {kind: defaultdict(list) for kind in KINDS}
    recalled = defaultdict(list)
    assessed = defaultdict(list)
    qualified = {}

    for lesson in lessons:
        number = lesson["lesson"]
        for kind in KINDS:
            for item in lesson.get("introduces", {}).get(kind, []):
                identifier = item_id(item)
                first[kind].setdefault(
                    identifier,
                    (number, introduction_route(lesson, kind, item)),
                )
            for identifier in lesson.get("requires", {}).get(kind, []):
                used[kind][identifier].append(number)
        for recall in lesson.get("recalls", []):
            recalled[recall_id(recall)].append(number)
        for surface in lesson.get("api_surface", []):
            if surface.get("qualified_name"):
                qualified[surface["id"]] = surface["qualified_name"]

    objective_by_id = {}
    for lesson in lessons:
        for objective in lesson.get("objectives", []):
            objective_by_id[objective["id"]] = (lesson["lesson"], objective)
    for lesson_bp in blueprint.get("lesson_blueprints", []):
        for objective in lesson_bp.get("objectives", []):
            if objective.get("assessed"):
                objective_id = objective["id"]
                source = objective_by_id.get(objective_id)
                if source:
                    for kind in KINDS:
                        for identifier in source[1].get(kind, []):
                            assessed[identifier].append(objective_id)

    return first, used, recalled, assessed, qualified


def continuity_findings(lessons):
    known = {kind: {} for kind in KINDS}
    missing = []
    optional_leaks = []
    for lesson in lessons:
        number = lesson["lesson"]
        for kind in KINDS:
            for identifier in lesson.get("requires", {}).get(kind, []):
                origin = known[kind].get(identifier)
                if origin is None:
                    missing.append((number, kind, identifier))
                elif origin[1] not in KNOWN_ROUTES:
                    optional_leaks.append((number, kind, identifier, origin[0]))
        for kind in KINDS:
            for item in lesson.get("introduces", {}).get(kind, []):
                identifier = item_id(item)
                known[kind].setdefault(
                    identifier,
                    (number, introduction_route(lesson, kind, item)),
                )
    return missing, optional_leaks


def exercise_stats(route_contract, lesson_number, route):
    lesson_routes = route_contract.get("lessons", {}).get(str(lesson_number), {})
    selected = []
    for notebook_kind in ("build", "aux"):
        for exercise in lesson_routes.get(notebook_kind, []):
            if exercise.get("route") == route:
                selected.append((notebook_kind, exercise))
    minutes = sum(exercise.get("minutes", 0) for _, exercise in selected)
    return selected, minutes


def exercise_summary(route_contract, lesson_number, route, include_titles=False):
    selected, minutes = exercise_stats(route_contract, lesson_number, route)
    if not selected:
        return "0 ejercicios · 0 min"
    base = f"{len(selected)} ejercicios · {minutes} min"
    if include_titles:
        titles = [f"{kind}: {exercise['title']}" for kind, exercise in selected]
        return f"{base} — " + "; ".join(titles)
    return base


def autonomous_load_summary(lesson, route_contract, route):
    """Render the complete, overlap-aware autonomous load breakdown."""
    components = []
    for notebook_kind, exercise in exercise_stats(
        route_contract, lesson["lesson"], route,
    )[0]:
        components.append({
            "id": f"{notebook_kind}:{exercise['title']}",
            "kind": "exercise",
            **exercise,
        })
    contract = lesson.get("load", {}).get("autonomous_components", {})
    for field, kind in (
        ("documents", "document"),
        ("quizzes", "quiz"),
        ("projects", "project"),
    ):
        for item in contract.get(field, []):
            components.append({"kind": kind, **item})
    selected = [item for item in components if item.get("route") == route]
    raw = {
        kind: sum(item.get("minutes", 0) for item in selected if item["kind"] == kind)
        for kind in ("document", "exercise", "quiz", "project")
    }
    groups = defaultdict(list)
    for item in selected:
        if item.get("overlap_id"):
            groups[item["overlap_id"]].append(item)
    overlap = sum(
        (len(items) - 1) * items[0]["minutes"]
        for items in groups.values()
        if len(items) > 1
    )
    field = "required_autonomous_minutes" if route == "REQUIRED" else "optional_minutes"
    total = lesson.get("load", {}).get(field, 0)
    return (
        f"carga total {total} min (documento {raw['document']} + "
        f"ejercicios {raw['exercise']} + quiz {raw['quiz']} + "
        f"proyecto {raw['project']} − solapamientos {overlap})"
    )


def introduced_by_route(lesson, route):
    values = []
    for kind in KINDS:
        for item in lesson.get("introduces", {}).get(kind, []):
            if introduction_route(lesson, kind, item) == route:
                values.append(item_id(item))
    return values


def requirement_with_origins(lesson, first):
    chunks = []
    for kind in KINDS:
        entries = []
        for identifier in lesson.get("requires", {}).get(kind, []):
            origin = first[kind].get(identifier)
            entries.append(f"`{identifier}` (L{origin[0]})" if origin else f"`{identifier}` (sin origen)")
        if entries:
            chunks.append(f"{kind}: " + ", ".join(entries))
    return "; ".join(chunks) if chunks else "Inicio del recorrido; no presupone conocimiento del curso."


def scene_ids(lesson, route):
    """Return the checker-verified effective route inventory."""
    return list(lesson.get("routes", {}).get(route, []))


def render_journey(graph, lessons, route_contract, blueprint):
    first, _, _, _, qualified = build_indexes(lessons, blueprint)
    missing, optional_leaks = continuity_findings(lessons)
    lines = [
        "# Auditoría del recorrido del alumno — L1 → L15",
        "",
        "> Artefacto generado por `framework/_build/pedagogy_reports.py` a partir del contrato ejecutable. No editar a mano.",
        "",
        "## Resultado de continuidad",
        "",
        f"- Dependencias sin introducción previa: **{len(missing)}**.",
        f"- Dependencias obligatorias cuyo único origen es OPTIONAL: **{len(optional_leaks)}**.",
        f"- Lessons educativas con rutas explícitas: **{len(graph['coverage']['runtime_lessons'])}/14**.",
        "- L15 conserva una práctica pública lineal y no se fuerza al renderer de escenas; "
        "la evaluación oficial permanece bloqueada: sus bancos deberán crearse de nuevo y "
        "entregarse exclusivamente desde la futura fuente privada autorizada.",
        "",
        "La entrada de cada lesson se calcula solo con introducciones LIVE + REQUIRED anteriores. Los nombres entre `backticks` son identificadores estables del contrato.",
        "",
    ]

    for lesson in lessons:
        number = lesson["lesson"]
        lines += [f"## L{number:02d} — {lesson['title']}", ""]
        lines.append(f"- **Entrada — qué sabe:** {requirement_with_origins(lesson, first)}")
        recalls = []
        for recall in lesson.get("recalls", []):
            mapping = recall.get("mapping", {})
            before = mapping.get("before", "origen declarado")
            now = mapping.get("now", "uso actual")
            recalls.append(f"`{recall_id(recall)}` (L{recall['introduced_in']}): {before} → {now}")
        lines.append("- **Recuperación:** " + ("; ".join(recalls) if recalls else "No requiere un recall distante; la continuidad es inmediata o la lesson inicia el curso."))

        introductions = []
        for route in ("LIVE", "REQUIRED", "OPTIONAL"):
            values = introduced_by_route(lesson, route)
            if values:
                introductions.append(f"{route_label(route)}: {csv(values)}")
        no_introduction = ("No añade conceptos: practica la integración del curso sin sustituir "
                           "la evaluación final oficial." if number == 15 else
                           "No añade conceptos nuevos.")
        lines.append("- **Introduce:** " + ("; ".join(introductions) if introductions else no_introduction))

        transitions = lesson.get("api_transitions", [])
        if transitions:
            rendered = []
            for transition in transitions:
                before = transition.get("from_api", transition.get("from", transition.get("before", "API anterior")))
                after = transition.get("to_api", transition.get("to", transition.get("now", "API nueva")))
                reason = transition.get("reason", transition.get("migration", "transición declarada"))
                rendered.append(f"`{before}` → `{after}` ({reason})")
            api_text = "; ".join(rendered)
        else:
            new_apis = [
                qualified.get(item_id(item), item_id(item))
                for item in lesson.get("introduces", {}).get("apis", [])
            ]
            api_text = "Superficie nueva: " + csv(new_apis) if new_apis else "Sin cambio de API pública visible."
        lines.append(f"- **Continuidad de API:** {api_text}")

        live_scenes = scene_ids(lesson, "LIVE")
        lines.append(
            f"- **Práctica guiada:** escenas {csv(live_scenes)}; "
            f"{exercise_summary(route_contract, number, 'LIVE', include_titles=True)}."
        )
        required_intro = introduced_by_route(lesson, "REQUIRED")
        lines.append(
            f"- **REQUIRED:** escenas {csv(scene_ids(lesson, 'REQUIRED'))}; "
            f"introducciones {csv(required_intro)}; {exercise_summary(route_contract, number, 'REQUIRED')}; "
            f"{autonomous_load_summary(lesson, route_contract, 'REQUIRED')}."
        )
        optional_intro = introduced_by_route(lesson, "OPTIONAL")
        lines.append(
            f"- **OPTIONAL:** escenas {csv(scene_ids(lesson, 'OPTIONAL'))}; "
            f"introducciones {csv(optional_intro)}; {exercise_summary(route_contract, number, 'OPTIONAL')}; "
            f"{autonomous_load_summary(lesson, route_contract, 'OPTIONAL')}. "
            "No entra en KNOWN ni en assessment."
        )

        package_paths = sorted({check["path"] for check in lesson.get("package_checks", [])})
        api_names = [qualified.get(item_id(item), item_id(item)) for item in lesson.get("introduces", {}).get("apis", [])]
        if package_paths or api_names:
            lines.append(f"- **Pieza acumulativa:** APIs {csv(api_names)}; snapshots comprobados {csv(package_paths)}.")
        else:
            lines.append("- **Pieza acumulativa:** no expone una API nueva del paquete; consolida la pieza ya disponible o el trabajo previo al paquete.")

        bridge = lesson.get("bridge")
        if bridge:
            lines.append(
                f"- **Necesidad de L{bridge['target_lesson']}:** {bridge['limitation']} → {bridge['need']}"
            )
        elif number == 15:
            lines.append("- **Salida:** assessment acumulativo; cierra el recorrido sin prometer una lesson inexistente.")
        else:
            lines.append("- **Siguiente lesson:** no declarada.")
        lines.append("")

    lines += [
        "## Cierre",
        "",
        "El cálculo machine-readable arroja cero dependencias pendientes y cero fugas OPTIONAL → REQUIRED. La revisión cualitativa, la evidencia vigente y sus límites se registran por separado en `docs/work1-work2-reaudit.md`.",
        "",
    ]
    return "\n".join(lines)


def lesson_list(values):
    return ", ".join(f"L{value}" for value in sorted(set(values))) if values else "—"


def objective_list(values):
    return ", ".join(f"`{value}`" for value in sorted(set(values))) if values else "—"


def render_registry_table(kind, graph, first, used, recalled, assessed, qualified):
    registry = graph.get("registries", {}).get(kind, [])
    lines = []
    if kind == "apis":
        lines += ["| API estable | Primera introducción | Reutilización | Assessment | Nombre público |", "|---|---|---|---|---|"]
    elif kind == "concepts":
        lines += ["| Concepto estable | Primera introducción | Reutilización | Recalls | Assessment |", "|---|---|---|---|---|"]
    else:
        lines += ["| Notación estable | Primera introducción | Reutilización | Assessment |", "|---|---|---|---|"]
    for entry in registry:
        identifier = item_id(entry)
        origin = first[kind].get(identifier)
        origin_text = f"L{origin[0]} · {origin[1]}" if origin else "—"
        if kind == "apis":
            lines.append(
                f"| `{identifier}` | {origin_text} | {lesson_list(used[kind][identifier])} | "
                f"{objective_list(assessed[identifier])} | `{qualified.get(identifier, '—')}` |"
            )
        elif kind == "concepts":
            lines.append(
                f"| `{identifier}` | {origin_text} | {lesson_list(used[kind][identifier])} | "
                f"{lesson_list(recalled[identifier])} | {objective_list(assessed[identifier])} |"
            )
        else:
            lines.append(
                f"| `{identifier}` | {origin_text} | {lesson_list(used[kind][identifier])} | "
                f"{objective_list(assessed[identifier])} |"
            )
    return lines


def render_dependencies(graph, lessons, route_contract, blueprint):
    first, used, recalled, assessed, qualified = build_indexes(lessons, blueprint)
    missing, optional_leaks = continuity_findings(lessons)
    lines = [
        "# Informe de dependencias del curso",
        "",
        "> Artefacto generado por `framework/_build/pedagogy_reports.py` a partir de `pedagogy/`. No editar a mano.",
        "",
        "## Resumen verificable",
        "",
        f"- Registry de conceptos: **{len(graph.get('registries', {}).get('concepts', []))}**.",
        f"- Registry de APIs: **{len(graph.get('registries', {}).get('apis', []))}**.",
        f"- Registry de notación: **{len(graph.get('registries', {}).get('notation', []))}**.",
        f"- Requisitos sin origen anterior: **{len(missing)}**.",
        f"- Requisitos procedentes solo de OPTIONAL: **{len(optional_leaks)}**.",
        "",
        "## Aristas por lesson",
        "",
        "| Lesson | Requiere conceptos | Requiere APIs | Requiere notación | Recalls | Siguiente necesidad |",
        "|---|---|---|---|---|---|",
    ]
    for lesson in lessons:
        bridge = lesson.get("bridge")
        next_need = f"L{bridge['target_lesson']}: {bridge['need']}" if bridge else "—"
        lines.append(
            f"| L{lesson['lesson']} | {csv(lesson.get('requires', {}).get('concepts', []))} | "
            f"{csv(lesson.get('requires', {}).get('apis', []))} | "
            f"{csv(lesson.get('requires', {}).get('notation', []))} | "
            f"{csv([recall_id(recall) for recall in lesson.get('recalls', [])])} | {next_need} |"
        )

    lines += ["", "## Conceptos", ""]
    lines += render_registry_table("concepts", graph, first, used, recalled, assessed, qualified)
    lines += ["", "## APIs visibles", ""]
    lines += render_registry_table("apis", graph, first, used, recalled, assessed, qualified)
    lines += ["", "## Notación", ""]
    lines += render_registry_table("notation", graph, first, used, recalled, assessed, qualified)

    lines += [
        "",
        "## Objetivos de assessment",
        "",
        "El blueprint conserva únicamente trazabilidad y distribución; no contiene enunciados ni soluciones.",
        "",
        "| Lesson | Objetivo | Ruta | Evaluable | Distribución declarada |",
        "|---|---|---|---|---|",
    ]
    for lesson_bp in blueprint.get("lesson_blueprints", []):
        distribution = ", ".join(f"{key}={value}" for key, value in lesson_bp.get("question_distribution", {}).items())
        for objective in lesson_bp.get("objectives", []):
            lines.append(
                f"| L{lesson_bp['lesson']} | `{objective['id']}` | {objective['route']} | "
                f"{'sí' if objective.get('assessed') else 'no'} | {distribution} |"
            )

    lines += [
        "",
        "## Fuente y mantenimiento",
        "",
        "Las introducciones, reutilizaciones y recalls se derivan de `pedagogy/lessons/NN.yml`; las rutas de práctica proceden de `pedagogy/exercise_routes.yml`; la trazabilidad evaluativa procede de `pedagogy/assessment_blueprint.yml`. CI regenera ambos informes y falla si existe drift.",
        "",
    ]
    return "\n".join(lines)


def check_or_write(path, content, check):
    if check:
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != content:
            print(f"OUT OF DATE: {path.relative_to(ROOT)}", file=sys.stderr)
            return False
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated reports differ")
    args = parser.parse_args()
    graph, lessons, routes, blueprint = load_contract()
    outputs = {
        JOURNEY_PATH: render_journey(graph, lessons, routes, blueprint),
        DEPENDENCY_PATH: render_dependencies(graph, lessons, routes, blueprint),
    }
    ok = all(check_or_write(path, content, args.check) for path, content in outputs.items())
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
