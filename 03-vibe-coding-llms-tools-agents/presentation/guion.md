# Guion — Clase 3: Vibe Coding, LLMs, Tools y Agentes

La presentacion tiene 3 bloques + hero + cierre. Duracion total: 20 minutos.

## Idea central

**Un LLM genera codigo token a token, sin saber si funciona. Un agente aniade herramientas al bucle. Tu trabajo es saber cuando confiar y cuando verificar.**

## Como usar este guion

Cada bloque tiene:
- `Objetivo`: que debe quedar claro.
- `Que decir`: frases clave.
- `Accion en pantalla`: que tocar o demostrar.
- `Riesgo`: errores de framing que evitar.
- `Salida`: frase mental de cierre.

---

## Hero (2 min)

### Objetivo
Conectar con Lesson 2 y abrir el cambio de paradigma: de escribir codigo a evaluar codigo generado.

### Accion en pantalla
- Senala los dos bloques: el codigo de L2 (PositionTracker escrito a mano) y el prompt en espanol.
- Senala los 3 iconos: LLM, Agente, Criterio.

### Que decir
- "En Lesson 2 escribisteis Order, Trade y PositionTracker a mano. Unas 60 lineas."
- "Hoy vamos a ver que pasa cuando le pides a una IA que genere esas mismas clases."
- "La clase tiene tres partes: como genera un LLM, que aniade un agente, y cuando confiar en lo que produce."

### Riesgo
- No vender la IA como magia ni como reemplazo del programador.
- No invalidar Lesson 2: escribir a mano era necesario para entender lo que la IA genera.

### Salida
- "La IA acelera, pero el criterio es tuyo."

---

## Bloque 1: Como piensa un LLM (7 min)

### Objetivo
Que el alumno vea que un LLM genera token a token, sin plan, y que el resultado es estocastico — mismo prompt, distinto output.

### Accion en pantalla
- Pulsa "Generar". Observa como los tokens aparecen uno a uno de izquierda a derecha.
- Senala el contador de tokens y la temperature.
- Pulsa "Generar otra vez" con la misma temperature. Senala que el output cambia.
- Sube la temperature a 0.8. Genera de nuevo. Senala las diferencias (mas verboso, nombres distintos, posible bug).
- Lee el panel explicativo.

### Que decir
- "Un LLM no piensa como tu. No tiene un plan de principio a fin."
- "Predice el siguiente token mas probable dado lo anterior. Y lo concatena."
- "Temperature baja: mas predecible. Temperature alta: mas creativo pero mas errores."
- "Fijate: mismo prompt, resultado diferente. Eso se llama comportamiento estocastico."
- "Por eso dos personas pueden pedir lo mismo y recibir codigo distinto."

### Riesgo
- No entrar en softmax, embeddings ni arquitectura de transformers. "Predice el siguiente token" basta.
- No presentar temperature alta como algo malo per se — es util para explorar.

### Salida
- "Un LLM predice tokens. No calcula, no razona, no verifica."

---

## Bloque 2: LLM vs Agente (6 min)

### Objetivo
Mostrar la diferencia entre un LLM (genera texto) y un agente (usa el LLM + herramientas en un bucle).

### Accion en pantalla
- Empieza en "Solo LLM". Senala el diagrama: tu -> LLM -> texto.
- Senala que las herramientas estan desactivadas (opacas).
- Pulsa "LLM + Agente". Senala el bucle: tu -> LLM -> tools -> resultado.
- Senala que las herramientas se activan (leer, escribir, ejecutar, buscar).
- Lee los dos ejemplos de codigo: prompt simple vs instruccion con ejecucion.

### Que decir
- "Un LLM recibe texto y devuelve texto. No ejecuta nada. No sabe si funciona."
- "Un agente usa el LLM como cerebro pero ademas puede hacer cosas: leer archivos, escribir codigo, ejecutar tests."
- "La diferencia es el bucle: pensar, actuar, observar, repetir."
- "Cuando usas Claude Code, ChatGPT con herramientas o Cursor — eso es un agente."
- "El LLM solo tiene una pasada. El agente tiene un bucle."

### Riesgo
- No entrar en ReAct, chain-of-thought ni frameworks especificos.
- No presentar agentes como infalibles — el bucle puede iterar sobre errores.

### Salida
- "LLM = una pasada de texto. Agente = bucle con herramientas."

---

## Bloque 3: Cuando confiar, cuando verificar (5 min)

### Objetivo
Dar al alumno un framework practico para calibrar confianza en codigo generado por IA.

### Accion en pantalla
- Senala el semaforo: verde, amarillo, rojo.
- Pulsa "Verde". Senala el ejemplo de boilerplate (__repr__, __str__).
- Pulsa "Amarillo". Senala el ejemplo de logica financiera (apply_trade). Destaca que un error de signo = perdidas.
- Pulsa "Rojo". Senala el ejemplo de seguridad. Destaca hardcoded secrets.
- En el panel derecho: deja que los alumnos busquen el bug. Da 30 segundos.
- Revela la solucion: `self._position += trade.size` deberia ser `-=` para ventas.

### Que decir
- "No todo el codigo merece el mismo nivel de revision."
- "Verde: boilerplate mecanico. Si parece bien, probablemente lo esta."
- "Amarillo: logica de negocio. Aqui un bug puede pasar desapercibido. Siempre verifica con un ejemplo numerico."
- "Rojo: seguridad, autenticacion, operaciones irreversibles. Nunca copies de una IA sin revision experta."
- "El bug del tracker es clasico: la IA copia el patron del bloque de arriba sin invertir el signo."

### Riesgo
- No dar la impresion de que la IA siempre falla. La mayoria del codigo esta bien.
- No simplificar demasiado: el semaforo es un framework, no una regla absoluta.

### Salida
- "La IA acelera. Tu criterio protege."

---

## Cierre (1 min)

### Objetivo
Cerrar con la secuencia y preparar el notebook donde aprenderan los patrones que la IA usa.

### Que decir
- "Hoy habeis entendido como genera un LLM, que aniade un agente, y cuando confiar."
- "LLM -> temperature -> agente -> semaforo -> evaluar. Esa es la secuencia."
- "En el notebook vais a aprender los patrones que la IA usa al generar: try/except, type hints, @property, comprehensions."
- "Siguiente clase: ya sabeis Python, OOP y como trabajar con IA. Toca datos reales: microestructura de BTC."

### Salida
- "La IA genera. Tu evaluas. El mercado no perdona errores."

---

## Checklist rapido

- [ ] He mostrado la generacion token a token con variacion estocastica.
- [ ] He diferenciado LLM (una pasada) de agente (bucle con herramientas).
- [ ] He usado el semaforo verde/amarillo/rojo con ejemplos concretos.
- [ ] He dejado que los alumnos busquen el bug en el tracker.
- [ ] He conectado con Lesson 2 (las 60 lineas de clases).
- [ ] He plantado el bridge a Lesson 4 (datos reales de mercado).
- [ ] No he entrado en transformers, softmax, embeddings ni prompt engineering.
