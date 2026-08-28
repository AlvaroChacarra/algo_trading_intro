# Guía de autoría del learning runtime

Esta guía describe cómo mantener una lesson sin crear una segunda versión del
contenido. L1–L14 usan el mismo contrato; L15 conserva su UX lineal de examen.

## Una fuente, varios recorridos

El cuerpo HTML se genera desde `framework/_build/`. El manifest
`pedagogy/lessons/NN.yml` enlaza escenas pedagógicas con nodos de ese cuerpo; el
runtime solo decide qué recorrido mostrar.

- `?mode=aula`: una escena activa, teclado y sin scroll del `body` en desktop.
- `?mode=estudio`: LIVE + REQUIRED en lectura vertical; OPTIONAL permanece oculto
  hasta que el alumno pulsa **Incluir OPTIONAL** o usa `&optional=1`.
- `?mode=aula&profe=1`: abre las notas docentes y permite ampliar el alcance de
  ruta sin cambiar de documento.
- En pantallas de hasta 900 px, una petición de aula usa el fallback vertical.
- `#scene-id/stage-id` crea un deep link estable. También se aceptan los parámetros
  `scene` y `stage`.

La posición, el alcance de ruta y el progreso por LIVE / REQUIRED / OPTIONAL se
guardan localmente por lesson. El índice lee ese mismo estado; no calcula progreso
a partir del porcentaje de scroll.

## Contrato mínimo de una lesson

El manifest debe declarar:

1. `requires` e `introduces` para conceptos, APIs y notación;
2. la ruta de cada introducción y requisito;
3. `recalls` cuando se recupera conocimiento distante;
4. superficie y transiciones de API visibles al alumno;
5. objetivos y carga;
6. escenas y etapas;
7. un bridge causal hacia la lesson siguiente;
8. bindings `package_checks` para las APIs acumulativas relevantes.

Los identificadores se eligen en los registries de `pedagogy/course_graph.yml`.
OPTIONAL nunca puede ser el único origen de un requisito futuro ni de un objetivo
evaluable.

Una escena apunta a una sección existente mediante `dom_id`:

```json
{
  "id": "l08-plan-validate-commit",
  "dom_id": "s1",
  "type": "code-state",
  "route": "LIVE",
  "layout": "split-42-58",
  "concepts": ["matching.plan_validate_commit", "matching.atomicity"],
  "duration_minutes": 10,
  "stages": [
    {"id": "plan", "dom_stage": 5, "route": "LIVE"},
    {"id": "validate", "dom_stage": 6, "route": "LIVE"},
    {"id": "commit", "dom_stage": 7, "route": "LIVE"}
  ]
}
```

`type` debe pertenecer al conjunto cerrado de `course_graph.yml`. `layout` describe
la intención de composición; no debe compensar un cuerpo mal estructurado. Una
etapa puede cambiar de ruta dentro de una escena: el runtime la excluirá del
recorrido hasta que su ruta esté habilitada.

## Cómo crear o migrar una lesson

1. Audita presentación, notebook principal, auxiliar, script y snapshot acumulado.
2. Declara primero las dependencias. Si algo se usa antes de aparecer, introduce,
   recupera o mueve el contenido; no añadas una excepción al checker.
3. Estabiliza la API pública desde su primera construcción. Si existe una versión
   pedagógica mínima, dale nombre propio y declara la transición.
4. Compón una ruta LIVE de 18–22 minutos de presentación y 18–22 minutos de
   práctica. Clasifica cada ejercicio por contenido en
   `pedagogy/exercise_routes.yml`.
5. Reutiliza secciones y simuladores reales. Añade `id` estable a cada nodo que el
   manifest necesite y evita duplicar el cuerpo para aula.
6. Termina con recap, bridge causal y quiz diagnóstico. El bridge debe expresar
   capacidad actual → limitación observable → nueva necesidad.
7. Regenera el curso y los dos informes de continuidad.
8. Ejecuta los checks pedagógicos, unitarios, desktop, móvil, Pages y JupyterLite.

## Comandos de mantenimiento

Desde la raíz del repositorio:

```bash
python pedagogy_check.py
python framework/_build/pedagogy_reports.py
python framework/_build/build_course.py --check-only
python framework/_build/build_course.py
python -m pytest framework/tests/ -q
node framework/_build/e2e_check.js
node framework/_build/desktop_e2e.js --audit-dir artifacts/work2-full-course-scaleout
```

Después de regenerar, `git diff` debe contener únicamente cambios esperados. En CI,
`pedagogy_reports.py --check` y una segunda regeneración detectan drift o ediciones
manuales de artefactos generados.

## Gate de revisión

Antes de aceptar una lesson nueva, comprueba como alumno:

- entiendo todo lo que se presupone al entrar;
- la abstracción nace de un problema que acabo de observar;
- reconozco sintaxis, notación y API;
- sé qué he construido y de qué lesson procede;
- distingo con precisión LIVE, REQUIRED y OPTIONAL;
- el assessment solo usa conocimiento obligatorio;
- entiendo la limitación que hace necesaria la siguiente lesson.

Y como docente: recorre aula con teclado en todos los viewports soportados, prueba el
modo profesor, confirma que lo esencial no necesita scroll interno y registra una
dry-run cronometrada con el equipo real de clase.
