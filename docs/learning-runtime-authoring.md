# Guía de autoría del learning runtime

Esta guía describe cómo mantener una lesson sin crear una segunda versión del
contenido. L1–L14 usan el mismo contrato; L15 conserva una UX lineal de práctica
acumulativa pública. El examen final oficial sigue siendo obligatorio, pero
permanece bloqueado: su banco deberá crearse de nuevo y entregarse desde la
futura fuente privada autorizada.

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
    {"id": "commit", "dom_stage": 7, "route": "LIVE"},
    {"id": "remainder", "dom_stage": 8, "route": "REQUIRED", "duration_minutes": 1}
  ]
}
```

`type` debe pertenecer al conjunto cerrado de `course_graph.yml`. `layout` describe
la intención de composición; no debe compensar un cuerpo mal estructurado. Una
etapa puede cambiar de ruta dentro de una escena: el runtime la excluirá del
recorrido hasta que su ruta esté habilitada.

`routes.LIVE`, `routes.REQUIRED` y `routes.OPTIONAL` son un inventario exacto, no
una segunda clasificación manual. Cada escena aparece bajo su `scene.route`; una
etapa que cambia la ruta efectiva aparece además como `scene-id/stage-id` bajo la
ruta de la etapa. El checker exige la misma secuencia que en `scenes`.

## Carga autónoma sin dobles conteos

Los minutos autónomos separan cuatro clases de trabajo: documento, ejercicio,
quiz y proyecto. Los ejercicios proceden de `pedagogy/exercise_routes.yml`; el
manifest de la lesson declara las otras tres en `load.autonomous_components`.
Toda escena o etapa efectiva REQUIRED/OPTIONAL debe tener un componente de
documento o quiz con el mismo identificador y ruta. Una escena superior conserva
sus minutos como presupuesto agregado de su ruta base; una etapa que cambia de
ruta declara `stage.duration_minutes` como fuente canónica aditiva para su ruta
efectiva. El componente autónomo del mismo id refleja exactamente ese valor y no
es una segunda fuente. El runtime muestra la duración del estado activo, no la
duración base junto a una ruta override. Si una escena
autónoma mezcla rutas en sus etapas, hay que dividirla para conservar una medida
honesta de su duración.

```json
{
  "required_autonomous_minutes": 133,
  "autonomous_components": {
    "documents": [
      {
        "id": "l14-capstone",
        "route": "REQUIRED",
        "minutes": 90,
        "overlap_id": "l14-capstone-project"
      }
    ],
    "quizzes": [
      {"id": "l14-quiz", "route": "REQUIRED", "minutes": 8}
    ],
    "projects": [
      {
        "id": "l14-capstone-project",
        "route": "REQUIRED",
        "minutes": 90,
        "overlap_id": "l14-capstone-project"
      }
    ]
  }
}
```

Por defecto todos los componentes suman. Un mismo `overlap_id` solo puede unir
representaciones de clases distintas y con igual duración: en el ejemplo,
documento y proyecto describen la misma actividad de 90 minutos y cuentan una
vez. El total REQUIRED es ejercicios (35) + actividad (90) + quiz (8) = 133.

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
corepack enable
npm ci
python -m pip install --requirement requirements-pages-lock.txt --require-hashes --only-binary=:all:
npx --no-install playwright install chromium webkit
python pedagogy_check.py
python framework/_build/pedagogy_reports.py --check
python framework/_build/build_course.py --check-only
python framework/_build/build_course.py
python -m pytest framework/tests/ -q
npm run test:desktop-contract
node --test framework/_build/pages_e2e.test.js
npm run test:e2e-docs
npm run test:e2e-desktop
npm run validate:e2e-desktop
python framework/_build/build_pages.py --output _site
python framework/_build/check_pages.py _site --base-path /algo_trading_intro/
python framework/_build/build_pages.py --output _site-repro
python framework/_build/check_pages.py _site-repro --base-path /algo_trading_intro/
cmp _site/.pages-integrity.json _site-repro/.pages-integrity.json
WORK2_PAGES_SCOPE=site node framework/_build/pages_e2e.js _site
```

El runtime de CI usa exactamente Node 20.19.4, npm 10.8.2 y Playwright 1.62.1,
declarados en `package.json` y `package-lock.json`. La evidencia desktop solo se
considera válida si el runner termina los 132 registros del plan cerrado y el
validador independiente vuelve a comprobar el SHA, los 32 inputs, la cobertura y
la ausencia de registros omitidos, duplicados o inesperados. El gate de Pages
ejecuta además un shard JupyterLite limpio por L1–L14; esos 14 shards, WebKit
móvil y la evidencia de identidad del navegador son gates browser remotos, no
quedan acreditados por construir el site estático localmente.

Después de regenerar, `git status --porcelain=v1 --untracked-files=all` debe quedar
vacío una vez versionadas todas las salidas públicas esperadas. En CI,
`pedagogy_reports.py --check` y una segunda regeneración detectan tanto drift o
ediciones manuales como outputs nuevos no ignorados que falten en el commit.

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
