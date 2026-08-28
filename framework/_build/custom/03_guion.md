# Guion — Clase 3: Módulos y errores

**Idea central:** las funciones de L2 se mudan a **tu propio módulo** `order_book.py`, importable desde cualquier archivo, y aprenden a fallar con clase: `try/except` para el usuario, `raise` para el autor.

**Formato:** documento interactivo (`python-iii-modules-doc.html`), autocontenido, sin internet. "Lo cian se toca."

---

## §0 · Hero — el reto (2 min)
- **Decir:** "Vuestras siete funciones valen oro… y viven en un notebook: cerráis la pestaña y mueren. Hoy las convertimos en una librería — como cuando escribís `import pandas`, pero la librería sois vosotros."
- **Salida:** "Mi código puede ser importable."

## §1 · Scrollytelling — la mudanza (7 min)
El panel muestra **dos archivos**: el módulo a la izquierda, `main.py` a la derecha.
- **0/5 atrapadas:** "💀 al cerrar el notebook, se acabó."
- **1/5 nace el módulo:** "la mudanza es literal: pegar las funciones en un .py. Un módulo es solo eso."
- **2/5 import:** "el módulo entero, con apellido: `order_book.best_bid(book)`. El prefijo te dice de dónde viene cada cosa."
- **3/5 from…import:** "una función concreta, sin apellido. Más cómodo, menos contexto — los dos estilos son correctos."
- **4/5 dos vidas:** plantea el problema, sin resolverlo aún: importar no debería arrancar un backtest.
- **5/5 robustez:** "una librería seria no revienta: avisa. Ese es el segundo tema de hoy."

## §2 · Simulador de namespaces (3 min)
- Alterna los tres botones (`import` / `from…import` / `as`): **qué nombres existen** después de cada línea. Señala el `NameError` del panel central: "solo trajiste ese nombre".
- La regla práctica está en la nota; añade la prohibición: `from x import *` jamás.

## §3 · El error como ciudadano (6 min)
Tres escenarios sobre el mismo libro vacío, en orden:
- **Escenario 1 (sin red):** el traceback tiene **dos saltos** — novedad respecto a L1: tu archivo Y el módulo. Se sigue leyendo de abajo arriba. "…y el mensaje habla de max(), no de libros: críptico."
- **Escenario 2 (try/except):** "la red del usuario: cazas y das plan B."
- **Escenario 3 (raise):** "la elegancia del autor: fallar antes y en el idioma del dominio — 'libro vacío: no hay best_bid'". Esta es la diferencia entre código que funciona y una librería que da gusto usar.
- **Callback:** es la respuesta a la pregunta trampa que quedó abierta en L2.

## §4 · __main__ (3 min)
- En «Importar no debería arrancar mi programa», usa primero la versión rota. Pulsa **import backtest** y deja que Python recorra el archivo: define la función y después ejecuta el `print` y el backtest. El problema debe sentirse antes de enseñar `__name__`.
- Activa la versión con guard y repite las dos vidas: al importar, `__name__ = 'backtest'` y la condición es falsa; al ejecutar, `__name__ = '__main__'` y entra en `main()`.
- Cierre de una frase: **el módulo define; el script, además, arranca**.
- En el notebook lo comprobarán con dos archivos reales y `runpy`: no se copia el patrón sin haber observado el side effect.

## §5 · Quiz (3 min)
- 5 A/B/C: import, from-import, except, raise, __main__.

## §6 · Puente + mapa (2 min)
- Mapa: L1-L2 ✓, L3 iluminada.
- **Puente:** "mirad vuestras firmas: `best_bid(book)`, `add_order(book, …)` — el dato por un lado, las funciones por otro, y vosotros de repartidores. ¿Y si el dato supiera operar consigo mismo? En L5 la métrica sin argumentos se leerá como property: `book.best_bid`. Próxima clase nacen Order y Fill."
- Notebook + gimnasio (15 drills: imports, tracebacks de dos saltos, errores diseñados).

## Checklist
- [ ] Módulo = archivo .py; la mudanza es literal.
- [ ] import (con apellido) vs from…import (sin) vs alias.
- [ ] Traceback de dos saltos, leído de abajo arriba.
- [ ] try/except = red del usuario; raise = diseño del autor.
- [ ] __main__: el módulo define, el script hace.
- [ ] El guard aparece como solución a un import con side effects, no como fórmula aislada.
