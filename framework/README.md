# framework/ — implementación de referencia y generador del curso

Esto es **infraestructura para el profesor**, no material de alumno.

## `exchange/` — la fuente de verdad

Implementación canónica del paquete que el alumno construye a lo largo de las 15 clases. Cada lección entrega un subconjunto acumulado de estos módulos en su `exercises/exchange/`.

```bash
python smoke_test.py        # verifica el motor end-to-end (libro, matching, backtest, estrategias)
```

## `_build/` — el generador de lecciones

El contenido de las clases L1–L14 (notebooks, HTML, README, CLAUDE, guion) se genera desde specs para mantener consistencia y garantizar que **todo el código corre**.

```bash
python _build/build_course.py --check-only   # autovalida todos los ejercicios (solución + validador)
python _build/build_course.py                # regenera las 15 carpetas de lección
python _build/build_course.py --clean        # además archiva/borra carpetas antiguas (cuidado)
```

- `lessons_foundations.py` / `lessons_engine.py` / `lessons_strategies.py` — specs de cada lección.
- `nbgen.py` — builders de notebook y del deck HTML (L7+).
- `docgen.py` + `docs/NN_body.html` + `docs/NN_custom.js` — los documentos interactivos de L1-L6
  (base compartida en `doc_assets/`: fuentes embebidas, CSS y motores JS genéricos).
- `build_course.py` — autovalida, emite y (opcional) limpia. Si una lección tiene
  `docs/NN_body.html`, su documento **sustituye** al deck.

**Para cambiar una lección: edita su spec y regenera.** No edites a mano los notebooks generados; se sobrescriben.

## Examen final

Se genera aparte en `../15-final-exam/generate_exam.py` (40 preguntas, A/B/C, +1 / −0.5).
