# Guion — Clase 2: Libraries + OOP para Trading

La presentacion tiene 3 bloques + hero + cierre. Duracion total: 20 minutos.

## Idea central

**Una libreria amplia tu caja de herramientas. Una clase organiza las tuyas. Un tracker convierte eventos en estado.**

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
Abrir con el contraste: script plano vs OOP. El alumno debe sentir el problema antes de ver la solucion.

### Accion en pantalla
- Senala los dos bloques de codigo en el hero: el problema (6 variables, duplicacion) y la solucion (dict de trackers).
- Senala los 3 iconos: Import, Class, State.

### Que decir
- "En Lesson 1 todo funcionaba con variables sueltas. Hoy vamos a ver que pasa cuando intentas escalar ese codigo."
- "La clase tiene tres partes: ver el problema de escalar, transformar dicts en clases, y jugar con un tracker que mueve estado."

### Riesgo
- No presentar OOP como algo academico o teorico.
- No hacer que Lesson 1 parezca un error — era la decision correcta para empezar.

### Salida
- "El problema no es que el codigo no funcione — es que no escala."

---

## Bloque 1: El problema de escalar (5 min)

### Objetivo
Que el alumno sienta fisicamente la duplicacion cuando anade activos al script plano.

### Accion en pantalla
- Empieza en "1 activo (BTC)". Senala que el script y el OOP parecen equivalentes.
- Pulsa "+ ETH". Senala como el script duplica variables y globals.
- Pulsa "+ SOL". Senala los contadores: 6 variables vs 3 objetos, 2 bloques duplicados vs 0.
- Lee el insight en voz alta.

### Que decir
- "Con un activo, ambos estilos funcionan igual. La diferencia aparece al escalar."
- "El script duplica: mismas variables, mismo patron, distinto prefijo."
- "Con OOP, anadir un activo es una linea en un dict. La logica no cambia."
- "Este es exactamente el problema que visteis al final de Lesson 1: el buy_volume que mezclaba BTC y ETH."

### Riesgo
- No hacer un analisis O(n) formal. Basta con la intuicion "cada activo duplica el dolor".
- No presentar el script como codigo malo — era correcto para un activo.

### Salida
- "N activos con script = N bloques duplicados. Con OOP = N objetos, cero duplicacion."

---

## Bloque 2: Dict -> Class -> Object (5 min)

### Objetivo
Mostrar la transformacion visual de dict a clase a objeto. Que el alumno vea como las claves se convierten en atributos.

### Accion en pantalla
- Empieza en "Dict (Lesson 1)". Senala el diagrama SVG — dict resaltado.
- Pulsa "Class (molde)". Senala como las claves pasan a `self.xxx` en `__init__`, y notional/describe pasan a ser metodos.
- Pulsa "Object (instancia)". Senala los dos objetos concretos (btc_order, eth_order) que nacen del mismo molde.
- Destaca la nota "La clase no complica — ordena."

### Que decir
- "Un dict guarda datos y nada mas. Para prototipar esta bien."
- "El problema es cuando notional y describe se repiten por fuera. La clase los pone dentro."
- "La clase es el molde. El objeto es una instancia concreta con valores reales."
- "En Lesson 1 tu orden era `order['price']`. Ahora es `order.price`. Las claves se han convertido en atributos."

### Riesgo
- No abrir temas como herencia, polimorfismo o metaclases.
- No presentar `self` como algo que hay que entender profundamente ahora. "self es el propio objeto" basta.
- No invalidar Lesson 1: el dict era correcto alli.

### Salida
- "La clase junta datos y comportamiento. El objeto es una instancia concreta."

---

## Bloque 3: Playground interactivo (7 min)

### Objetivo
Unir las piezas: crear una orden, disparar trades, ver como el tracker acumula estado.

### Accion en pantalla
- Configura una orden (BTCUSDT, buy, 100000, 0.10).
- Pulsa "Compra demo". Senala cash, position, equity.
- Pulsa "Venta parcial". Senala como cash sube y position baja.
- Pulsa "Secuencia completa" para ver dos trades encadenados.
- Cambia el mark price y ve como equity se mueve.
- Senala el panel de codigo equivalente.

### Que decir
- "Order organiza datos y comportamiento."
- "Trade representa un evento con consecuencia economica."
- "PositionTracker acumula consecuencias y convierte eventos en estado."
- "Fijate: nadie toca `_cash` directamente. Todo pasa por `apply_trade()`. Eso es encapsulacion."
- "En el notebook vais a construir esto paso a paso."

### Riesgo
- No atascarse explicando self, __init__ o __repr__ en detalle. Eso va en el notebook.
- No vender el tracker como motor de trading real. Es un mini sistema pedagogico.

### Salida
- "Cuando aparece estado, el codigo empieza a parecerse a un sistema."

---

## Cierre (1 min)

### Objetivo
Cerrar con la secuencia memorable y preparar notebook + bridge a Lesson 3.

### Que decir
- "Hoy no habeis aprendido toda OOP. Habeis aprendido por que aparece."
- "Import -> Tabla -> Order -> Trade -> Estado. Esa es la secuencia."
- "En el notebook vais a escribir estas ~60 lineas a mano."
- "Siguiente clase: y si pudieras describir lo que quieres en espanol y que un LLM genere esas clases? Eso es vibe coding."

### Salida
- "Tool -> data -> object -> event -> state."

---

## Checklist rapido

- [ ] He mostrado la comparacion script vs OOP con 1, 2 y 3 activos.
- [ ] He hecho la transformacion dict -> class -> object paso a paso.
- [ ] He usado el playground para mostrar cash, position, equity en vivo.
- [ ] He conectado con Lesson 1 (buy_volume mezclado, dict con symbol).
- [ ] He plantado el bridge a Lesson 3 (vibe coding con LLMs).
- [ ] No he abierto herencia, polimorfismo ni metaclases.
