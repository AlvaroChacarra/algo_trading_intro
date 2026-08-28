# Work 1 — Dry-run docente

Estado: **ACEPTADO POR EL OWNER — dry-run cronometrada no registrada**

Este artefacto define la prueba de impartición de L1, L8, L10 y L14. Los tiempos
declarados y la selección de ejercicios proceden del contrato. El 28 de agosto
de 2026, el owner del curso revisó el piloto, indicó que «tiene buena pinta» y
autorizó expresamente el commit final, PR y merge a `main` para continuar con
Work 2.

Esta aceptación es una decisión de producto, no una dry-run cronometrada. No se
han proporcionado tiempos reales por lesson ni una evaluación separada de cada
registro. La diferencia queda documentada para no presentar estimaciones o CI
como evidencia humana inexistente.

## Protocolo

1. Usar un navegador desktop en `?mode=aula&profe=1`, preferiblemente conectado
   al proyector o pantalla que se empleará en clase. Registrar viewport y escala.
2. Limpiar el progreso de la lesson. Recorrer toda la ruta LIVE a ritmo oral
   normal, usando las etapas, simuladores y transiciones previstas. No saltar una
   escena porque resulte familiar.
3. Cronometrar por separado la presentación y la práctica guiada. Para la
   práctica, usar únicamente los ejercicios marcados LIVE.
4. Comprobar desde una distancia representativa que títulos, código, fórmulas,
   estado y controles sean legibles. Registrar cualquier zoom necesario.
5. Anotar prerrequisitos ausentes, recuperación insuficiente, transición confusa
   o contenido que deba cambiar de ruta.
6. Marcar cada lesson `PASS` solo si la presentación ocupa 18–22 minutos, la
   práctica se aproxima a 20 minutos y no hay un problema pedagógico o visual
   material. Tras cualquier cambio, repetir la lesson afectada.

## Baseline contractual

| Lesson | Caso que valida | Presentación LIVE | Práctica LIVE | Selección guiada |
|---|---|---:|---:|---|
| L1 | Introducción densa | 20 min | 19 min | Build 1–3; A1–A2 |
| L8 | Algoritmo código ↔ estado | 20 min | 19 min | B1–B3 |
| L10 | Arquitectura acumulativa | 20 min | 21 min | Build 1–3; C1–C2; A1–A2 |
| L14 | Matemática y simulación | 20 min | 21 min | Build 1–3; C1–C2; A1–A2 |

La tolerancia ejecutable de práctica guiada es 18–22 minutos y una desviación
máxima de 2 minutos respecto a `guided_minutes`. El resto de ejercicios está
clasificado de forma explícita como REQUIRED u OPTIONAL.

## Evidencia humana disponible

- Fecha: 28 de agosto de 2026.
- Revisor y decisor: owner del curso.
- Resultado: aceptación visual del piloto y autorización de merge.
- Incidencias materiales comunicadas: ninguna.
- Tiempos reales de presentación y práctica: **NO REGISTRADOS**.
- Validación formal por lesson y entorno proyectado: **NO REGISTRADA**.

## Decisión global

- Resultado de producto: **GO para mergear Work 1 e iniciar Work 2**.
- Base automática: CI, geometría por etapa, fallback móvil, generación y
  contratos pedagógicos verdes.
- Riesgo residual aceptado: la adecuación real a 18–22 minutos de presentación y
  aproximadamente 20 minutos de práctica solo está validada por contrato, no por
  cronometraje docente.
- Acción en Work 2: ejecutar la dry-run cronometrada en su primer hito de
  validación y corregir antes de extender el runtime al resto del curso si algún
  piloto excede la ventana.
