# Lesson 5 · Tu cartera recuerda lo que has ejecutado

## Objetivo

En L3 conectaste funciones mediante imports. En L4 construiste `Fill`, que describe
una ejecución y devuelve su flujo. Ahora construirás una cartera que **utiliza ese
Fill y conserva caja y unidades**. Después un libro le proporcionará el precio
con el que consultar su valor. Sin comisiones; precios en USD/unidad, caja en USD.

## De L4 a L5

Si llegan diez ejecuciones más, ¿seguirías escribiendo sumas en `main.py`?

| En L4, main… | En L5, PositionTracker… |
| --- | --- |
| Suma los flujos. | Los acumula con `apply_fill()`. |
| Resta los tamaños. | Conserva las unidades en `position`. |
| Combina resultados. | Mantiene el estado entre llamadas. |

`main.py` sigue conectando las piezas; `Fill` sigue calculando cada flujo.

## Archivos

| Archivo | Tu trabajo |
| --- | --- |
| `models.py` | Reutilizar tu `Fill` de L4, sin cambiarlo. |
| `portfolio.py` | Completar constructor, `apply_fill` y `equity`. |
| `book.py` | Completar `mid`; `Level`, ordenación e `imbalance` están proporcionados. |
| `main.py` | Importar, crear objetos y comprobar cada paso. No definir clases aquí. |
| `solutions/solucion.md` | Consultar los cuatro archivos completos y las variantes. |

## Cómo trabajar

Trae el `models.py` que completaste en L4 a esta carpeta. Si no terminaste L4,
el archivo incluido es su referencia resuelta, generada desde la misma solución;
úsala conscientemente, sin perder tu intento. No hay otra clase `Fill` que escribir.

Abre juntos los archivos de `exercises`. Cada apartado coincide con un comentario
`TODO · Ejercicio N.a`. Sustituye los `pass`, guarda y ejecuta `python main.py`
desde esa carpeta después de cada paso. El programa está incompleto al principio:
añade solo las llamadas del paso que ya puedes probar. Cada ejecución de terminal
crea objetos nuevos; dentro de una ejecución conserva el mismo `tracker`.
Si haces una copia personal, conserva juntos los cuatro `.py` y sus nombres.

**Núcleo presencial:** ejercicios 1–4, unos 20 min incluyendo integración.
**Consolidación requerida:** 5–6, unos 10 min. **OPTIONAL:** 7, unos 5 min.
Predice cada salida antes de ejecutar; consulta la solución tras intentarlo.

## Ejercicio 1 · Una instancia que conserva estado

### 1.a · Prepara `PositionTracker` en `portfolio.py`

Completa `__init__`: guarda el argumento `cash` en `self.cash` y cero en
`self.position`. `cash=0.0` es el valor por defecto si no pasas efectivo inicial.
Cada instancia debe tener sus propios atributos. No uses atributos de clase.

### 1.b · Importa en `main.py`

Fuera de `main()`, importa `Fill` desde `models` y `PositionTracker` desde
`portfolio`, como hacías en L4. Dentro de `main()` utilizarás esas clases.

### 1.c · Crea y observa

Crea `tracker = PositionTracker(cash=1000)` y `buy = Fill('buy', 101, 2)`.
Imprime `tracker.cash` y `tracker.position` con etiqueta `Inicio:`.
Antes de ejecutar: ¿crear `buy` cambiará la cartera? Predice caja y posición.

<details>
<summary>Comprobar después de predecir y ejecutar</summary>

Esperas **1000 y 0** (0.0 es equivalente).
El fill describe una ejecución; todavía no has pedido al tracker contabilizarla.

</details>

## Ejercicio 2 · Un objeto utiliza el comportamiento de otro

### 2.a · Completa `apply_fill(self, fill)` en `portfolio.py`

Suma a `self.cash` el resultado de **`fill.cash_flow()`**. No vuelvas a calcular
precio por tamaño: esa responsabilidad ya pertenece al `Fill` de L4.
`+=` suma al valor anterior. Si `fill.side` es `'buy'`, suma `fill.size` a
`self.position`; si es `'sell'`, réstalo. Completa ambas patas antes de probar.

Aquí `self` es la cartera y `fill` es la ejecución recibida. Durante la llamada a
`fill.cash_flow()`, el `self` de ese otro método es el fill. No son el mismo objeto.
Este método modifica atributos; no necesita devolver otra cartera.

### 2.b · Aplica desde `main.py`

Llama a `tracker.apply_fill(buy)` e imprime caja y posición con etiqueta `Compra:`.
Esperas **798 y 2**: 1000 − 101 × 2 y 0 + 2.
No escribas `tracker = tracker.apply_fill(buy)`: asignarías `None` a `tracker`.
¿Quién calculó el flujo y quién lo acumuló?

## Ejercicio 3 · Consultar no es operar

### 3.a · Completa `equity(self, mark)` en `portfolio.py`

Devuelve caja más posición multiplicada por `mark`. `mark` es el precio por unidad
que eliges para valorar las unidades restantes: USD + unidades × USD/unidad.
Usa `return`; no cambies atributos ni guardes el mark en la cartera.
La equity es el valor total, no el beneficio. Para compararla con el capital inicial,
en este escenario sin otros movimientos restarías 1000.

### 3.b · Consulta desde `main.py`

Imprime `tracker.equity(100)` y `tracker.equity(105)` con etiqueta `Valoraciones:`.
Después imprime caja y posición con `Estado intacto:`.
Predice los dos valores y el estado final. ¿Cambió el dinero o solo su valoración?

<details>
<summary>Comprobar después de predecir y ejecutar</summary>

Esperas **998 y 1008**, porque 798 + 2 × 100 = 998 y 798 + 2 × 105 = 1008.
El estado sigue en **798 y 2**. Solo cambió el precio usado para valorar.

</details>

## Ejercicio 4 · Acumula en la misma cartera

### 4.a · Añade la venta en `main.py`

Crea `sell = Fill('sell', 103, 1)` y aplícalo al mismo `tracker`.
Imprime caja, posición y `equity(100)` con etiqueta `Venta:`.
Esperas **901, 1 y 1001**: 798 + 103, 2 − 1 y 901 + 1 × 100.
No reinicies la cartera. Volvemos explícitamente a mark 100: consultar antes a 105
no guardó ese precio. Caja 901 no significa pérdida 99: conservas una unidad.

Estos fills son ejecuciones confirmadas proporcionadas como datos.
Todavía no simulamos su ejecución contra un libro ni afirmamos que se pueda vender
a 103 contra un bid de 99.

## Ejercicio 5 · Conecta un libro con la cartera

### 5.a · Importa, crea y lee en `main.py`

Importa `Level` y `OrderBook` desde `book`. Un `Level(price, size)` guarda el precio
y tamaño de un nivel; su lista (`bids` o `asks`) indica el lado.
Crea `OrderBook([Level(98, 1), Level(99, 2)], [Level(101, 3)])` y guárdalo en `book`.
El constructor proporcionado ordena compras de mayor a menor precio y ventas
al revés. No necesitas modificarlo.

Primero guarda `best_bid = book.bids[0]`; después imprime `best_bid.price` con
`Mejor bid:`. Esperas **99**. `[0]` recupera un objeto; `.price` lee su atributo.
El libro **contiene** niveles. La cartera **utiliza** fills, sin tener que guardarlos.

### 5.b · Completa `mid` en `book.py`

En L3, `describe` obtenía bid y ask de diccionarios. Aquí lees los precios de
objetos `Level`: el cálculo `(bid + ask) / 2` y la ausencia indicada por `None`
conservan su significado. Cambia la organización de los datos.

`@property`, ya colocado, ejecuta el método al leer `book.mid`, sin paréntesis.
Si falta cualquiera de los dos lados, devuelve `None` antes de acceder a `[0]`.
Si existen ambos, lee el `.price` del primer nivel de cada lado y devuelve su media.
Con este libro esperas **100.0**, obtenido como (99 + 101) / 2.

### 5.c · Valora solo si existe referencia, en `main.py`

Guarda `mark = book.mid`. Si es `None`, imprime `Sin referencia para valorar`;
en otro caso imprime `tracker.equity(mark)` con `Valoración con libro:`.
Esperas **1001.0**. El mid sirve como referencia; no garantiza poder ejecutar a él.

Repite la comprobación con `one_side = OrderBook([Level(99, 2)], [])` y su mid.
Debes obtener el mensaje de ausencia, sin llamar a `equity(None)` ni sustituirlo
por cero. El `if` pertenece a `main.py`, que conecta las piezas.

## Ejercicio 6 · Comprueba la propiedad y prepara L6

### 6.a · Compara guardar con recalcular, en `main.py`

Guarda `previous_mid = book.mid`, cambia `book.asks[0].price` a 103 e imprime
`previous_mid` y `book.mid` con `Guardado / actual:`. Antes de ejecutar, predice
cuál cambia y por qué. Usamos un único ask para conservar el orden.
Restaura su precio a 101 al terminar.

<details>
<summary>Comprobar después de predecir y ejecutar</summary>

Esperas **100.0 y 101.0**.
La variable guardó un número; la propiedad calcula otra vez con los datos actuales.

</details>

### 6.b · Consulta el método proporcionado

Imprime `book.imbalance(levels=1)` con `Imbalance:`. Compara los tamaños del primer
nivel de cada lado: (2 − 3) / (2 + 3) = **−0.2**. No uses los precios ni el segundo
bid. El signo negativo indica más tamaño vendedor en esa profundidad, no una orden.
En L6 una regla utilizará esta medida para decidir.

### 6.c · Conserva la guarda y comprueba los imports

Ejecuta por separado `python main.py` y `python -c "import main"` desde `exercises`.
El primero muestra las comprobaciones; el segundo no imprime nada, como en L3–L4.

## Ejercicio 7 · OPTIONAL · Variaciones sobre tus mismos objetos

Añade cada experimento al final de `main()`. No es necesario para avanzar.

### 7.a · Dos carteras independientes

Crea `a` y `b` con 1000. Aplica una compra de 2 a 101 solo a `a` y muestra ambos
estados. Esperas **798 / 2** y **1000 / 0**. ¿Qué `self` recibió la llamada?

### 7.b · Consultar dos veces frente a aplicar dos veces

En una cartera nueva `probe` con 1000, aplica `buy` una vez. Consulta dos veces
`equity(100)`: ambas dan **998**. Aplica el mismo `buy` otra vez y muestra el estado:
**596 / 4**. Cada llamada contabiliza una ejecución; no hay deduplicación automática.

### 7.c · Otra profundidad, mismos niveles

Con el libro restaurado, compara `imbalance(levels=1)` y `imbalance(levels=2)`.
Esperas **−0.2 y 0.0**: con dos niveles, compras suma 1 + 2 y ventas suma 3.
Cambiar la consulta no cambia el contenido del libro.

## Criterio de cierre y continuidad

Puedes seguir `main.py → PositionTracker → Fill.cash_flow()` y explicar dónde
cambia el estado. También puedes seguir `book.mid → número → tracker.equity(mark)`
sin confundir valoración con operación. En L6 cambiará la regla de decisión sobre
el mercado; estas responsabilidades seguirán separadas.
