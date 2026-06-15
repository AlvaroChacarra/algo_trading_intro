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
slippage) · ejecución VWAP (TWAP vs VWAP, perfil, predicción dinámica) · market making
(inventario, adverse selection, CARA) · Avellaneda-Stoikov (reservation price, optimal spread,
efecto de γ).

## Generación
```bash
python generate_exam.py
```
- El banco de preguntas es la lista `QUESTIONS` en `generate_exam.py` (tuplas
  `(pregunta, A, B, C, correcta, tema)`). Editar/ampliar ahí.
- Produce `examen.html` (alumno) y `examen_con_respuestas.html` (clave, respuestas marcadas).
- Ambos HTML están en `.gitignore` (no se versionan los exámenes).

## Notas
- Mantener exactamente 40 preguntas (un `assert` lo comprueba).
- Para variantes A–E, barajar el orden de `QUESTIONS` con semillas distintas antes de renderizar
  (extensión pendiente; la versión actual emite una única forma).
