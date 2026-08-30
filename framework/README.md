# framework/ — implementación de referencia y generador del curso

Esto es **infraestructura para el profesor**, no material de alumno.

## `exchange/` — la fuente de verdad

Implementación canónica del paquete que el alumno construye durante L4–L14. Cada
una de esas lessons recibe en `exercises/exchange/` el snapshot acumulado hasta
esa misma clase: incluye la superficie introducida en ella y excluye APIs futuras.

```bash
python smoke_test.py        # verifica el motor end-to-end (libro, matching, backtest, estrategias)
```

## `_build/` — el generador de lecciones

El contenido de las clases L1–L14 (notebooks, HTML, README, CLAUDE, guion) se genera desde specs para mantener consistencia y garantizar que **todo el código corre**.

```bash
python _build/build_course.py --check-only   # autovalida todos los ejercicios (solución + validador)
python _build/build_course.py                # regenera L1–L14 y el índice; L15 se genera aparte
python _build/pedagogy_reports.py            # regenera los informes de continuidad
python _build/build_course.py --clean        # además archiva/borra carpetas antiguas (cuidado)
```

- `lessons_foundations.py` / `lessons_engine.py` / `lessons_strategies.py` — specs de cada lección.
- `nbgen.py` — builders de notebook y del deck HTML (L7+).
- `docgen.py` + `docs/NN_body.html` + `docs/NN_custom.js` — documentos interactivos
  (base compartida en `doc_assets/`: fuentes embebidas, CSS y learning runtime).
- `build_course.py` — autovalida, emite y (opcional) limpia. Si una lección tiene
  `docs/NN_body.html`, su documento **sustituye** al deck.
- `pedagogy_reports.py` — deriva el student journey y el informe de dependencias
  desde los manifests; CI impide que se editen a mano.

**Para cambiar una lección: edita su spec y regenera.** No edites a mano los notebooks generados; se sobrescriben.
El contrato de autoría y el checklist completo están en
[`docs/learning-runtime-authoring.md`](../docs/learning-runtime-authoring.md).

## Práctica acumulativa pública de L15

Se genera aparte en `../15-final-exam/generate_exam.py` (40 preguntas públicas,
A/B/C, +1 / −0.5). No es el examen oficial: los bancos oficiales continuo y
final aún no existen; deberán crearse de nuevo y entregarse exclusivamente desde
la futura fuente privada autorizada.
