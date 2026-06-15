# Guion — Clase 1: De texto a máquina (y tu primer dato de mercado)

**Idea central:** seguimos UNA línea —`mid = (bid + ask) / 2`— en su viaje desde tu texto hasta los 1s y 0s, y al final la usas en tu primer algoritmo. Hilo único, sin saltos.

Presentación interactiva (Pyodide). No te preocupes del tiempo: usa las diapositivas que necesites; el alumno debe salir con los 6 puntos del cierre.

---

## Hero · El reto (2 min)
- **Decir:** "Quiero que el ordenador calcule el `mid` de este libro con una línea. El problema: la CPU no entiende `mid = (bid + ask) / 2`, solo entiende 1s y 0s. Hoy seguimos ESA línea hasta el fondo."
- **Pantalla:** snapshot BTCUSDT; "Otro snapshot" para ver que cambia.
- **Salida:** "Hay un viaje de mi texto a la máquina."

## Bloque 1 · ¿Qué es Python? (dos diapositivas, 5 min)
- **1.1 — Python es un programa que lee tu texto.** "Un `.py` es texto plano. Python (CPython) es otro programa que lo lee, lo entiende y lo ejecuta. Sin Python, el archivo sigue ahí pero nadie lo lee."
- **1.2 — La máquina solo ve 1s y 0s.** Simulador texto→bits: escribe `bid`, ve carácter→`ord`→8 bits. **Clave (puente):** "convertir las LETRAS a bits es fácil, pero eso NO es ejecutar el programa; falta traducir el SIGNIFICADO. De eso va el resto."
- **Salida:** "La máquina solo ve binario; hay que traducir el significado de mi código."

## Bloque 2 · El viaje de tu línea (cinco diapositivas, 8 min)
Sigue el raíl Texto → Tokens → AST → Bytecode → VM → 1s/0s.
- **2.1 Tokens:** "Primero Python trocea la línea en piezas con significado: nombres, operadores, números. Aún no calcula nada." (chips de la línea).
- **2.2 AST:** árbol dibujado (suma bid+ask, luego divide entre 2, guarda en mid). Botón "Ver AST" → `ast.dump` real. "El árbol captura QUÉ se opera con qué."
- **2.3 Bytecode:** **primero pídeles que predigan** cuántos pasos de cálculo creen que hay (4/6/9 → 6); luego revela la tabla en cristiano (LOAD bid, LOAD ask, súmalos, …) + "Ver bytecode" (`dis` real). Caption: fíjate solo en LOAD/BINARY_OP/STORE; RESUME y RETURN son arranque y final.
- **2.4 VM → 1s/0s:** "La VM ejecuta el bytecode; el resultado, 99975, vive en memoria como bits (se muestran)." **Sé honesto:** la VM está escrita en C y es ella quien baja a binario; los decimales usan IEEE-754. Lo importante: todo acaba en 1s y 0s. Viaje cerrado.
- **2.5 Playground:** que **predigan el nº de tokens**, escriban su línea y vean tokens/AST/bytecode en vivo. **Es real, lo calcula Python en el navegador.**
- **Riesgo:** no explicar cada opcode; quédate con "instrucciones de la VM". Aviso de aula: Pyodide tarda unos segundos la primera vez y necesita internet; las diapositivas explicativas (chips/árbol/tabla) funcionan aunque falle.

## Bloque 3 · Compilar vs interpretar (dos diapositivas, 4 min)
- **3.1 Compilado (C):** "traduce TODO a binario una vez, antes de ejecutar. Rápido, pero hay que compilar y el binario es de esa máquina."
- **3.2 Python híbrido:** "compila a bytecode (lo que viste) y una VM lo interpreta al vuelo. Más lento que C, pero portable e interactivo — por eso va genial en Jupyter y para prototipar." Botón "Animar el viaje".
- **Salida:** "Compilar = texto→bytecode; interpretar = la VM ejecutándolo. Python hace las dos."

## Bloque 4 · El lenguaje, punto por punto (cinco diapositivas, 8-10 min)
Ve despacio, una idea por diapositiva, construyendo el bid/offer. Cada una tiene editor en vivo (ejecuta y modifica delante de ellos):
- **4.1 Variables:** `bid`, `ask`. "Un nombre que apunta a un valor."
- **4.2 Operaciones y tipos:** `spread`, `mid`. "Esta es LA línea del viaje. Fíjate: resta de enteros = entero; división = float."
- **4.3 Listas y for:** media de varios mids. "La lista guarda muchos; el for repite; total acumula."
- **4.4 Diccionarios:** una orden `{...}`. "Campos con nombre = una orden de verdad. En la clase 3 será una clase `Order`."
- **4.5 if/elif/else:** clasificar el mercado. "El programa decide. Cambia el spread y vuelve a ejecutar."

## Bloque extra · Errores son pistas (4 min)
- 4 retos en orden. **El output ya etiqueta la fase** ("⛔ Falló al COMPILAR" / "⛔ Falló al EJECUTAR"), así que la lección cala aunque acierten a la primera. Engancha con el bloque 2.
- **Riesgo:** son 4 ejemplos, no una taxonomía.

## Bloque 5 · Tu primer algoritmo (5 min)
- Rule builder + editor. **Cierra el hilo:** el `spread` da el *estado* del mercado; el `mid` —la línea que perseguimos todo el viaje— es ahora la *señal* que decide (`if mid <= 100000: buy`).
- Cambia el mercado y ve cómo cambia la decisión. Recalca: la regla es un toy pedagógico.

## Mini test (3 min)
- 5 preguntas A/B/C que cubren los 6 puntos. Feedback inmediato y resultado final. Úsalo para detectar qué no quedó claro antes de cerrar.

## Cierre (1 min)
Repasa los 6 puntos del panel y manda al notebook (guardar snapshot/orden como datos + medir presión).

## Checklist (los innegociables)
- [ ] (1) Qué es Python — programa que lee texto.
- [ ] (2) Cómo funciona de verdad — el viaje completo.
- [ ] (3) De texto a 1s/0s — tokens, AST, bytecode, VM.
- [ ] (4) Compilar vs interpretar.
- [ ] (5) Variables, listas, dicts, if, for — construyendo el bid/offer.
- [ ] (6) Tu primer algoritmo.
- [ ] (★) El error te dice si falló compilando o ejecutando.
