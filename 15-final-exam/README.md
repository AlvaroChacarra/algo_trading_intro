# Clase 15 — Examen final

Test de cierre del curso. Cubre todo el arco: Python/OOP, el framework `exchange`,
microestructura, tipos de orden y matching, ejecución VWAP, market making y Avellaneda-Stoikov.

L15 es un **assessment lineal**, no una presentación por escenas. El capstone de
L14 es trabajo autónomo separado y no sustituye este examen.

## Formato
- 40 minutos · 40 preguntas · 3 opciones (A/B/C).
- Baremo: acierto **+1**, fallo **−0.5**, en blanco **0**.

## Generar
```bash
python generate_exam.py
```
Produce `examen.html` (para el alumno) y `examen_con_respuestas.html` (clave).
La versión canónica de `examen.html` se versiona; la clave y las variantes por
semilla quedan fuera del control de versiones (ver `.gitignore`).

## Trazabilidad pedagógica

Las tuplas históricas de pregunta conservan sus seis campos, por lo que el
generador y sus variantes siguen siendo compatibles. En paralelo,
`question_bank.py` publica `CANONICAL_METADATA`, `EXTRA_METADATA` y
`CHECKPOINT_METADATA`; `PUBLIC_BANKS` mantiene la correspondencia posicional
entre cada pregunta y su metadata, sin incluir respuestas.

Cada registro tiene un id estable, lección(es), objetivo(s) reales del
blueprint, tipo de la distribución cognitiva, nivel cognitivo y dificultad. Los
40 ítems canónicos cumplen exactamente el reparto de L15 (8 por cada uno de los
cinco tipos). Ocho son integraciones explícitas de al menos dos lecciones y dos
bloques del curso, todas enlazadas con `l15-integrate-course`.

Los tests cruzan automáticamente estos enlaces con
`pedagogy/assessment_blueprint.yml`: solo se admiten objetivos evaluables de
ruta `LIVE` o `REQUIRED`; una profundización `OPTIONAL` no puede entrar en el
assessment.
