# Contrato pedagógico --- Algorithmic Trading con Python

**Status:** Proposed baseline\
**Version:** 1.1\
**Date:** 2026-08-17\
**Owner:** Álvaro López Chacarra\
**Ámbito:** metodología docente, ritmo de aula, trabajo autónomo y
evaluación continua

------------------------------------------------------------------------

## 1. Propósito

Este documento define la metodología pedagógica autoritativa del curso
de **Algorithmic Trading con Python**.

Su objetivo es separar claramente:

-   lo que se explica en clase;
-   lo que se practica conjuntamente;
-   lo que el alumno debe completar de forma autónoma;
-   cuándo y cómo se comprueba que ese aprendizaje se ha consolidado.

Principio central:

> La clase introduce, estructura y practica lo esencial. El aprendizaje
> no termina al acabar la sesión: el alumno debe completar y consolidar
> el contenido por su cuenta, sabiendo que será evaluado posteriormente.

El curso no pretende que todo el material disponible de una lesson quede
consumido durante el tiempo presencial.

------------------------------------------------------------------------

## 2. Unidad docente y duración

Una **lesson** es una unidad de contenido del curso.

Una **sesión presencial estándar** dura aproximadamente **50 minutos**.

La estructura objetivo es:

  ------------------------------------------------------------------------
  Bloque                           Duración objetivo Función
  --------------------- ---------------------------- ---------------------
  Evaluación de                               10 min Recuperación activa y
  contenido anterior                                 accountability

  Presentación                                20 min Intuición, conceptos
                                                     y demostración

  Ejercicios conjuntos                        20 min Aplicación guiada y
                                                     resolución de dudas

  **Total**                              **≈50 min** 
  ------------------------------------------------------------------------

Esta distribución es una referencia operativa, no una restricción al
minuto. Puede adaptarse cuando la naturaleza de una lesson lo requiera.

------------------------------------------------------------------------

## 3. Modelo de aprendizaje

Cada lesson se completa en tres fases.

### Fase 1 --- Introducción y comprensión

Durante la presentación, el profesor debe priorizar:

1.  el problema que se quiere resolver;
2.  la intuición;
3.  los conceptos esenciales;
4.  las conexiones con lessons anteriores;
5.  una demostración suficiente para que el alumno pueda continuar
    trabajando después.

La presentación no tiene como objetivo agotar toda la teoría disponible.

------------------------------------------------------------------------

### Fase 2 --- Práctica guiada

Durante aproximadamente 20 minutos se resuelven ejercicios
conjuntamente.

El objetivo no es completar todos los ejercicios de la lesson, sino:

-   practicar el núcleo;
-   mostrar el patrón de razonamiento;
-   resolver las dificultades más importantes;
-   dejar al alumno preparado para trabajar de forma autónoma.

Los ejercicios restantes forman parte del aprendizaje requerido aunque
no se completen durante la sesión.

------------------------------------------------------------------------

### Fase 3 --- Consolidación autónoma

Después de la clase, el alumno debe revisar y completar el material
pendiente:

-   documento interactivo;
-   notebook de construcción;
-   ejercicios no realizados;
-   gimnasio o ejercicios auxiliares cuando corresponda;
-   código o conceptos señalados como evaluables.

Regla:

> "No se ha dado en directo" no significa "no entra".

El material publicado de la lesson forma parte del contenido del curso
salvo que el profesor indique expresamente lo contrario.

------------------------------------------------------------------------

## 4. Función de los tests

Los tests cortos son el principal mecanismo de **recuperación activa y
responsabilidad individual** durante el semestre.

Su función no es únicamente calificar. Deben provocar que el alumno:

-   vuelva sobre el contenido después de clase;
-   complete lo que no se terminó presencialmente;
-   detecte lagunas antes de seguir acumulando conceptos;
-   mantenga continuidad entre sesiones.

### Formato estándar

Por cada lesson evaluada:

-   **10 preguntas**;
-   respuestas **A/B/C/D**;
-   aproximadamente **10 minutos**.

Las preguntas pueden cubrir tanto lo explicado presencialmente como el
material que el alumno debía completar por su cuenta.

------------------------------------------------------------------------

## 5. Regla fundamental de evaluación diferida

Una lesson solo debe evaluarse cuando el alumno haya tenido una
oportunidad razonable de:

1.  asistir o consumir la lesson;
2.  trabajar el contenido por su cuenta;
3.  consolidarlo antes del test.

Por tanto, el test **no tiene que producirse necesariamente en la sesión
inmediatamente posterior en términos cronológicos**.

Debe producirse en la primera sesión compatible con haber tenido tiempo
real de estudio.

------------------------------------------------------------------------

## 6. Sesión estándar

Cuando existe tiempo entre dos sesiones para trabajar de forma autónoma:

``` text
Sesión N
→ presentación Lesson N
→ ejercicios Lesson N
→ trabajo autónomo

Sesión N+1
→ test Lesson N (10 preguntas / ≈10 min)
→ presentación Lesson N+1
→ ejercicios Lesson N+1
```

Este es el patrón docente por defecto.

------------------------------------------------------------------------

## 7. Sesiones consecutivas o dobles

Cuando dos sesiones se imparten consecutivamente, **no se evalúa la
primera lesson en la segunda sesión**.

Razón:

> El alumno todavía no ha tenido la fase de consolidación autónoma.

Ejemplo:

``` text
Sesión A
→ Lesson 4

inmediatamente después

Sesión B
→ Lesson 5
→ NO test de Lesson 4

siguiente encuentro con tiempo de estudio previo

→ test conjunto Lesson 4 + Lesson 5
→ 20 preguntas
→ ≈20 minutos
```

Regla general:

> 10 preguntas y aproximadamente 10 minutos por cada lesson pendiente de
> evaluación.

Como consecuencia, una sesión que acumule dos lessons anteriores puede
dedicar aproximadamente 20 minutos a evaluación y reducir
proporcionalmente el tiempo disponible para presentación o ejercicios.

Esto debe considerarse al planificar el calendario real.

------------------------------------------------------------------------

## 8. Lessons autónomas

Determinadas lessons pueden asignarse total o parcialmente para trabajo
autónomo.

Esto es una herramienta pedagógica válida, no un recurso de emergencia.

Una lesson autónoma debe proporcionar suficiente material para que el
alumno pueda trabajar sin una explicación presencial completa:

-   documento interactivo;
-   ejemplos;
-   notebook;
-   ejercicios;
-   validadores;
-   material de apoyo necesario.

### Regla de consolidación

Una lesson realizada autónomamente **no tiene por qué evaluarse
inmediatamente en la siguiente sesión**.

La siguiente sesión presencial puede utilizarse para:

-   explicar los puntos esenciales;
-   corregir interpretaciones;
-   resolver dudas;
-   mostrar los ejercicios de mayor valor;
-   conectar esa lesson con la siguiente.

El test debe situarse después de esta consolidación cuando
pedagógicamente sea preferible.

Ejemplo:

``` text
Alumno trabaja Lesson 4 en casa
→ siguiente sesión: consolidación Lesson 4 + avance Lesson 5
→ trabajo autónomo
→ sesión posterior: test Lesson 4 + Lesson 5
```

La secuencia exacta puede variar. La condición necesaria es que el
alumno sepa claramente **qué contenido tiene que dominar y cuándo será
evaluado**.

------------------------------------------------------------------------

## 9. Uso estratégico de lessons autónomas

No todas las lessons tienen que consumir una sesión presencial completa.

Son buenas candidatas para trabajo autónomo aquellas cuyo contenido:

-   sea principalmente práctica;
-   pueda seguirse bien mediante el documento interactivo;
-   disponga de validadores suficientes;
-   requiera repetición más que explicación conceptual;
-   dependa menos de una explicación causal compleja del profesor.

El tiempo presencial debe concentrarse en aquello donde el profesor
aporta mayor valor marginal:

-   intuiciones difíciles;
-   arquitectura;
-   microestructura;
-   decisiones de diseño;
-   interpretación económica;
-   errores conceptuales frecuentes;
-   razonamiento cuantitativo;
-   integración entre componentes.

No se debe decidir qué lessons serán autónomas solo para "ganar tiempo".
La decisión debe maximizar aprendizaje por minuto presencial.

------------------------------------------------------------------------

## 10. Relación entre presentación y material completo

La presentación de aproximadamente 20 minutos representa el **core
narrativo** de la lesson.

El repositorio puede contener más profundidad que la presentada en
directo.

Se distinguen tres niveles conceptuales:

### Núcleo presencial

El alumno debe comprenderlo durante la sesión.

### Consolidación requerida

Puede quedar parcial o totalmente para casa, pero forma parte del
conocimiento esperado y puede ser evaluado.

### Profundización opcional

Contenido adicional destinado a alumnos que quieran avanzar más. No debe
convertirse implícitamente en materia obligatoria.

Esta clasificación debe ser visible cuando sea relevante.

------------------------------------------------------------------------

## 11. Evaluación acumulativa

Los tests frecuentes evalúan conocimiento próximo y obligan a mantener
el ritmo.

Sin embargo, por sí solos no garantizan recuperación de contenidos
antiguos.

Por ello se mantiene como opción preferente un **examen final
acumulativo**.

Su función pedagógica es distinta:

-   recuperar contenidos de todo el semestre;
-   demostrar integración;
-   reforzar conexiones entre las primeras lessons y el sistema
    completo;
-   hacer visible al alumno cuánto ha progresado.

El examen final no es el principal mecanismo de evaluación, pero sí una
pieza obligatoria del sistema de evaluación.

Principio:

> Tests continuos para consolidación local + examen final para
> integración global.

### Ponderación oficial

La calificación final del curso se distribuye así:

  Componente                 Peso
  -------------------- ----------
  Asistencia              **10%**
  Participación           **20%**
  Exámenes continuos      **40%**
  Examen final            **30%**
  **Total**              **100%**

Los **exámenes continuos** corresponden al sistema de tests A/B/C/D
descrito en este contrato, agregados según las reglas académicas que se
definan para el cálculo de la nota.

La **participación** recoge la implicación efectiva del alumno en el
trabajo de aula: resolución de ejercicios, razonamiento, discusión y
contribución activa. No debe confundirse con mera presencia.

La **asistencia** mide presencia en las sesiones conforme a las reglas
académicas aplicables.

El **examen final** es acumulativo y representa el 30% de la nota final.

------------------------------------------------------------------------

## 12. Lesson 14 y capstone

La Lesson 14 puede utilizarse de forma distinta a una sesión estándar.

El capstone o problema abierto puede convertirse en trabajo autónomo del
alumno en lugar de intentar resolverlo íntegramente durante la sesión.

Una configuración válida es:

``` text
Profesor
→ explica el núcleo conceptual de L14
→ presenta el problema y los criterios

Alumno
→ implementa / resuelve el capstone de forma autónoma

Profesor
→ evalúa posteriormente los conceptos de L14
→ revisa decisiones y errores relevantes
```

La prioridad es evitar que la complejidad del capstone reduzca la
comprensión del núcleo conceptual de la lesson.

------------------------------------------------------------------------

## 13. Principios de diseño de los tests

Los tests deben medir comprensión, no memorización accidental.

Una batería de 10 preguntas debería combinar:

-   lectura de código;
-   predicción de comportamiento;
-   comprensión conceptual;
-   interpretación de resultados;
-   identificación de errores;
-   conexiones entre piezas del sistema.

Debe evitarse que todos los tests puedan aprobarse memorizando
literalmente el documento.

Cuando una lesson combine Python y trading, el test debería comprobar
ambos cuando sean parte de sus objetivos.

------------------------------------------------------------------------

## 14. Consecuencias para el diseño del material

Cada lesson debe poder funcionar en dos modos:

### Modo presencial

El profesor selecciona:

-   los ≈20 minutos de presentación de mayor valor;
-   los ejercicios que resolverá conjuntamente;
-   qué partes quedan para consolidación autónoma.

### Modo autónomo

El alumno debe poder recorrerla sin depender totalmente del profesor.

Por ello, el material debe ser:

-   autocontenido;
-   navegable;
-   suficientemente explicativo;
-   verificable mediante ejercicios/validadores;
-   explícito sobre qué es núcleo, requerido y opcional.

El diseño web, los notebooks y los validadores no son complementos:
forman parte de la infraestructura pedagógica del curso.

------------------------------------------------------------------------

## 15. Regla de carga

El trabajo autónomo es parte deliberada del curso, pero su carga debe
ser controlada.

Una lesson no debe trasladar sistemáticamente a casa todo aquello que no
cabe por exceso de contenido.

La secuencia correcta es:

``` text
definir qué debe aprender el alumno
→ decidir qué requiere presencia
→ decidir qué puede consolidar solo
→ dimensionar el material
```

No:

``` text
añadir contenido
→ impartir lo que quepa
→ mandar todo lo restante
```

El trabajo autónomo debe ser intencional y dimensionado.

------------------------------------------------------------------------

## 16. Política de calendario

El calendario debe distinguir entre:

-   `lesson`: unidad de contenido;
-   `session`: bloque presencial;
-   `assessment`: test asociado a una o varias lessons.

No existe necesariamente una relación 1:1 entre los tres.

Ejemplos válidos:

``` text
1 session → 1 lesson
2 sessions consecutivas → 2 lessons → 1 assessment posterior
1 lesson autónoma → consolidación en session posterior → assessment después
1 session → consolidación de lesson previa + introducción de nueva lesson
```

Esta separación debe reflejarse en cualquier futuro calendario o
manifest del curso.

------------------------------------------------------------------------

## 17. Invariantes pedagógicos

### PED-01 --- Tiempo presencial ≠ contenido total

No es necesario completar toda la lesson durante los ≈50 minutos.

### PED-02 --- El alumno trabaja entre sesiones

La consolidación autónoma forma parte explícita del modelo docente.

### PED-03 --- La evaluación genera continuidad

Cada lesson obligatoria debe tener una comprobación posterior,
individual o agrupada.

### PED-04 --- No se examina antes de permitir consolidación

Una doble sesión no genera un test inmediato entre sus dos partes.

### PED-05 --- Las lessons autónomas son evaluables

Que el profesor no imparta todo el contenido en directo no elimina la
responsabilidad del alumno.

### PED-06 --- El profesor concentra el presencial en el mayor valor marginal

Intuición, razonamiento, arquitectura, errores y feedback tienen
prioridad sobre práctica mecánica.

### PED-07 --- El alumno conoce el contrato

Antes de trabajar una lesson debe quedar claro:

-   qué debe saber;
-   qué debe hacer;
-   qué es obligatorio;
-   qué es opcional;
-   cuándo aproximadamente se comprobará.

### PED-08 --- La evaluación acumulativa tiene una función distinta

Los tests cortos consolidan el corto plazo; el examen final obligatorio
mide integración y retención global.

### PED-09 --- La ponderación de evaluación es estable

La evaluación oficial es: **10% asistencia + 20% participación + 40%
exámenes continuos + 30% examen final**.

------------------------------------------------------------------------

## 18. Arquitectura pedagógica objetivo

``` text
ANTES / ENTRE SESIONES
Trabajo autónomo pendiente
        ↓
INICIO DE SESIÓN
Test de lessons ya consolidadas
        ↓
PRESENTACIÓN
≈20 min de núcleo conceptual
        ↓
PRÁCTICA GUIADA
≈20 min de ejercicios seleccionados
        ↓
DESPUÉS DE LA SESIÓN
Completar material + practicar + consolidar
        ↓
SIGUIENTE OPORTUNIDAD VÁLIDA
Test A/B/C/D
```

Para dobles sesiones:

``` text
Lesson A
→ Lesson B consecutiva
→ trabajo autónomo posterior
→ test A+B en el siguiente encuentro compatible
```

------------------------------------------------------------------------

## 19. Decisión final

El curso adopta un modelo de **flipped consolidation**, no un modelo en
el que todo debe enseñarse presencialmente.

La sesión presencial sirve para:

> orientar → explicar → practicar → desbloquear.

El trabajo posterior sirve para:

> completar → repetir → consolidar.

El test siguiente crea el incentivo para:

> recuperar → demostrar → mantener continuidad.

Este ciclo es la unidad pedagógica real del curso.

------------------------------------------------------------------------

## 20. Relación con otras fuentes

Este documento es la **golden source pedagógica** del proyecto y es
autoritativo para:

-   duración y estructura pedagógica de las sesiones;
-   trabajo autónomo;
-   tests entre lessons;
-   tratamiento de dobles sesiones;
-   lessons autónomas;
-   sistema y ponderación de evaluación;
-   función pedagógica del examen final.

Si cualquier otra fuente del proyecto entra en conflicto con este
documento sobre cuestiones pedagógicas o de evaluación, **prevalece este
contrato pedagógico** y la otra fuente debe corregirse.

Si otra fuente del proyecto indica **40 minutos por clase**, debe
actualizarse a **aproximadamente 50 minutos**.

El contrato de infraestructura GitHub regula publicación y seguridad, no
metodología docente.
