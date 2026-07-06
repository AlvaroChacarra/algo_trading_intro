# Guion — Clase 1: De texto a máquina

**Idea central:** seguimos UNA línea —`mid = (bid + ask) / 2`— desde tu texto hasta los 1s y 0s, y al final la usas en tu primer algoritmo.

**Formato:** documento interactivo (`python-i-data-model-doc.html`). Tú haces scroll y narras; los alumnos lo siguen en su pantalla si quieren. Todo es autocontenido: funciona sin internet. Regla de la casa que conviene decir en el minuto 1: **"lo cian se toca"**.

---

## §0 · Hero — el reto (2 min)
- **Decir:** "Este es el libro de BTCUSDT, latiendo. ¿Cuánto vale *ahora mismo*? El punto medio. Yo lo calculo de cabeza; la máquina solo entiende 1s y 0s. Hoy cruzamos esa distancia."
- **Pantalla:** el libro pulsando solo; señala el hueco del mid.
- **Salida:** "Hay un viaje de mi texto a la máquina."

## §1 · Scrollytelling — el viaje (8 min)
Scroll **lento**: cada parada del panel es una idea. No corras; el panel espera.
- **0/5 texto:** "30 caracteres. Para Python, aún nada."
- **1/5 tokens:** "trocea en piezas con etiqueta — como separar palabras antes de entender la frase."
- **2/5 AST:** "el árbol pone orden: ¿qué se hace antes? Fíjate: tu paréntesis ya no existe — su trabajo era dar forma al árbol."
- **3/5 bytecode:** **antes de llegar, pregunta:** "¿cuántas instrucciones creéis que salen de esta línea? ¿4, 6, 9?" (son 6).
- **4/5 la VM:** deja correr la animación de la pila entera; si se la pierden, botón ↻ repetir.
- **5/5 binario:** "viaje cerrado: tu texto, ejecutándose como electricidad."
- **Nota de honestidad** (está en el doc): CPython hace más cosas; este es el esqueleto real.
- **Simulador "tu propia línea":** cede el teclado. Que escriban su línea, que la rompan (quitar un paréntesis, sumar texto y número → el TypeError es *exactamente* el de Python).

## §2 · Variables y el mid (4 min)
- **El gate:** el botón ▶ está bloqueado hasta que escriban su predicción. Insiste: "escribidla; vale equivocarse, no vale saltárselo".
- El `.0` del resultado es la lección: división → float, siempre.
- **Step-through:** pulsa Paso y narra cómo se puebla la memoria (nombres → valores → chips de tipo).

## §3 · Listas y for (3 min)
- El visualizador: cursor + acumulador. Usa Paso las dos primeras vueltas, Auto para el resto.
- Recalca el patrón: "acumulador que engorda + cursor que avanza = el 80% del análisis de datos".

## §4 · Diccionarios (2 min)
- Hover código↔ficha: "son la misma cosa vista dos veces".
- Ejecuta el `order["venue"]` y señala la ficha ganando el campo: "el dict está vivo".

## §5 · if/elif (3 min)
- Slider de spread: solo UNA rama iluminada cada vez; con spread=10 ambas condiciones son ciertas pero gana la primera — **el orden importa**.
- Honestidad (está en el doc): los umbrales son inventados; la estructura es la lección.

## §6 · Rompe código (3 min)
- Los tres desastres en orden: NameError, TypeError, IndexError. Regla de oro en voz alta: **"el traceback se lee de abajo arriba"**.
- Conecta con §1: "ya sabéis QUÉ falló y en qué fase".

## §7 · El algoritmo + quiz + puente (5 min)
- Ejecuta el algoritmo completo: dato → cálculo → decisión. "Quince líneas, y ya es un algoritmo de trading: primitivo, pero con la anatomía de uno profesional."
- **Quiz:** 5 A/B/C con feedback. Úsalo de diagnóstico: si fallan en bloque una pregunta, vuelve a esa sección.
- **Mapa del paquete:** "hoy pusisteis la primera piedra" — señala L1 iluminada y el arco entero.
- **Puente:** "añadid ETH esta noche… ¿cuántas variables duplicáis? Ese dolor se cura el próximo día."
- **Cierre:** manda al notebook (`01_build_exercises.ipynb`) y presenta el gimnasio (31 drills, dosis mínima declarada).

## Checklist (los innegociables)
- [ ] Python = programa que lee tu texto; el viaje tokens → AST → bytecode → VM.
- [ ] División → float (el gate del `.0`).
- [ ] Acumulador + cursor; dict por nombre; el embudo if/elif y el orden.
- [ ] Traceback de abajo arriba; los 3 errores del día.
- [ ] El algoritmo completo ejecutado y el puente a funciones (L2).
