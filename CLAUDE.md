# CLAUDE.md — cómo trabajar en este repositorio

Guía para cualquiera (persona o agente) que edite el curso. La regla de oro:

> **Todo el material del alumno se genera. No edites notebooks, docs, READMEs de
> clase, guiones ni el paquete `exchange/` de las lecciones a mano. Edita el
> spec y regenera.**

Antes de decidir, lee `AGENTS.md`. Para pedagogía manda
`CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md`; para infraestructura,
`ARCHITECTURE.md`. El contrato verificable de continuidad vive en `pedagogy/`.

## Cómo se genera el curso

El generador vive en `framework/_build/`:

- `lessons_foundations.py` / `lessons_engine.py` / `lessons_strategies.py` — los **specs** de cada clase: objetivo, bloques conceptuales, ejercicios de construcción y del gimnasio (cada ejercicio = enunciado + starter + validador `assert` + solución, y opcionalmente `tier`, `min`, `pista`).
- `lessons_docs.py` / `lessons_scripts.py` — textos teóricos y los `.py` consolidados por clase.
- `docs/NN_body.html` + `NN_custom.js` + `NN_data.py` — el documento interactivo de cada clase. `NN_data.py::build()` corre la **implementación canónica** en tiempo de compilación sobre el replay sintético y embebe resultados reproducibles, no cifras escritas a mano.
- `doc_assets/` — CSS y fuentes embebidas (data-URI) compartidos por todos los docs.
- `doc_assets/learning_runtime.{css,js}` — interpreta escenas para `?mode=aula` y
  `?mode=estudio` sin duplicar contenido.
- `capstone/` — plantilla, corrector y baremo del capstone (se copian a L14).
- `docgen.py` / `nbgen.py` — ensamblan docs y notebooks desde los specs.
- `build_course.py` — orquesta todo: autovalida los **293 ejercicios** (ejecuta given+solución+validador), y solo si pasan, emite cada clase (README, CLAUDE, presentación, notebooks, paquete `exchange/` acumulado, `data/`) y el `index.html` raíz.

```bash
python framework/_build/build_course.py --check-only   # solo valida los ejercicios
python pedagogy_check.py                               # PED-CHECK-01..09
python framework/_build/build_course.py                # valida y regenera todo
(cd 15-final-exam && python generate_exam.py)          # examen + checkpoint
```

## El paquete de referencia

`framework/exchange/` es la implementación completa de `exchange`. Es lo que se
**stagea** en cada clase: cada lesson recibe el snapshot acumulado hasta esa
misma clase, incluida la superficie que introduce, y excluye APIs futuras.
Núcleo en librería estándar pura. El examen y el capstone importan de aquí.

## Verificación

```bash
python pedagogy_check.py
python framework/_build/pedagogy_reports.py --check
python -m pytest framework/tests/ -q
python framework/_build/fuzz_matching.py --seed 20260828 --cases 120000
(cd framework && python smoke_test.py)
python framework/_build/build_course.py --check-only
node --test framework/_build/desktop_evidence_contract.test.js
node --test framework/_build/pages_e2e.test.js framework/_build/validate_pages_audit.test.js
python framework/_build/build_pages.py --output _site
python framework/_build/check_pages.py _site --base-path /algo_trading_intro/
```

La evidencia browser canónica exige los binarios fijados por Playwright. CI abre
los 15 documentos, ejecuta Desktop con `--audit-dir` y valida el artefacto en un
segundo proceso con `--verify-browser`; Pages repite el build, compara ambos
manifests de integridad y ejecuta WebKit/JupyterLite en contextos limpios. Si no
están instalados los navegadores, no describas esos gates como ejecutados.

CI (`.github/workflows/course.yml`) corre además los `.py` consolidados,
regenera y exige un working tree completamente limpio mediante
`git status --porcelain=v1 --untracked-files=all`: detecta tanto drift tracked
como salidas públicas nuevas aún no versionadas. El entorno Python de Pages se
instala desde `requirements-pages-lock.txt` con hashes y binarios únicamente.

## Dónde vive cada cosa que NO se genera (editable a mano)

- `framework/exchange/**` — el paquete de referencia.
- `framework/_build/**` — specs, docs-fuente, generador, capstone.
- `framework/tests/**`, `framework/smoke_test.py`, `framework/_build/e2e_check.js`.
- `15-final-exam/{generate_exam,question_bank,verify_result}.py`.
- `check_my_work.py`, este `CLAUDE.md`, `README.md`, `PLAN_MAESTRO_*.md`.

Todo lo demás bajo `NN-*/` es salida del generador.

## Convenciones de diseño

- Tokens: fondo `#09090b`, acento cian `#22d3ee` ("**lo cian se toca**"), bids verde `#4ade80`, asks rojo `#f87171`, aviso `#fbbf24`.
- Motores JS compartidos activados por marcado, no por IDs: `.scrolly[data-scrolly]`, `.runbtn[data-target]`, `.quiz[data-quiz]`, `#rail`, `DOC.chart(...)`. Progreso en `localStorage` (`algoTrading.NN`).
- `?profe=1` en cualquier doc abre el cajón con el guion.
