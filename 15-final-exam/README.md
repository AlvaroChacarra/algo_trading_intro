# Clase 15 — Práctica acumulativa pública

Práctica de cierre del curso. Cubre todo el arco: Python/OOP, el framework
`exchange`, microestructura, matching, VWAP, market making y Avellaneda-Stoikov.

> **No es el examen oficial.** Banco, opciones y respuestas forman parte de un
> repositorio público y deben considerarse divulgados. El examen obligatorio
> del 30% permanece bloqueado hasta disponer de un banco nuevo en la fuente
> privada prevista por `ARCHITECTURE.md`.

L15 es un **assessment lineal**, no una presentación por escenas. El capstone de
L14 es trabajo autónomo separado y no sustituye este examen.

## Formato
- 40 minutos · 40 preguntas · 3 opciones (A/B/C).
- Baremo: acierto **+1**, fallo **−0.5**, en blanco **0**.

## Generar
```bash
python generate_exam.py
```
Produce `examen.html` (práctica autocorregible) y una clave local de práctica.
La versión canónica se versiona; la clave y variantes quedan fuera de Git.

## Trazabilidad pedagógica

Las tuplas históricas de pregunta conservan sus seis campos, por lo que el
generador y sus variantes siguen siendo compatibles. En paralelo,
`question_bank.py` publica `CANONICAL_METADATA`, `EXTRA_METADATA` y
`CHECKPOINT_METADATA`; `PUBLIC_BANKS` mantiene la correspondencia posicional
entre cada pregunta y su metadata, sin incluir respuestas.

Cada registro tiene id estable, lección(es), objetivo(s), ids semánticos de
conceptos/APIs/notación, tipo cognitivo y dificultad. Los 40 ítems cubren
L1–L14 y cumplen el reparto 8×5. `code_reading` contiene código/traza y
`debugging` un fallo observable.

Los tests cruzan enlaces e ids con manifests y blueprint: solo admiten objetivos
LIVE/REQUIRED, exigen todos los requisitos L15 y excluyen ids OPTIONAL.
