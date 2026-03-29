# Guion de la presentacion: Que es Python - Clase 1

Este documento esta pensado para acompanar a la presentacion visual.

La regla es esta:

- La presentacion muestra el mapa mental.
- Tu voz aporta intuicion, ejemplos y matices.
- Este guion te ayuda a no dejarte nada importante.

No esta organizado por tiempo, sino por slide o bloque conceptual del HTML.

## Idea central de toda la clase

La frase mas importante de la sesion es:

**Python no es magia. Python es un programa que lee texto, lo interpreta y produce una accion real.**

Si el alumno sale con esa intuicion bien asentada, ya tiene el marco correcto para entrar en Jupyter y aprender sintaxis sin sentir que todo es arbitrario.

## Como usar este guion

En cada bloque tienes:

- `Objetivo`: que debe entender el alumno.
- `Que decir`: frases o ideas que conviene verbalizar.
- `Aclaraciones`: cosas importantes que no estan en pantalla o no deben cargarse en la slide.
- `Pregunta util`: pregunta breve para activar la atencion.
- `Idea de salida`: la frase mental con la que deberian quedarse.

## Slide 0: Hero y apertura

Corresponde al hero de la presentacion y a la idea "Python es un programa que lee texto".

### Objetivo

Romper la sensacion de misterio y fijar el tono de la clase: vamos a entender que pasa por debajo, no solo a memorizar sintaxis.

### Que decir

- "Hoy no quiero que memoriceis comandos. Quiero que entendais que esta pasando cuando escribes codigo y pulsas ejecutar."
- "La intuicion correcta es mucho mas valiosa que aprender veinte palabras nuevas de golpe."
- "Ademas lo vamos a conectar con trading desde el principio: leer datos, calcular algo y automatizar una decision sencilla."

### Aclaraciones

- No alargues demasiado esta apertura.
- No entres aun en detalles de tokenizacion o AST.
- La funcion de esta slide es dar confianza y direccion.

### Pregunta util

- "Cuando pulsas ejecutar, quien crees que esta leyendo ese codigo?"

### Idea de salida

- "Hay un programa real leyendo mi texto."

## Slide 1: Tu primer programa en 30 segundos

Corresponde a `#demo` y al bloque "Editor en vivo".

### Objetivo

Que el alumno vea que un `.py` no es una caja negra: es texto plano que Python puede ejecutar.

### Que decir

- "Esto es solo texto. Un `.py` no es un objeto misterioso."
- "Lo puedes abrir con un editor cualquiera y ver exactamente lo que hay."
- "Lo importante no es el fichero por si solo, sino que existe otro programa que sabe leerlo."
- "Cuando hago `python hola.py`, estoy invocando a ese programa."

### Aclaraciones

- Corrige explicitamente una confusion tipica: el fichero no hace nada por si mismo.
- Si borrases Python del ordenador, el fichero seguiria ahi, pero ya no habria nadie que lo interpretara.
- El editor en vivo no es para ensenar sintaxis compleja. Es solo para que vean causa y efecto.

### Pregunta util

- "Si dejo el fichero y quito Python del ordenador, que pasa?"

### Idea de salida

- "Un `.py` es texto; Python lo lee y produce el resultado."

## Slide 2: Que es un programa

Corresponde a `#programa`, al diagrama de flujo y al bloque "Dos formas de leer el mismo codigo".

### Objetivo

Separar tres capas:

- lo que escribe una persona,
- lo que entiende Python,
- y lo que acaba ejecutando la maquina.

### Que decir

- "Un programa es una lista ordenada de instrucciones que una maquina puede ejecutar."
- "La CPU no entiende Python ni espanol ni ingles; trabaja con una capa mucho mas basica."
- "Los lenguajes de programacion existen para que nosotros podamos escribir instrucciones legibles."
- "Python hace de traductor entre una capa humana y una capa ejecutable."

### Aclaraciones

- No hace falta entrar en arquitectura de computadores.
- Basta con que entiendan que la CPU no ve conceptos como `print` o `if`.
- La comparacion entre CPU y Python sirve para que entiendan que una misma cadena de caracteres puede verse de formas muy distintas segun quien la procese.

### Sobre `print`

Este punto conviene verbalizarlo bien:

- Primero `print` es solo texto.
- Luego el tokenizador lo reconoce como una pieza del lenguaje.
- Despues el parser detecta que se esta usando en una llamada a funcion.
- Mas tarde, al ejecutar, Python resuelve el nombre `print` y encuentra el comportamiento asociado en sus built-ins.

### Aclaraciones tecnicas importantes

- No digas que `print` es una keyword. En Python es una built-in, no una palabra reservada.
- No digas que la CPU "entiende print". Quien entiende `print` es Python.

### Pregunta util

- "La CPU ve `print("hola")` como nosotros lo vemos?"

### Idea de salida

- "La CPU ve bits; Python ve estructura con significado."

## Slide 3: Python es, el mismo, un programa

Corresponde a `#cpython`.

### Objetivo

Separar con claridad:

- Python como lenguaje,
- Python como interprete instalado,
- y tu fichero `.py` como entrada de ese interprete.

### Que decir

- "Cuando instalas Python, no instalas una idea abstracta. Instalas un ejecutable real."
- "Ese ejecutable ocupa disco, tiene bytes y corre como cualquier otro programa."
- "Tu fichero `.py` necesita a ese interprete para cobrar vida."

### Analogias que funcionan bien

- "El `.py` es la receta; Python es el cocinero."
- "El `.pdf` necesita un lector; el `.py` necesita un interprete."

### Aclaraciones

- Puedes mencionar que la implementacion habitual se llama CPython porque esta escrita principalmente en C.
- No hace falta entrar en otras implementaciones salvo que te pregunten.
- El objetivo no es una clase de historia de Python, sino dejar clara la relacion entre fichero e interprete.

### Pregunta util

- "Que instalas exactamente cuando instalas Python?"

### Idea de salida

- "Python no es solo un lenguaje. Es tambien el programa que lo ejecuta."

## Slide 4: Que hace CPython por dentro

Corresponde a `#pipeline`, al pipeline visual, al mini-tokenizador y al detective de errores.

### Objetivo

Dar un mapa mental simple del recorrido interno del codigo y usarlo para explicar mejor los errores.

### Que decir

- "CPython no pasa del texto a la pantalla en un solo salto."
- "Primero separa piezas, luego intenta entender la estructura, luego prepara la ejecucion y finalmente ejecuta."
- "No quiero que memoriceis todas las cajas; quiero que podais distinguir donde esta fallando algo."

### Como explicar cada etapa

#### Tokenizacion

- "Rompe el texto en piezas reconocibles: nombres, operadores, parentesis, strings."
- "Aqui todavia no entiende del todo el programa; simplemente deja de ver una cadena plana."

#### Parsing y AST

- "El parser intenta encajar los tokens en la gramatica de Python."
- "Si lo logra, construye una estructura interna del programa."
- "Esa estructura es el AST: una representacion de forma, no un texto para humanos."

#### Bytecode

- "El AST se transforma en bytecode."
- "El bytecode no es codigo binario nativo de la CPU."
- "Es un lenguaje intermedio que entiende la maquina virtual de Python."

#### VM

- "La VM vive dentro del proceso de Python."
- "Ejecuta el bytecode instruccion a instruccion."
- "Aqui es donde aparecen muchos errores de ejecucion."

#### Output

- "Si todo va bien, la ejecucion produce un efecto real: texto, calculos, ficheros, red, graficos..."

### Como explicar los errores

Esta es una de las partes mas utiles de toda la clase.

- `SyntaxError`: "No entiendo la frase que me has escrito."
- `NameError`: "Entiendo la frase, pero ese nombre no existe."
- `TypeError`: "La frase se entiende, pero esa operacion no tiene sentido con esos tipos."
- `ZeroDivisionError`: "La sintaxis esta bien, pero lo que intentas hacer falla al ejecutar."

### Aclaraciones

- `prnt("hola")` no es `SyntaxError`. La sintaxis es valida; el nombre simplemente no existe.
- No conviertas el AST o el bytecode en una obsesion tecnica. Solo necesitas intuicion.
- La utilidad real del pipeline es mejorar el debugging mental del alumno.

### Preguntas utiles

- "Que tipo de error es peor para empezar: uno de sintaxis o uno de ejecucion?"
- "Donde diriais que falla `prnt("hola")`?"

### Idea de salida

- "Un error puede venir de no entender el codigo o de fallar al ejecutarlo. No es lo mismo."

## Slide 5: El REPL y Jupyter

Corresponde a `#jupyter`, al REPL, al mini-REPL real y al mock de notebook.

### Objetivo

Ensenar que Jupyter no es "otra cosa distinta", sino una forma visual, comoda y didactica de trabajar con el mismo interprete.

### Que decir

- "El REPL es una conversacion con Python."
- "Escribes una linea, la ejecuta, devuelve algo y espera la siguiente."
- "Jupyter toma esa misma logica y la convierte en un espacio de trabajo mas visual."
- "En un notebook puedes mezclar texto, codigo, resultados y graficos sin salir del mismo sitio."

### Como explicar el kernel

- "El kernel es el proceso que mantiene vivas las variables, imports y funciones."
- "Si defines `spread` en una celda, otra celda puede usarlo porque ambas hablan con el mismo kernel."
- "Si reinicias el kernel, desaparece ese estado."

### Aclaraciones

- No presentes Jupyter como un lenguaje nuevo.
- No digas que cada celda es un programa completamente aislado.
- El notebook es ideal para aprendizaje porque deja pensar, probar, corregir y documentar a la vez.

### Conexiones utiles con trading

- "Es el formato perfecto para jugar con un snapshot, cambiar un precio y ver inmediatamente que cambia."
- "Nos interesa porque en trading cuantitativo pensar y probar rapido vale mucho."

### Pregunta util

- "Por que una variable creada en una celda existe en la siguiente?"

### Idea de salida

- "Jupyter es la conversacion con Python convertida en laboratorio."

## Slide 6: Por que Python y no otro

Corresponde a `#porque`.

### Objetivo

Justificar Python como eleccion del curso sin venderlo como moda ni como lenguaje "facil sin mas".

### Que decir

- "No usamos Python por casualidad."
- "Lo usamos porque reduce friccion al aprender, pero sigue siendo util para construir cosas reales."
- "Es legible, tiene un ecosistema enorme y encaja especialmente bien con datos, analisis, notebooks y automatizacion."

### Como contarlo sin sonar a propaganda

- "Python no es perfecto para todo."
- "Pero para este curso tiene un equilibrio excelente entre claridad conceptual y potencia real."
- "Nos deja centrarnos en ideas de trading y automatizacion sin pelearnos demasiado con la sintaxis."

### Sobre las empresas

- No hace falta detenerse mucho en cada logo.
- Usalos como prueba social ligera: Python se usa en contextos serios.
- El mensaje no es "si Netflix lo usa, entonces es bueno", sino "esto no es una herramienta de juguete".

### Pregunta util

- "Que preferimos en una primera clase: un lenguaje que impresione o uno que nos deje pensar mejor?"

### Idea de salida

- "Python es amable para aprender y serio para construir."

## Slide 7: Cierre y puente al notebook

Corresponde a `#cierre`.

### Objetivo

Cerrar el mapa mental y dejar al alumno preparado para entrar al notebook con sentido, no a ciegas.

### Que decir

- "Ya no entramos al notebook solo para probar cosas. Entramos sabiendo que hay un interprete, un flujo y una logica detras."
- "Ahora toca pasar de entender el mapa a usarlo."
- "Lo siguiente sera crear variables, calcular un spread y automatizar una regla simple de mercado."

### Aclaraciones

- El cierre no debe sentirse como final de tema, sino como puente.
- Es importante que el alumno note continuidad: HTML primero para entender, notebook despues para tocar.

### Frase de salida recomendable

- "Aprender a programar no consiste en leer mucho sobre codigo. Consiste en tocarlo, romperlo y arreglarlo."

### Idea de salida

- "Ya tengo el mapa mental; ahora toca practicar."

## Conceptos ampliados para repaso

Esta parte sirve mas como material de apoyo para el alumno que como guion oral.

## 1. Programa, lenguaje e interprete

Un `lenguaje de programacion` es una forma de escribir instrucciones legibles para humanos.

Un `programa` es un conjunto de instrucciones ejecutables.

Un `interprete` es un programa que sabe leer instrucciones escritas en cierto lenguaje y coordinar su ejecucion.

En esta clase:

- Python como lenguaje es la sintaxis y las reglas.
- Python como programa es el interprete instalado.
- Tu `.py` es la entrada que ese interprete lee.

## 2. Que pasa con `print("hola")`

Cuando escribes `print("hola")`, ocurre algo parecido a esto:

1. Hay texto en un fichero o en una celda.
2. CPython separa ese texto en tokens.
3. El parser comprueba si la secuencia respeta la gramatica.
4. Si la sintaxis es valida, construye una estructura interna del programa.
5. Esa estructura se prepara para ejecucion.
6. La VM ejecuta las instrucciones.
7. El runtime termina produciendo salida real.

## 3. Que es un token

Un token es una unidad lexica reconocible por el lenguaje.

Ejemplos:

- `print`
- `(`
- `)`
- `"hola"`
- `+`

La tokenizacion todavia no entiende el programa completo, pero deja de ver una cadena plana de caracteres.

## 4. Que es el AST

AST significa `Abstract Syntax Tree`.

Es una representacion estructural del programa que usa el interprete para razonar sobre la forma del codigo.

Una forma intuitiva de verlo:

- no ve solo letras,
- ve "llamada a funcion" con nombre `print` y argumento `"hola"`.

## 5. Bytecode y codigo binario no son lo mismo

El `bytecode` es un lenguaje intermedio para la VM de Python.

El `codigo binario nativo` es el que entiende la CPU.

Por eso:

- CPython no traduce simplemente todo tu programa a instrucciones nativas de CPU y ya.
- Trabaja con una capa intermedia y luego la VM va ejecutandola.

## 6. Sintaxis frente a ejecucion

Un error de sintaxis significa que Python no puede entender correctamente la forma del programa.

Ejemplos tipicos:

- parentesis sin cerrar
- comillas sin cerrar
- estructura gramatical invalida

Un error de ejecucion significa que la forma del programa es valida, pero algo falla al llevarlo a cabo.

Ejemplos tipicos:

- usar una variable que no existe
- dividir entre cero
- mezclar tipos incompatibles

## 7. REPL, notebook y kernel

El `REPL` es una conversacion lineal con el interprete.

Un `notebook` organiza esa conversacion en celdas y anade salida visible, texto explicativo y narrativa.

El `kernel` es el proceso que mantiene el estado comun entre celdas.

## 8. Por que esto importa para trading

En trading algoritmico no basta con saber palabras sueltas de Python. Lo importante es poder:

- leer datos,
- calcular metricas,
- probar ideas rapido,
- automatizar reglas,
- inspeccionar resultados.

Python y Jupyter encajan especialmente bien en ese flujo.

## Errores de explicacion que conviene evitar

- No digas que `print` es una keyword.
- No digas que la CPU entiende Python directamente.
- No presentes Jupyter como otro lenguaje.
- No hagas pensar que el AST es algo que el alumno deba manipular ahora.
- No conviertas la clase en una clase de arquitectura de computadores.

## Checklist rapido para ti

- He dejado claro que un `.py` es texto plano.
- He diferenciado lenguaje, fichero e interprete.
- He explicado que Python instalado es un programa real.
- He separado bien `SyntaxError` y errores de runtime.
- He explicado que Jupyter reutiliza el mismo interprete mediante un kernel.
- He conectado el final con la practica inmediata del notebook.

## Cierre recomendado en una frase

**"Hoy no hemos aprendido mucha sintaxis todavia, pero hemos ganado algo mejor: un mapa mental correcto para que todo lo demas tenga sentido."**
