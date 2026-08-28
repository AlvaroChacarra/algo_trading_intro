# Work 2 — Dry-run docente del curso completo

Estado: **PENDIENTE — no existe evidencia humana cronometrada**

Work 1 autorizó el scale-out con aceptación visual del owner, pero dejó sin
registrar los tiempos reales de L1, L8, L10 y L14. Work 2 amplía la matriz
contractual a L1–L14 y no convierte esas estimaciones ni las pruebas geométricas en
una dry-run humana.

## Baseline preparado

| Lesson | Presentación LIVE declarada | Práctica LIVE seleccionada | REQUIRED autónomo | OPTIONAL |
|---|---:|---:|---:|---:|
| L1 | 20 min | 20 min | 58 min | 44 min |
| L2 | 20 min | 20 min | 58 min | 41 min |
| L3 | 20 min | 20 min | 52 min | 5 min |
| L4 | 20 min | 20 min | 36 min | 20 min |
| L5 | 20 min | 20 min | 34 min | 15 min |
| L6 | 20 min | 20 min | 52 min | 10 min |
| L7 | 20 min | 20 min | 42 min | 10 min |
| L8 | 20 min | 20 min | 56 min | 15 min |
| L9 | 20 min | 20 min | 34 min | 10 min |
| L10 | 20 min | 20 min | 12 min | 5 min |
| L11 | 20 min | 20 min | 14 min | 10 min |
| L12 | 20 min | 20 min | 14 min | 35 min |
| L13 | 20 min | 20 min | 19 min | 0 min |
| L14 | 22 min | 20 min | 125 min | 10 min |

L14 suma 35 minutos de ejercicios REQUIRED y un proyecto/capstone REQUIRED de
90 minutos, declarado por separado como `required_project_minutes`; por eso su
total autónomo es 125 minutos. En L12, la
predicción dinámica de volumen es OPTIONAL, no evaluable y no constituye un
prerrequisito posterior.

## Protocolo de cierre

1. Usar `?mode=aula&profe=1` en el equipo y proyector reales, con viewport y escala
   anotados.
2. Recorrer cada estado LIVE con teclado y a ritmo oral normal, sin saltar escenas.
3. Cronometrar por separado presentación y práctica; usar solo los ejercicios LIVE
   declarados en `pedagogy/exercise_routes.yml`.
4. Registrar legibilidad a distancia, zoom, pausas, preguntas y cualquier scroll
   interno necesario para información esencial.
5. Marcar una lesson PASS solo con 18–22 minutos de presentación, 18–22 minutos de
   práctica y sin salto conceptual o problema visual material.
6. Repetir la lesson afectada después de cualquier corrección.

Se recomienda ejecutar primero L1, L8, L10 y L14 para cerrar la deuda heredada y
después una lesson representativa adicional de cada bloque. La baseline docente V2
solo puede recibir GO definitivo cuando el owner adjunte tiempos y resultado.

## Evidencia disponible

- Selección explícita de ejercicios y tiempos declarados: disponible.
- Navegación y geometría automatizadas en los viewports de aceptación: disponible
  en el artefacto de CI de Work 2.
- Aceptación visual heredada de los cuatro pilotos: disponible en
  `docs/work1-teaching-dry-run.md`.
- Tiempos reales y PASS humano por lesson: **no disponibles**.

Por tanto, este artefacto no autoriza a describir el curso como validado en aula;
mantiene visible la única condición externa pendiente del cierre docente.
