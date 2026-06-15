# Guion — Clase 1: De texto a máquina (y tu primer dato de mercado)

**Idea central:** tu código es texto; una máquina solo entiende 1s y 0s; Python es el puente — compila tu texto a *bytecode* y una máquina virtual lo interpreta. Entender ese viaje explica hasta los errores.

Presentación interactiva (Pyodide): hero + 5 bloques + cierre. ~20 min.

---

## Hero (2 min)
- **Objetivo:** fijar la pregunta de la clase: "esto que escribo, ¿cómo lo entiende la máquina?".
- **Acción en pantalla:** snapshot de mercado BTCUSDT; pulsa "Otro snapshot" para ver que los datos cambian.
- **Qué decir:** "Hoy no memorizamos comandos. Vamos a ver, con Python real en el navegador, cómo tu texto llega hasta los 1s y 0s de la CPU."
- **Salida:** "Hay un viaje del texto a la máquina; vamos a recorrerlo."

## Bloque 1 — Texto → 1s y 0s (4 min)
- **Objetivo:** la máquina solo entiende binario; tu texto es, por debajo, números.
- **Acción:** escribe en el campo (`buy`, tu nombre…) y muestra cómo cada carácter → `ord` → 8 bits. Luego pulsa "Animar el viaje de Python" y recorre los carriles compilado vs interpretado.
- **Qué decir:** "C traduce todo a binario de una vez, antes de ejecutar. Python es híbrido: compila tu texto a un intermedio, el *bytecode*, y una máquina virtual lo va interpretando. Compila y a la vez interpreta."
- **Riesgo:** no entrar en detalle de Unicode/UTF-8; basta "carácter → número → bits".
- **Salida:** "La máquina solo ve 1s y 0s; algo tiene que traducir."

## Bloque 2 — El viaje de una línea (5 min)
- **Objetivo:** hacer tangible el pipeline real: tokens → AST → bytecode.
- **Acción:** con `mid = (bid + ask) / 2`, pulsa "Compilar" y recorre las tres pestañas. Señala en el bytecode `LOAD_NAME`, `BINARY_OP`, `STORE_NAME`. Cambia la línea (p.ej. un `if`) y recompila.
- **Qué decir:** "Esto no es un dibujo: lo está calculando Python ahora mismo. Tu línea se parte en piezas (tokens), se ordena en un árbol (AST) y se compila a estas instrucciones (bytecode) que ejecuta la VM."
- **Riesgo:** no explicar cada opcode; quédate con "estas son las instrucciones de la máquina virtual".
- **Salida:** "Texto → tokens → árbol → bytecode → ejecución."

## Bloque 3 — Escribe, ejecuta, observa (4 min)
- **Objetivo:** que escriban Python real y vean causa-efecto.
- **Acción:** ejecuta el editor; usa los presets (Variables/Lista y for/Diccionario). Conecta: "lo que escribes aquí pasa por el viaje del bloque 2".
- **Qué decir:** "Variables, listas, diccionarios. El diccionario es clave: así modelaremos una orden de mercado."
- **Salida:** "Sé escribir y ejecutar Python básico."

## Bloque 4 — Los errores son pistas (4 min)
- **Objetivo:** desmitificar el error y conectarlo con el viaje.
- **Acción:** los 4 retos en orden. En cada uno, primero ejecuta para ver el error, deja que lo arreglen, aparece la pista; al resolver, avanza al siguiente.
- **Qué decir:** "SyntaxError = ni siquiera compiló (falló antes del bytecode). NameError/TypeError/ZeroDivisionError = compiló, pero la VM tropezó al ejecutar. El tipo de error te dice en qué fase mirar."
- **Riesgo:** no convertirlo en taxonomía; son 4 ejemplos. Recordar: `prnt("x")` sería NameError, no SyntaxError.
- **Salida:** "Un error te dice dónde y en qué fase falló."

## Bloque 5 — Del dato a la decisión (5 min)
- **Objetivo:** mostrar el esqueleto dato → cálculo → decisión.
- **Acción:** snapshot interactivo + rule builder ("si spread ≤ 50 → comprar"); cambia el mercado y ve cómo cambia la decisión; muestra el mismo algoritmo en el editor de la derecha y ejecútalo.
- **Qué decir:** "Esto es un algoritmo: lee un dato, calcula, decide. En el notebook lo guardaremos como un `dict` — el primer ladrillo del motor que construiremos todo el curso."
- **Riesgo:** dejar claro que la regla es un toy, no una estrategia real.
- **Salida:** "Dato → cálculo → decisión es la estructura de cualquier algo."

## Cierre (1 min)
- Recoge: texto → bytecode → VM → 1s/0s; el error te dice si falló compilando o ejecutando; dato→cálculo→decisión.
- Manda abrir el notebook de construcción.

## Checklist
- [ ] He mostrado texto → bits con un ejemplo en vivo.
- [ ] He diferenciado compilado vs interpretado y dicho que Python compila a bytecode + VM.
- [ ] He compilado una línea de verdad y enseñado tokens/AST/bytecode.
- [ ] He conectado SyntaxError = compilación vs runtime = ejecución.
- [ ] He construido dato → cálculo → decisión en vivo.
- [ ] He cerrado mandando al notebook.
