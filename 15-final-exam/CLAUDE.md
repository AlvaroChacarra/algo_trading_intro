# Clase 15 — Examen final (guía de implementación)

Cierre del curso. No es una lección con notebook: es un test que se genera.

## Formato y baremo
- 40 minutos · 40 preguntas · 3 opciones (A/B/C), una correcta.
- Acierto **+1**, fallo **−0.5**, en blanco **0** (penaliza responder a ciegas).
- Dificultad: conceptos de algo trading exigentes + preguntas de código de nivel intermedio
  sobre el propio framework `exchange`.

## Cobertura (todo el arco del curso)
Python/OOP y diseño del framework (Strategy, polimorfismo, encapsulación) · microestructura
(spread, mid, microprice, imbalance, depth) · tipos de orden y matching (market/limit/IOC/FOK,
slippage) · ejecución VWAP (slicing, TWAP vs VWAP y perfil estático) · market making
(inventario, adverse selection, CARA) · Avellaneda-Stoikov (reservation price, optimal spread,
efecto de γ).

## Generación
```bash
python generate_exam.py            # examen.html + examen_con_respuestas.html + checkpoint.html
python generate_exam.py --seed 3   # examen_s3.html (variante equilibrada, no versionada)
```
- El banco de preguntas vive en **`question_bank.py`** (fuente única de verdad):
  - `CANONICAL` — las 40 oficiales, orden fijo → `examen.html` reproducible al byte.
  - `EXTRA` — pool ampliado (80 en total) para variantes por seed con el mismo reparto por tema.
  - `CHECKPOINT` — 24 preguntas de L1-L6 (Python, módulos, POO) para el autoexamen de mitad de curso.
  - `*_METADATA` — trazabilidad posicional de cada pregunta a lecciones, objetivos,
    tipo cognitivo y dificultad, sin respuestas ni cambios en la tupla consumida.
  - `PUBLIC_BANKS` — registro determinista de los tres bancos y sus metadatos.
  - `sample_balanced()` — muestrea equilibrado por tema, reproducible por seed.
- `generate_exam.py` sin `--seed` emite: `examen.html` (alumno), `examen_con_respuestas.html`
  (clave del profe) y **`../06-oop-iii-inheritance/checkpoint.html`** (20 preguntas, 20 min).
  Con `--seed N>0` emite una variante `examen_sN.html` (equilibrada, distinta, para otra convocatoria).
- `examen.html` y `checkpoint.html` **se versionan**; `examen_*.html` (clave y variantes) están en `.gitignore`.

## Código de resultado + verificación
Al corregirse, examen y checkpoint emiten un código copiable tipo
`AT26-L15-S0-R34-W3-B3-N8.13-27` con un checksum. El profesor lo valida con:
```bash
python verify_result.py AT26-L15-S0-R34-W3-B3-N8.13-27
```
`verify_result.py` recomputa el checksum (detecta copias mal pegadas o notas infladas a mano) y
la coherencia nota↔aciertos. El checksum del JS (`generate_exam.py`) y el de Python deben coincidir.

## Autocorrección del alumno (cualquier clase)
Desde la raíz del repo: `python check_my_work.py <clase>` ejecuta el cuaderno de esa clase y
cuenta validadores que pasan / fallan / sin tocar (sin abrir Jupyter). `--aux` para el gimnasio,
`all` para todas.

## Notas
- Mantener exactamente 40 preguntas canónicas (un `assert` lo comprueba).
- Mantener para L15 el reparto 8×5 del blueprint y al menos ocho integraciones
  multi-lección/multi-bloque enlazadas a `l15-integrate-course`.
- La métrica `equity_curve` es contenido core; lo OPTIONAL es dibujarla con
  matplotlib. No evaluar predicción dinámica de volumen, factor de corrección,
  la visualización de la curva ni otras profundizaciones OPTIONAL: el test de
  regresión del banco lo impide.
- Si tocas la fórmula del checksum en el JS, cámbiala también en `verify_result.py` (y viceversa).
