# Plan maestro - Curso de Trading Algoritmico 2026

## 1. Vision del curso

Curso de 15 clases de 40 minutos sobre trading algoritmico con enfoque pragmatico, visual y orientado a construir. El objetivo no es dar una formacion academica lenta, sino ensenar a pensar como alguien que:

- entiende como funciona un mercado electronico,
- sabe automatizar ideas con Python,
- puede apoyarse en LLMs, tools y agentes,
- y conecta microestructura, ejecucion, pricing y market making con ejemplos reales.

El tono del curso sera:

- directo,
- sin paja,
- con intuicion antes que formalismo,
- con ejemplos practicos,
- y con notebooks/htmls disenados para mantener atencion y velocidad.

---

## 2. Principios pedagogicos

### Regla de diseno por clase
En 40 minutos, cada clase debe resolver una pregunta central.

Cada sesion tendra esta estructura:

1. **Contexto** - que problema resuelve la clase y por que importa.
2. **Intuicion** - pocas ideas, muy claras.
3. **Demo** - visual o simulacion.
4. **Mini practica** - tocar parametros, modificar codigo, responder algo.
5. **Takeaways** - 3 ideas finales y puente a la siguiente clase.

### Que evitamos

- teoria larga sin aplicacion,
- demasiadas definiciones seguidas,
- notebooks con bloques enormes de texto,
- matematicas innecesarias antes de tiempo,
- ejemplos abstractos sin mercado detras,
- dependencia ciega en IA.

### Que maximizamos

- intuicion,
- causalidad,
- visualizacion,
- simulaciones cortas,
- continuidad entre clases,
- capacidad de prototipar rapido.

---

## 3. Formato del repo

Se propone una carpeta por clase:

- `first-lesson/`
- `second-lesson/`
- `third-lesson/`
- `fourth-lesson/`
- `fifth-lesson/`
- `sixth-lesson/`
- `seventh-lesson/`
- `eighth-lesson/`
- `ninth-lesson/`
- `tenth-lesson/`
- `eleventh-lesson/`
- `twelfth-lesson/`
- `thirteenth-lesson/`
- `fourteenth-lesson/`
- `fifteenth-lesson/`

### Estructura base por carpeta
Cada clase deberia intentar seguir esta estructura minima:

- `README.md` - objetivo y guia rapida.
- `presentation/` - HTML pedagogico y guion si la clase lo necesita.
- `lesson.ipynb` o `lesson.html` - pieza principal de trabajo.
- `data/` - datos locales de apoyo.
- `assets/` - imagenes, csv, gifs o json.
- `exercises/` - ejercicios guiados o mini build path.
- `solutions/` - opcional o embebido al final del notebook.

### Convencion por tipo de clase

- Clases de Python, microestructura, ejecucion y modelizacion: **Jupyter Notebook**.
- Clases mas visuales o tipo presentacion interactiva: **HTML + p5.js**.

### Patron recomendado para clases foundation
Para las primeras clases de programacion, el patron que mejor encaja es:

1. **Presentacion pedagogica** - mapa mental e intuicion.
2. **Notebook principal** - demo corta y construccion guiada.
3. **Ejercicios** - progresion paso a paso para tocar codigo.

Este patron ya funciona especialmente bien para clases 1 y 2, donde el alumno todavia necesita mucho contexto antes de construir solo.

---

## 4. Estilo de materiales

### Notebooks
Los notebooks deben ser:

- cortos,
- muy interactivos,
- con markdown minimo,
- con celdas pequenas,
- con visuales inmediatos,
- y con una practica accionable.

#### Plantilla sugerida de notebook
1. Titulo
2. Objetivo de la clase
3. Por que importa
4. Intuicion en 3-5 bullets
5. Demo o simulacion
6. Mini ejercicio
7. Solucion o pista
8. Resumen final

### HTMLs
Los HTMLs deben servir para:

- introducir conceptos visualmente,
- ensenar ideas con animaciones,
- controlar el ritmo narrativo,
- y evitar saturar al alumno con demasiado codigo cuando no toca.

Uso recomendado:

- `p5.js` para animaciones,
- controles simples para cambiar parametros,
- graficos que respondan a inputs,
- lenguaje visual tipo desk / trading terminal cuando ayude.

---

## 5. Syllabus detallado de las 15 clases

## Clase 1 - Python basico
**Formato:** Presentacion HTML + Notebook + Ejercicios

### Objetivo
Llevar a una persona desde cero absoluto a entender que Python es texto que interpreta un lenguaje capaz de automatizar tareas.

### Debe cubrir

- que es un programa,
- que significa ejecutar codigo,
- variables,
- tipos basicos,
- listas,
- diccionarios,
- `for loops`,
- `if`,
- funciones,
- automatizacion de tareas simples.

### Intuicion clave
Python no es "programar por programar", sino escribir instrucciones repetibles para quitar trabajo manual.

### Estructura pedagogica recomendada
1. Presentacion HTML para fijar que Python es un programa real que lee texto.
2. Notebook corto para pasar de variables y listas a una mini lectura de mercado.
3. Cuaderno de ejercicios guiados para construir un sistema toy paso a paso.

### Demo sugerida

- recorrer una lista de precios,
- calcular medias simples,
- procesar trades ficticios,
- crear una funcion que compute spread o PnL basico.

### Takeaway
El alumno sale sabiendo leer y tocar codigo sin miedo.

---

## Clase 2 - Python OOP + librerias
**Formato:** Presentacion HTML + Notebook + Ejercicios

### Objetivo
Explicar primero que es una libreria y por que `import pandas as pd` cambia lo que uno puede hacer. Despues, pasar de listas y diccionarios a objetos propios de trading.

### Debe cubrir

- que es una libreria,
- que hace un `import`,
- idea practica de `pandas`,
- clase,
- objeto,
- atributos,
- metodos,
- crear un mini sistema con objetos tipo `Order`, `Trade` y `PositionTracker`.

### Secuencia ideal
1. Librerias como "codigo que otros ya escribieron".
2. Ejemplo practico con `pandas` sobre una tabla simple.
3. Limite de trabajar solo con listas y diccionarios.
4. Diferencia entre usar una libreria y crear nuestro propio objeto.
5. Construccion de un mini sistema OOP de trading.

### Demo sugerida

- leer una tabla simple con `pandas`,
- crear una clase `Order`,
- anadir un metodo como `notional()`,
- crear una clase `Trade`,
- actualizar `cash`, `position` y `equity` con `PositionTracker`.

### Estructura pedagogica recomendada
1. Presentacion HTML para explicar intuitivamente que es una libreria, que hace `import` y por que las clases ayudan a organizar codigo.
2. Notebook principal con un bloque corto de `pandas` y una transicion clara hacia OOP.
3. Cuaderno de ejercicios guiados donde el alumno construye el mini proyecto paso a paso.

### Takeaway
El alumno entiende que el codigo puede ampliarse con librerias y organizarse con objetos reutilizables.

---

## Clase 3 - Vibe Coding, LLMs, tools y agentes
**Formato:** HTML

### Objetivo
Dar contexto de trabajo moderno en 2026: que es una LLM, que es una tool y como cambia la forma de construir codigo.

### Debe cubrir

- que es una LLM,
- que sabe hacer bien,
- que hace mal,
- que es una tool,
- que es un agente,
- como encaja esto en flujos reales de coding.

### Enfoque
No convertirlo en una clase de "prompts". Debe ser una clase sobre productividad con criterio.

### Mensajes clave

- la IA acelera, no reemplaza criterio,
- hay que verificar outputs,
- el contexto importa,
- un buen programador con agentes construye mucho mas rapido.

### Demo
La experimentacion local con CODEX se deja fuera del repo principal o como apoyo informal.

---

## Clase 4 - Microestructura de mercado
**Formato:** Notebook

### Objetivo
Introducir microestructura con foco crypto, idealmente BTC, usando datos actualizados aunque no sean real time.

### Debe cubrir

- bid,
- ask,
- spread,
- mid price,
- volumen,
- imbalance,
- LOB,
- diferencia entre liquidez visible y negociacion.

### Enfoque
Crypto/BTC para hacerlo mas tangible y actual.

### Demo sugerida

- snapshot de libro,
- calculo de spread y mid,
- imbalance por niveles,
- visualizacion de profundidad,
- como cambia la lectura del mercado con el libro.

### Datos
Usar datos actualizados de BTC guardados localmente para reproducibilidad.

---

## Clase 5 - Tipos de ordenes y matching behavior
**Formato:** Notebook interactivo o HTML interactivo

### Objetivo
Ensenar como se envian y se cruzan ordenes en un mercado electronico.

### Debe cubrir

- limit orders,
- market orders,
- IOC,
- FOK / FAK / Fill and Kill segun convencion elegida,
- matching behavior,
- venue logic si da tiempo.

### Requisito importante
Debe haber simulacion visual con capacidad de:

- poner limit orders,
- quitarlas,
- lanzar market orders,
- observar fills parciales o completos,
- ver como reacciona el libro.

### Intuicion clave
La forma de enviar la orden cambia el coste, la probabilidad de ejecucion y el riesgo.

---

## Clase 6 - LOB practice: pipeline de ciencia de datos
**Formato:** Notebook

### Objetivo
Montar el pipeline conceptual y practico para modelar variables del libro.

### Debe cubrir

- framing del problema,
- definicion de target,
- features del LOB,
- datos sinteticos + datos reales,
- train/test split temporal,
- leakage,
- baseline simple.

### Objetivos de prediccion posibles

- imbalance,
- volumen,
- probabilidad de fill.

### Enfoque
Esta clase es el **pipeline**. Menos foco en resultados, mas en como se construye bien.

---

## Clase 7 - LOB practice: ejemplos concretos
**Formato:** Notebook

### Objetivo
Aplicar el pipeline anterior a ejemplos concretos y comparar salidas.

### Debe cubrir

- ejemplo de prediccion de imbalance,
- ejemplo de prediccion de volumen,
- ejemplo de probabilidad de fill,
- comparacion entre feature sets,
- lectura critica de resultados.

### Enfoque
La clase 6 prepara. La clase 7 ensena ejemplos completos y rapidos.

---

## Clase 8 - Execution Algorithms: VWAP practice I
**Formato:** Notebook

### Objetivo
Introducir el problema de predecir volumen para construir un schedule tipo VWAP.

### Debe cubrir

- que es VWAP,
- por que importa el perfil intradia de volumen,
- prediccion de volumen con:
  - media,
  - mediana,
  - media de un dia concreto,
  - mediana de un dia concreto,
- intuicion de benchmark.

### Enfoque
Primero baselines simples y entendibles.

### Demo sugerida

- curvas intradia de volumen,
- comparar lunes contra otros dias,
- construir una curva de participacion simple.

---

## Clase 9 - Execution Algorithms: VWAP practice II
**Formato:** Notebook

### Objetivo
Dar el paso desde baseline simple a un modelo mas dinamico de prediccion de volumen.

### Debe cubrir

- entrenamiento con historico de dias,
- ejemplo entrenando solo con lunes para predecir lunes,
- senal basada en los 5 minutos anteriores,
- ventana rolada,
- comparacion entre baseline y modelo dinamico,
- impacto sobre el schedule de ejecucion.

### Intuicion clave
No basta con mirar medias historicas; el flujo reciente tambien informa.

---

## Clase 10 - Bonos del gobierno
**Formato:** HTML + p5.js

### Objetivo
Explicar la logica economica y matematica basica de los bonos soberanos de forma visual y trader-friendly.

### Debe cubrir

- que es un bono,
- cupon,
- tenor,
- precio,
- yield / YTM,
- relacion precio-yield,
- formula de precio,
- mercado primario vs secundario,
- rol de bancos centrales,
- como las expectativas de tipos afectan valoraciones,
- DV01 como sensibilidad a 1 bp de cambio en YTM.

### Enfoque narrativo sugerido
1. Que promete un bono.
2. Por que tiene sentido economico.
3. Como se calcula el precio.
4. Que significa YTM.
5. Por que cuando sube yield cae precio.
6. Que hace el banco central y por que importa.
7. Que mide DV01.

### Demo visual

- slider de yield,
- cambio de precio con yield,
- curvas visuales,
- flujos de cupones,
- sensibilidad DV01.

---

## Clase 11 - RFQs y curva de probabilidad de cierre
**Formato:** Notebook

### Objetivo
Modelar la probabilidad de cierre de una RFQ en funcion del spread y otras features de cliente.

### Debe cubrir

- que es un RFQ,
- spread como comision o margen cobrado,
- relacion spread-probabilidad de cierre,
- tiers de cliente,
- diferencia entre tier 1, 2 y 3,
- curvas monotonicas de cierre,
- modelo exponencial inicial,
- evolucion a regresion logistica con mas features.

### Narrativa deseada

- tier 1: cliente dificil de cerrar, mas competitivo,
- tier 3: cliente que acepta peores precios,
- dealers ajustan precios segun calidad del flujo,
- la curva de cierre debe tener sentido economico.

### Salida ideal
Comparar curvas de cierre por tier y mostrar como cambian con el spread.

---

## Clase 12 - Market making intro
**Formato:** HTML + p5.js

### Objetivo
Introducir el market making con foco en inventario, utilidad y aversion al riesgo.

### Debe cubrir

- que hace un market maker,
- de donde sale el PnL,
- adverse selection,
- riesgo de inventario,
- funcion de utilidad,
- utilidad CARA,
- parametro `gamma`,
- como `gamma` afecta cotizaciones.

### Enfoque
Primero intuicion muy visual. Nada de entrar demasiado pronto en derivaciones.

### Demo visual

- inventario moviendose en el tiempo,
- cotizaciones que se ajustan,
- cambio de `gamma`,
- efecto sobre agresividad / conservadurismo del market maker.

---

## Clase 13 - Market making Avellaneda-Stoikov
**Formato:** Notebook o HTML hibrido con apoyo de simulacion

### Objetivo
Dar intuicion, explicar el origen del modelo y aterrizarlo en la formula y simulaciones.

### Debe cubrir

- intuicion del problema,
- mencion a la HJB,
- explicacion leve de control optimo estocastico,
- reservation price,
- optimal spread,
- rol de inventario,
- simulaciones del modelo.

### Restriccion pedagogica
No convertirla en una clase de derivacion matematica larga. La matematica aparece para legitimar el modelo, no para dominar el tiempo.

### Resultado esperado
El alumno entiende de donde sale la formula y que hace cada parametro.

---

## Clase 14 - Exam I
**Formato:** Quiz

### Estado
Se deja para el final del proyecto.

### Idea preliminar
Quiz conceptual corto con foco en:

- Python,
- microestructura,
- ordenes,
- ejecucion,
- bonos,
- RFQ,
- market making.

---

## Clase 15 - Exam II
**Formato:** Quiz

### Estado
Se deja para el final del proyecto.

### Idea preliminar
Segunda parte del examen o quiz complementario con algo mas de interpretacion y razonamiento.

---

## 6. Hilo conductor del curso

El curso debe sentirse como una historia continua:

1. Aprendes a programar desde cero.
2. Aprendes a usar librerias y a modelar objetos.
3. Aprendes a construir mas rapido con LLMs y agentes.
4. Entiendes como funciona el mercado por dentro.
5. Entiendes como se mandan ordenes y que consecuencias tiene cada una.
6. Empiezas a modelar datos del libro.
7. Pasas de microestructura a prediccion.
8. Conectas prediccion con ejecucion.
9. Te mueves a pricing y cierre en RFQ.
10. Cierras con market making y control de inventario.

---

## 7. Stack recomendado del proyecto

### Para notebooks

- Python
- `pandas`
- `numpy`
- `matplotlib`
- `plotly` si compensa interactividad
- `scikit-learn`
- widgets ligeros cuando ayuden a explorar

### Para visuales HTML

- HTML/CSS/JS
- `p5.js`
- controles simples con sliders y botones

### Para datos

- CSVs locales reproducibles
- snapshots y series historicas pequenas
- mezcla de datos reales y sinteticos cuando sea pedagogicamente mejor

---

## 8. Reglas de diseno de contenido

### Markdown dentro de notebooks
Cada bloque de texto debe ser:

- corto,
- accionable,
- con pocas palabras,
- sin rodeos,
- y con una intuicion clara.

### Celdas de codigo
Deben ser:

- pequenas,
- con nombres claros,
- con una sola idea por celda,
- faciles de modificar en directo.

### Visuales
Cada concepto importante deberia tener al menos uno de estos:

- grafico,
- tabla,
- simulacion,
- animacion,
- slider.

---

## 9. Decisiones importantes ya tomadas

### Decisiones pedagogicas

- Nivel de entrada: **cero absoluto**.
- Tono: **pragmatico, rapido, no academico**.
- Curso disenado para que el alumno **entienda y toque**.
- IA tratada como herramienta de productividad, no como magia.

### Decisiones por clase

- Clase 1 seguira el patron presentation -> notebook -> ejercicios.
- Clase 2 seguira el mismo patron y usara un mini proyecto OOP de trading.
- Clase 3 sera HTML centrado en LLMs, tools y agentes.
- Clase 4 tendra foco crypto, preferiblemente BTC, con datos actualizados.
- Clase 5 incluira matching behavior y simulacion interactiva.
- Clases 6 y 7 usaran mezcla de datos reales y sinteticos.
- Clases 8 y 9 separaran baselines de volumen y modelo dinamico.
- Clase 10 sera visual con HTML + p5.js.
- Clase 11 hara modelizacion monotonic de cierre por spread y tier.
- Clase 12 introducira utilidad y CARA antes del modelo formal.
- Clase 13 conectara intuicion, HJB y formula con simulacion.
- Clases 14 y 15 quedan para el final.

---

## 10. Riesgos del proyecto y mitigacion

### Riesgo 1 - Meter demasiado en cada clase
**Mitigacion:** una idea central por sesion.

### Riesgo 2 - Material demasiado tecnico demasiado pronto
**Mitigacion:** intuicion primero, formula despues.

### Riesgo 3 - Notebooks lentos o aburridos
**Mitigacion:** celdas cortas, visuales rapidos, interaccion frecuente.

### Riesgo 4 - IA como gimmick
**Mitigacion:** ensenar validacion, contexto y criterio.

### Riesgo 5 - Falta de continuidad entre clases
**Mitigacion:** reutilizar objetos, datasets y estilo visual a lo largo del curso.

---

## 11. Roadmap de construccion del repo

### Fase 1 - Planificacion

- cerrar el plan maestro,
- definir naming final de carpetas,
- decidir datasets base por bloque,
- fijar stack minimo.

### Fase 2 - Estructura del repo

- crear carpetas `first-lesson` a `fifteenth-lesson`,
- crear esqueletos de `README.md`, `data/`, `assets/`,
- dejar plantilla base para notebook/html.

### Fase 3 - Bloque foundation

- clase 1,
- clase 2,
- clase 3.

### Fase 4 - Bloque microestructura y ordenes

- clase 4,
- clase 5.

### Fase 5 - Bloque LOB + data science + execution

- clases 6, 7, 8 y 9.

### Fase 6 - Bloque rates / RFQ / market making

- clases 10, 11, 12 y 13.

### Fase 7 - Evaluacion

- clases 14 y 15.

---

## 12. Plantilla de objetivos por clase

Cada clase deberia arrancar con algo asi:

- **Que vas a entender hoy**
- **Que vas a tocar hoy**
- **Que deberias poder explicar al final**

Y deberia cerrar con:

- **3 ideas que te llevas**
- **1 error tipico**
- **1 puente a la siguiente clase**

---

## 13. Siguiente iteracion recomendada

Una vez aprobado este plan maestro, el orden ideal de trabajo es:

1. crear la estructura de carpetas de las 15 clases,
2. redactar un `README.md` breve para cada clase,
3. construir primero las clases 1, 2 y 3,
4. fijar datasets de BTC para las clases 4 a 9,
5. disenar los HTMLs visuales de las clases 10 y 12,
6. dejar la 13 para despues de tener bien armada la 12,
7. disenar examenes al final, no antes.

---

## 14. Conclusion

El curso tiene muy buena forma si se mantiene esta disciplina:

- una idea central por clase,
- intuicion antes que formalismo,
- visuales siempre que aporten,
- codigo pequeno y util,
- continuidad entre temas,
- y mentalidad de builder apoyado en IA.

Si se ejecuta bien, el alumno no solo aprendera conceptos de trading algoritmico. Tambien aprendera a **pensar**, **prototipar** y **explicar** mejor en un entorno realista de 2026.
