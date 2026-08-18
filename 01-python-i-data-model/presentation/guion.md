# Guion — Clase 1: De texto a máquina

**Tesis:** escribimos una intención en una forma cómoda para humanos; CPython la transforma hasta que la CPU puede ejecutarla. Python sacrifica rendimiento y control frente a C++ a cambio de un ciclo de desarrollo muy rápido. Ese equilibrio alimentó un ecosistema que aprovecharemos durante todo el curso.

**Historia única:** libro de órdenes → `mid = (bid + ask) / 2` → texto a máquina → primitivas de Python → algoritmo → duplicación con ETH → funciones en L2.

**Formato:** documento interactivo (`python-i-data-model-doc.html`). Regla de la casa: **«lo cian se toca»**.

---

## §0 · Hero — reto y promesa (1 min)

- **Decir:** «Esto es un libro de órdenes. Al final de hoy habremos escrito un pequeño algoritmo capaz de leerlo, calcular información y tomar una decisión.»
- Señalar bid, ask y el hueco del mid.
- **Contrato:** «Antes quiero enseñaros durante cinco minutos qué ocurre entre escribir una línea de Python y que un procesador la ejecute.»
- **Disclaimer:** «No necesitáis memorizar tokens, AST o bytecode. Quiero que os quedéis con el modelo mental.»

## §1 · Texto → máquina, Python vs C++ y por qué Python (4 min)

Recorrer el scrolly con ritmo; tokens y AST son paradas visuales, no contenido para memorizar.

1. **Source:** intención formalizada como `mid = (bid + ask) / 2`.
2. **Tokens + AST:** CPython reconoce piezas y estructura las operaciones. No detenerse.
3. **Python bytecode:** instrucciones para la máquina virtual de Python; no son instrucciones nativas de x86-64 o ARM64.
4. **CPython VM:** ejecuta el bytecode.
5. **CPU:** ejecuta finalmente machine code nativo.

**Definición obligatoria:** «Python es el lenguaje. CPython es su implementación estándar y la que usa la mayoría: está escrita principalmente en C, analiza el source, lo compila a Python bytecode y ejecuta ese bytecode en su máquina virtual.»

Escribir o señalar: **CPython ≠ bytecode** y **Python source ≠ bytecode ≠ machine code**.

Comparar solo los dos pipelines:

- Python → compilador de CPython → Python bytecode → CPython VM → CPU.
- C++ → GCC/Clang/MSVC → machine code nativo → CPU.

No decir «Python es simplemente interpretado» ni «C++ no indica dónde está el error». C++ detecta muchos errores antes de ejecutar. La ventaja práctica de Python es el ciclo corto **write → run → inspect → fix**, reforzado por REPL, notebooks, celdas, tracebacks e introspección.

Cerrar con el círculo virtuoso: sintaxis + interactividad + experimentación → adopción → comunidad → librerías → más adopción. Presentarlo como una causa importante, no como explicación histórica única. Frase: **«Una de las grandes ventajas de Python no es solamente Python. Es todo el código que otra gente ya ha escrito para nosotros.»**

AI, máximo 20 segundos: el lenguaje natural puede elevar la interfaz con la que expresamos intención, pero debajo sigue siendo necesario transformarla en operaciones ejecutables. No afirmar que desaparecerán los lenguajes.

El simulador «tu propia línea» queda para exploración autónoma; no consumir tiempo presencial salvo pregunta del grupo.

## §2 · Variables y el mid (3 min)

- Mantener el gate predict-before-reveal.
- La división devuelve `float`; introducir `int`, `float` y `str` por reconocimiento.
- Step-through solo si aporta: nombres → valores → tipos.

## §3 · Listas y `for` (3 min)

- Lista = varios niveles/precios; `for` = recorrerlos.
- Dos vueltas con Paso y resto con Auto.
- Patrón: cursor que avanza + acumulador que actualiza.

## §4 · Diccionarios (2 min)

- Orden = `side + price + size`; acceso por nombre.
- Hover código↔ficha y añadir `venue`.

## §5 · `if/elif` (2 min)

- El spread convierte observación en decisión.
- Solo una rama; si coinciden condiciones, gana la primera. El orden importa.
- Los umbrales son didácticos, no una estrategia calibrada.

## §6 · Errores (2 min)

- NameError, TypeError e IndexError.
- Leer el traceback de abajo arriba.
- Conectar con el pipeline: SyntaxError antes de ejecutar; otros errores aparecen cuando la ejecución alcanza la operación problemática.
- Repetir: Python permite **escribir → ejecutar → observar → corregir**; no implica que C++ tenga malos diagnósticos.

## §7 · Algoritmo, quiz y puente (5 min)

- Ejecutar el algoritmo: dato → cálculo → decisión.
- **Decir:** «Ya sabemos suficiente Python para representar información del mercado, recorrerla, guardarla y tomar una decisión.»
- Cierre: «Quince líneas y ya tenemos la anatomía de un algoritmo: dato → cálculo → decisión.»
- Quiz como diagnóstico rápido.
- Añadir ETH → duplicación de variables y lógica → L2: funciones.
- Enviar al notebook y al trabajo autónomo.

## Presupuesto presencial

- Reto + texto a máquina + C++ + ecosistema + AI: **≈5 min**.
- Python práctico + algoritmo + quiz + puente: **≈15 min**.
- Presentación core: **≈20 min**. El dominio se consolida con ejercicios guiados, trabajo autónomo y test posterior.

## Checklist

- [ ] En 60 segundos saben qué construirán.
- [ ] Python = lenguaje; CPython = implementación/runtime estándar.
- [ ] CPython compila a bytecode y su VM lo ejecuta.
- [ ] Bytecode ≠ machine code.
- [ ] Python/CPython y C++ aparecen como pipelines correctos.
- [ ] C++ conserva su ventaja de detección preejecución; no se caricaturizan sus errores.
- [ ] Python se explica por `write → run → inspect → fix` y su entorno interactivo.
- [ ] Ecosistema como círculo virtuoso prudente; AI en menos de un minuto.
- [ ] Order book y `mid = (bid + ask) / 2` siguen siendo el hilo héroe.
- [ ] Se ejecuta el algoritmo y se conserva el puente a funciones en L2.
