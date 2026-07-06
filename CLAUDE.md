# CLAUDE.md — cómo trabajar en este repositorio

Guía para cualquiera (persona o agente) que edite el curso. La regla de oro:

> **Todo el material del alumno se genera. No edites notebooks, docs, READMEs de
> clase, guiones ni el paquete `exchange/` de las lecciones a mano. Edita el
> spec y regenera.**

## Cómo se genera el curso

El generador vive en `framework/_build/`:

- `lessons_foundations.py` / `lessons_engine.py` / `lessons_strategies.py` — los **specs** de cada clase: objetivo, bloques conceptuales, ejercicios de construcción y del gimnasio (cada ejercicio = enunciado + starter + validador `assert` + solución, y opcionalmente `tier`, `min`, `pista`).
- `lessons_docs.py` / `lessons_scripts.py` — textos teóricos y los `.py` consolidados por clase.
- `docs/NN_body.html` + `NN_custom.js` + `NN_data.py` — el documento interactivo de cada clase. `NN_data.py::build()` corre el **motor real** en tiempo de compilación y embebe los números, para que los simuladores no mientan.
- `doc_assets/` — CSS y fuentes embebidas (data-URI) compartidos por todos los docs.
- `capstone/` — plantilla, corrector y baremo del capstone (se copian a L14).
- `docgen.py` / `nbgen.py` — ensamblan docs y notebooks desde los specs.
- `build_course.py` — orquesta todo: autovalida los ~270 ejercicios (ejecuta given+solución+validador), y solo si pasan, emite cada clase (README, CLAUDE, presentación, notebooks, paquete `exchange/` acumulado, `data/`) y el `index.html` raíz.

```bash
python framework/_build/build_course.py --check-only   # solo valida los ejercicios
python framework/_build/build_course.py                # valida y regenera todo
(cd 15-final-exam && python generate_exam.py)          # examen + checkpoint
```

## El paquete de referencia

`framework/exchange/` es la implementación completa de `exchange`. Es lo que se
**stagea** en cada clase (cada lección recibe el paquete construido hasta la
clase anterior). Núcleo en librería estándar pura. El examen y el capstone
importan de aquí.

## Verificación

```bash
cd framework && python -m pytest tests/ -q        # motor, doc-data, examen, capstone
cd framework && python smoke_test.py              # end-to-end sobre el CSV real
node framework/_build/e2e_check.js                # abre los 15 docs + índice sin errores
```

CI (`.github/workflows/course.yml`) corre pytest, el smoke, `--check-only`, los
`.py` consolidados y **regenera + `git diff --exit-code`**: si editaste algo
generado a mano en vez del spec, el diff lo delata.

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
