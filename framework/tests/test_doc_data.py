"""Regresión de los data-builders de los docs: claves y sanidad de los números
que se embeben en las páginas. Si el motor o el CSV cambian y esto pasa, los
documentos siguen contando la verdad."""

import importlib.util
from html import unescape
import json
import os
from pathlib import Path
import re
import sys

import pytest

HERE = os.path.dirname(__file__)
DOCS = os.path.join(HERE, "..", "_build", "docs")
ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK = ROOT / "framework"


FALSE_PROVENANCE_PATTERNS = {
    "snapshot real/histórico": re.compile(
        r"\bsnapshots?\s+(?:real(?:es)?|hist[oó]ric[oa]s?|de\s+verdad)\b"
    ),
    "fila/dato/CSV real": re.compile(
        r"\b(?:filas?|datos?|csv)\s+real(?:es)?\b"
    ),
    "libro/mercado/día/volumen real": re.compile(
        r"\b(?:libro|mercado|d[ií]a|volumen)\s+real(?:es)?\b"
    ),
    "replay real/histórico": re.compile(
        r"\breplay\s+(?:real|hist[oó]ric[oa])\b"
    ),
    "500 reales/de verdad": re.compile(
        r"\b500(?:\s+snapshots?)?\s+(?:real(?:es)?|de\s+verdad)\b"
    ),
    "fills/ejecuciones/números reales": re.compile(
        r"\b(?:fills?|ejecuciones?|n[uú]meros?)\s+real(?:es)?\b"
    ),
}

EXPECTED_KEYS = {
    7: {"raw", "snaps", "mids", "imbs", "signalUps", "signalTotal", "mid0",
        "depthBid3", "depthAsk3"},
    8: {"bids", "asks", "mid", "sweeps", "variants", "big", "limPx", "sizes",
        "limitPrices", "scenarios", "fokBug"},
    9: {"anatomy", "equity", "fills", "filled", "steps", "finalEquity"},
    10: {"buyonce", "imbalance"},
    11: {"signal", "monos", "monoFinals", "arrivalMid", "avgSlip", "nSlips"},
    12: {"total", "mid0", "sweepAvg", "twapAvg", "vwapAvg", "bars"},
    13: {"skew", "noskew"},
    14: {"naive", "as", "sweep", "sigmaHorizon", "kappa", "horizon"},
}


def load(n):
    spec = importlib.util.spec_from_file_location(
        f"d{n}", os.path.join(DOCS, f"{n:02d}_data.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build()


@pytest.fixture(scope="module")
def data():
    return {n: load(n) for n in EXPECTED_KEYS}


def test_builders_expose_expected_keys(data):
    for n, keys in EXPECTED_KEYS.items():
        assert keys <= set(data[n]), f"doc {n}: faltan claves {keys - set(data[n])}"


def test_l7_series_aligned(data):
    d = data[7]
    assert len(d["mids"]) == len(d["imbs"]) == len(d["snaps"]) == 500
    assert len(d["raw"]) == 3
    assert d["depthBid3"] > 0 and d["depthAsk3"] > 0
    assert 0 < d["signalUps"] <= d["signalTotal"]


def test_l8_slippage_monotone_with_size(data):
    slips = [s["slip"] for s in data[8]["sweeps"]]
    assert slips == sorted(slips), "más tamaño nunca puede dar menos slippage"
    assert data[8]["variants"]["fok"]["nfills"] == 0


def test_l8_scenarios_preserve_order_type_invariants(data):
    scenarios = data[8]["scenarios"]
    assert len(scenarios) == 60
    for scenario in scenarios:
        if scenario["type"] == "fok" and not scenario["fills"]:
            assert scenario["after"] == scenario["before"], "FOK fallida debe ser atómica"
        if scenario["type"] in {"market", "ioc", "fok"}:
            # Ninguno de estos modos crea liquidez nueva en el lado de la orden.
            before_levels = sum(len(v) for v in scenario["before"].values())
            after_levels = sum(len(v) for v in scenario["after"].values())
            assert after_levels <= before_levels


def test_l8_fok_counterexample_motivates_plan_before_commit(data):
    bug = data[8]["fokBug"]
    assert bug["remaining"] > 0
    assert bug["canonicalAfter"] == bug["before"], "la FOK real debe abortar sin mutar"
    assert bug["naiveAfter"] != bug["before"], "el contraejemplo debe exhibir la mutación parcial"


def test_l9_fills_complete_and_marked(data):
    d = data[9]
    assert len(d["anatomy"]) == 4
    assert [x["i"] for x in d["anatomy"]] == [0, 1, 2, 3]
    assert d["filled"] == pytest.approx(0.5, abs=1e-6)
    assert all(0 <= f["i"] < len(d["equity"]) for f in d["fills"])


def test_l12_sweep_worse_than_sliced(data):
    d = data[12]
    assert d["sweepAvg"] < d["twapAvg"] and d["sweepAvg"] < d["vwapAvg"], \
        "vender de golpe debe salir peor que troceado en este dataset"
    assert sum(d["bars"]) == pytest.approx(1.0, abs=1e-3)


def test_l12_dynamic_prediction_is_honest(data):
    """La actividad del replay es estacionaria: el modelo rolado NO bate a la
    media plana, y ni el volumen-oráculo mueve la ejecución. El doc lo cuenta
    así; si el motor cambiara y esto dejara de ser cierto, hay que reescribirlo."""
    d = data[12]
    assert d["maeRoll"] >= d["maeStatic"], \
        "sin autocorrelación, la media rolada no debe ganar a la media global"
    assert abs(d["oracleVsTwapBps"]) < 2.0, \
        "ni con previsión perfecta del volumen se gana apenas en un paseo aleatorio"
    assert len(d["vol"]) == len(d["staticPred"]) + 1 == len(d["rollPred"]) + 1


def test_l13_skew_tames_inventory(data):
    d = data[13]
    assert d["arrivalIntensity"] == data[14]["arrivalIntensity"] == 520.0
    assert d["skew"]["nFills"] >= 50 and d["noskew"]["nFills"] >= 50, \
        "la comparación necesita suficientes llegadas para ser informativa"
    assert d["skew"]["maxInv"] < d["noskew"]["maxInv"]


def test_l14_gamma_monotone_inventory(data):
    d = data[14]
    inv = [s["maxInv"] for s in d["sweep"]]
    pnl = [s["pnl"] for s in d["sweep"]]
    assert all(a > b for a, b in zip(inv, inv[1:])), \
        "el escenario didáctico debe mostrar control de inventario estricto"
    assert all(a > b for a, b in zip(pnl, pnl[1:])), \
        "el escenario didáctico debe mostrar el coste de ese control"
    assert all(s["nFills"] >= 300 for s in d["sweep"])
    assert d["as"]["finalPnl"] > d["naive"]["finalPnl"]


def _false_provenance_claims(targets):
    violations = []
    for target in targets:
        if not target.is_file():
            continue
        text = target.read_text(encoding="utf-8").lower()
        for line_number, line in enumerate(text.splitlines(), 1):
            for label, pattern in FALSE_PROVENANCE_PATTERNS.items():
                if pattern.search(line):
                    violations.append(
                        f"{target.relative_to(ROOT)}:{line_number}: {label}"
                    )
    return violations


def _canonical_provenance_targets():
    targets = [
        ROOT / "PLAN_MAESTRO_CURSO_TRADING_2026.md",
        ROOT / "CLAUDE.md",
    ]
    targets += list((ROOT / "framework/_build").glob("lessons_*.py"))
    targets += list((ROOT / "framework/_build/docs").glob("*"))
    targets += list((ROOT / "framework/_build/custom").glob("*"))
    targets += list((ROOT / "pedagogy").glob("*.yml"))
    targets += list((ROOT / "pedagogy/lessons").glob("*.yml"))
    return targets


def _generated_provenance_targets():
    targets = [ROOT / "index.html", ROOT / "README.md"]
    for lesson_dir in ROOT.glob("[0-9][0-9]-*"):
        for target in lesson_dir.rglob("*"):
            relative_parts = target.relative_to(lesson_dir).parts
            if "data" in relative_parts:
                continue
            if target.suffix.lower() in {".md", ".html", ".ipynb", ".py", ".js"}:
                targets.append(target)
    return targets


def test_canonical_course_claims_identify_the_replay_as_synthetic():
    """Las fuentes no pueden atribuir provenance empírica al replay sintético."""
    violations = _false_provenance_claims(_canonical_provenance_targets())
    assert not violations, "claims de provenance falsos: " + "; ".join(violations)

    data_contract = (ROOT / "data/README.md").read_text(encoding="utf-8").lower()
    assert "dataset **sintético**" in data_contract
    assert "no datos reales de un" in data_contract
    assert "`fill`" in data_contract and "**simulados**" in data_contract


def test_generated_course_claims_identify_the_replay_as_synthetic():
    """La misma política alcanza HTML, notebooks, guiones y scripts emitidos."""
    violations = _false_provenance_claims(_generated_provenance_targets())
    assert not violations, "claims generados de provenance falsos: " + "; ".join(violations)


def test_l9_required_io_surface_is_explicit_and_directly_exercised():
    spec = (ROOT / "framework/_build/lessons_engine.py").read_text(encoding="utf-8")
    body = (ROOT / "framework/_build/docs/09_body.html").read_text(encoding="utf-8")
    guide = (ROOT / "framework/_build/custom/09_guion.md").read_text(encoding="utf-8")
    lesson = json.loads(
        (ROOT / "pedagogy/lessons/09.yml").read_text(encoding="utf-8")
    )
    blueprint = json.loads(
        (ROOT / "pedagogy/assessment_blueprint.yml").read_text(encoding="utf-8")
    )
    routes = json.loads(
        (ROOT / "pedagogy/exercise_routes.yml").read_text(encoding="utf-8")
    )
    required_titles = {
        item["title"] for item in routes["lessons"]["9"]["build"]
        if item["route"] == "REQUIRED"
    }

    direct_title = "B7 · Carga REQUIRED: from_csv, sample y snapshots"
    assert direct_title in required_titles and direct_title in spec
    for api in ("market.from_csv", "market.sample", "market.snapshots"):
        assert lesson["introduction_routes"]["apis"][api] == "REQUIRED"
    lifecycle = next(
        item for item in lesson["objectives"] if item["id"] == "l09-reset-lifecycle"
    )
    assert lifecycle["route"] == "REQUIRED"
    assessed = next(
        item for item in blueprint["lesson_blueprints"] if item["lesson"] == 9
    )
    assert next(
        item for item in assessed["objectives"]
        if item["id"] == "l09-reset-lifecycle"
    )["assessed"] is True
    for api in ("Market.from_csv", "Market.sample", ".snapshots"):
        assert api in spec
    assert "REQUIRED y evaluable" in body and "REQUIRED y evaluable" in guide
    assert "factories secundarias" not in body
    assert "I/O queda fuera del núcleo" not in body


def test_l10_optional_override_is_not_confused_with_optional_learning():
    body = (ROOT / "framework/_build/docs/10_body.html").read_text(encoding="utf-8")
    theory = (ROOT / "framework/_build/lessons_docs.py").read_text(encoding="utf-8")
    lesson = json.loads(
        (ROOT / "pedagogy/lessons/10.yml").read_text(encoding="utf-8")
    )
    assert "opcionales de <em>sobrescribir</em>" in body
    assert "LIVE" in body and "REQUIRED y evaluable" in body
    assert "opcionales de **sobrescribir**" in theory
    assert "no son profundidad OPTIONAL" in theory
    routes = lesson["introduction_routes"]["apis"]
    assert routes["strategy.on_fill"] == "LIVE"
    assert routes["strategy.on_start"] == routes["strategy.on_end"] == "REQUIRED"


def test_plan_separates_formative_quizzes_from_official_assessment_and_l15():
    plan = (ROOT / "PLAN_MAESTRO_CURSO_TRADING_2026.md").read_text(encoding="utf-8")
    assert "Quiz diagnóstico formativo A/B/C" in plan
    assert "No es el examen continuo oficial" in plan
    assert "10 preguntas A/B/C/D" in plan
    assert "L1–L14 tienen documento interactivo" in plan
    assert "L15 es deliberadamente un assessment lineal" in plan
    assert "VWAPStrategy.run" not in plan
    assert "VWAPStrategy.on_book_update" in plan and "Backtest.run" in plan


def test_golden_source_statuses_match_their_authoritative_role():
    pedagogy = (
        ROOT / "CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md"
    ).read_text(encoding="utf-8")
    architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "**Status:** Authoritative baseline\\" in pedagogy
    assert "**Status:** Authoritative target baseline — migration pending\\" in architecture
    assert "**Status:** Proposed baseline" not in pedagogy + architecture

    pilot = (ROOT / "docs/work1-desktop-pedagogy-pilot.md").read_text(
        encoding="utf-8"
    )
    assert "work1-work2-reaudit.md" in pilot.split("## Estado y alcance", 1)[0]
    assert "work2-full-course-scaleout.md" not in pilot.split(
        "## Estado y alcance", 1
    )[0]


def test_every_interactive_document_embeds_its_emitted_teacher_script():
    for lesson in range(1, 15):
        folder = next(ROOT.glob(f"{lesson:02d}-*"))
        guion = (folder / "presentation/guion.md").read_text(encoding="utf-8")
        documents = list((folder / "presentation").glob("*-doc.html"))
        assert len(documents) == 1, folder
        html = documents[0].read_text(encoding="utf-8")
        assert html.count('id="guion-src"') == 1, documents[0]
        assert guion.replace("</script", "<\\/script") in html, documents[0]


def test_visible_market_loop_uses_the_canonical_fill_api():
    body = (ROOT / "framework/_build/docs/09_body.html").read_text(encoding="utf-8")
    assert "tracker.apply_fill(fill)" in body
    assert "tracker.apply(fills)" not in body


def test_presentations_do_not_claim_to_execute_python_in_browser():
    plan = (ROOT / "PLAN_MAESTRO_CURSO_TRADING_2026.md").read_text(encoding="utf-8")
    assert "Pyodide cuando hay código" not in plan
    for lesson in range(1, 7):
        folder = next(ROOT.glob(f"{lesson:02d}-*"))
        for name in ("README.md", "CLAUDE.md"):
            text = (folder / name).read_text(encoding="utf-8")
            assert "deck a medida (Pyodide)" not in text
            assert "**Pyodide** ejecutando Python real" not in text


def test_l12_visible_vwap_handles_a_leading_zero_weight_like_the_engine():
    body = (ROOT / "framework/_build/docs/12_body.html").read_text(encoding="utf-8")
    snippet = body.split('<section id="s3">', 1)[1].split("</section>", 1)[0]
    visible = unescape(re.sub(r"<[^>]+>", "", snippet))
    assert "self._t += 1" in visible
    assert "if slice_size <= 0.0:" in visible
    assert visible.index("self._t += 1") < visible.index("if slice_size <= 0.0:")
    assert "sum(self.profile[:self._t + 1]) / sum(self.profile)" not in visible
    assert "target = self.total_size  # reintenta el residual final" in visible
    assert "fill.size > remaining" in visible
    assert "next_executed == self._executed" in visible

    sys.path.insert(0, str(FRAMEWORK))
    try:
        from exchange.book import Level, OrderBook
        from exchange.orders import Side
        from exchange.strategies.vwap import VWAPStrategy

        strategy = VWAPStrategy("X", Side.BUY, 1.0, 2, profile=[0.0, 1.0])
        book = OrderBook("X", [Level(99.0, 1.0)], [Level(101.0, 1.0)])
        assert strategy.on_book_update(book) == []
        assert strategy._t == 1
        action = strategy.on_book_update(book)[0]
        assert action.order.size == pytest.approx(1.0)
    finally:
        sys.path.pop(0)


def test_l8_teaching_separates_student_model_from_atomic_canonical_core():
    body = (ROOT / "framework/_build/docs/08_body.html").read_text(encoding="utf-8")
    custom = (ROOT / "framework/_build/docs/08_custom.js").read_text(encoding="utf-8")
    canonical = (ROOT / "framework/exchange/matching.py").read_text(encoding="utf-8")
    visible = unescape(re.sub(r"<[^>]+>", "", body))

    assert "StudentMatchingEngine.process() · modelo didáctico" in body
    assert "StudentMatchingEngine · modelo didáctico" in body
    assert "exchange/matching.py · core canónico" in body
    assert "class StudentMatchingEngine:" in custom
    assert "class MatchingEngine:" not in custom
    assert "_EPS" not in body and "_EPS" not in custom

    canonical_commit = (
        "candidate = OrderBook(",
        "[Level(level.price, level.size) for level in book.bids]",
        "remaining = Fraction.from_float(order.size)",
        "if Fraction.from_float(take) != take_exact:",
        "remaining -= Fraction.from_float(take)",
        "if order.order_type is OrderType.FOK and remaining > 0:",
        "candidate.reduce(consumed_side, price, take)",
        "if Fraction.from_float(resting_size) != remaining:",
        "book.bids = candidate.bids",
        "book.asks = candidate.asks",
    )
    for claim in canonical_commit:
        assert claim in canonical
        assert claim in visible, f"el bloque canónico visible perdió: {claim}"


def test_l8_exercises_keep_positive_subnormal_sizes_and_guard_remainders():
    spec = (ROOT / "framework/_build/lessons_engine.py").read_text(encoding="utf-8")
    lesson = spec.split("# L8 —", 1)[1].split("# L9 —", 1)[0]

    for stale_guard in (
        "remaining<=1e-12",
        "r<=1e-12",
        "remaining<=EPS",
        "r<=EPS",
        "remaining>EPS",
        "r>EPS",
        "EPS=1e-12",
    ):
        assert stale_guard not in lesson
    assert lesson.count("math.fsum") >= 10
    assert "math.ulp(0.0)" in lesson
    assert "un size subnormal positivo se ejecuta" in lesson
    assert "filled>0.0 and r==o.size" in lesson


def test_l9_atomic_step_is_consistent_from_sources_through_docgen_and_core():
    build = ROOT / "framework/_build"
    custom = (build / "docs/09_custom.js").read_text(encoding="utf-8")
    guide = (build / "custom/09_guion.md").read_text(encoding="utf-8")
    canonical = (ROOT / "framework/exchange/market.py").read_text(encoding="utf-8")

    spec = importlib.util.spec_from_file_location("docgen_l9_contract", build / "docgen.py")
    docgen = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(docgen)
    emitted = docgen.build_doc({"n": 9, "title": "Construir Market"}, guide)

    for source in (custom, emitted, canonical):
        assert "next_i = self._i + 1" in source
        assert "next_book = OrderBook.from_snapshot(" in source
        assert "next_timestamp = _integer_timestamp(raw_timestamp)" in source
        assert "self._i = next_i" in source
        assert "self._timestamp = next_timestamp" in source
        assert "self.book = next_book" in source
    for source in (custom, guide, emitted):
        assert "self._i += 1" not in source
    for source in (custom, canonical, emitted):
        assert "self._timestamp = None" in source
        assert "self.book = None" in source
    assert "_timestamp=None" in guide and "book=None" in guide
    assert "_i=-1`, `_timestamp=None` y `book=None`" in guide


def test_governance_sources_keep_official_assessment_mandatory_and_fail_closed():
    contract = (ROOT / "CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md").read_text(
        encoding="utf-8"
    )
    assert "opción preferente un **examen final" not in contract
    assert "**examen final acumulativo obligatorio**" in contract

    expected = {
        "pedagogy/lessons/14.yml": (
            "la evaluación oficial permanece bloqueada",
            "sus bancos deberán crearse de nuevo",
            "futura fuente privada autorizada",
        ),
        "framework/_build/pedagogy_reports.py": (
            "la evaluación oficial permanece bloqueada",
            "sus bancos deberán crearse de nuevo",
            "futura fuente privada autorizada",
        ),
        "framework/_build/docgen.py": (
            "la evaluación oficial permanece bloqueada",
            "deberán crearse de nuevo",
            "futura fuente privada autorizada",
        ),
        "framework/README.md": (
            "bancos oficiales continuo y final aún no existen",
            "deberán crearse de nuevo",
            "futura fuente privada autorizada",
        ),
        "docs/learning-runtime-authoring.md": (
            "examen final oficial sigue siendo obligatorio",
            "permanece bloqueado",
            "futura fuente privada autorizada",
        ),
        "README.md": (
            "examen final obligatorio",
            "permanece bloqueado",
            "futura fuente privada autorizada",
        ),
        "PLAN_MAESTRO_CURSO_TRADING_2026.md": (
            "examen final obligatorio (banco privado nuevo pendiente)",
        ),
    }
    for relative, required in expected.items():
        source = " ".join(
            (ROOT / relative).read_text(encoding="utf-8").lower().split()
        )
        for claim in required:
            normalized_claim = " ".join(claim.lower().split())
            assert normalized_claim in source, (
                f"{relative} perdió el estado fail-closed: {claim}"
            )


def test_generation_docs_describe_the_actual_lesson_snapshot_scope():
    guide = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    framework_readme = (ROOT / "framework/README.md").read_text(encoding="utf-8")
    normalized_guide = " ".join(guide.split())
    normalized_readme = " ".join(framework_readme.split())

    assert "paquete construido hasta la clase anterior" not in normalized_guide
    assert "snapshot acumulado hasta esa misma clase" in normalized_guide
    assert "incluida la superficie que introduce" in normalized_guide
    assert "excluye APIs futuras" in normalized_guide

    assert "construye durante L4–L14" in normalized_readme
    assert "Cada una de esas lessons recibe en `exercises/exchange/`" in normalized_readme
    assert "regenera L1–L14 y el índice; L15 se genera aparte" in normalized_readme
    assert "regenera las 15 carpetas de lección" not in normalized_readme
