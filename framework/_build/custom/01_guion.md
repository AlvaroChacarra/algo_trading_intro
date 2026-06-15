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
- **2.3 Bytecode:** tabla en cristiano (LOAD bid, LOAD ask, súmalos, …) + botón "Ver bytecode" (`dis` real). "Son las instrucciones que ejecuta la máquina virtual."
- **2.4 VM → 1s/0s:** "La VM ejecuta el bytecode instrucción a instrucción; cada una acaba en operaciones binarias de la CPU. Resultado: 99975.0. Viaje cerrado."
- **2.5 Playground:** que escriban su propia línea (`spread = ask - bid`, un `if`…) y vean tokens/AST/bytecode en vivo. **Es real, lo calcula Python en el navegador.**
- **Riesgo:** no explicar cada opcode; quédate con "instrucciones de la VM".

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
- 4 retos en orden. **Engancha con el bloque 2:** "SyntaxError = no llegó ni a compilar; NameError/TypeError/ZeroDivisionError = compiló pero la VM tropezó." El tipo de error te dice en qué fase mirar.
- **Riesgo:** son 4 ejemplos, no una taxonomía.

## Bloque 5 · Tu primer algoritmo (5 min)
- Rule builder + editor con el algoritmo completo. "dato → cálculo → decisión. En el centro, la misma `mid` que seguimos desde el minuto uno."
- Cambia el mercado y ve cómo cambia la decisión. Recalca: la regla es un toy pedagógico.

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
