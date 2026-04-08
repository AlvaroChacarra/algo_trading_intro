# Guion — Clase 5: Tipos de Ordenes y Matching Behavior

La presentacion tiene 3 bloques + hero + cierre. Duracion total: 20 minutos.

## Idea central

**El LOB es la subasta. Una orden es tu participacion en ella. La forma de participar cambia el coste, la probabilidad de ejecucion y el riesgo.**

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
Conectar con L4 y plantear la tension fundamental: market (ejecucion garantizada) vs limit (precio garantizado).

### Accion en pantalla
- Senala las dos tarjetas: market order (roja) y limit order (verde).
- Señala los contrastes: precio incierto vs ejecucion incierta, taker vs maker.
- Senala la pregunta central: "¿Por que no siempre usas una market order?"

### Que decir
- "En L4 visteis el LOB como estructura: bids, asks, spread, imbalance. Hoy lo ponemos en movimiento."
- "Cuando envias una orden, no es magia. Hay reglas sobre como se ejecuta. Eso es lo que vamos a aprender hoy."
- "La tension es esta: una market order garantiza que ejecutas, pero no sabes exactamente a que precio. Una limit order garantiza el precio, pero puede que no ejecute nunca."
- "La clase tiene tres partes: los tres tipos de ordenes, el simulador donde los vais a ver en accion, y el trade-off de coste."

### Riesgo
- No entrar todavia en la mecanica del matching. Solo plantar la tension.
- No hacer que L4 parezca incompleto — era la base necesaria para llegar aqui.

### Salida
- "El precio no es un hecho — y la ejecucion tampoco lo es."

---

## Bloque 1: Tipos de ordenes (6 min)

### Objetivo
Que el alumno entienda las garantias de cada tipo de orden y cuando usar cada uno.

### Accion en pantalla
- Senala las tres tarjetas: market (roja), limit (verde), IOC/FOK (amarilla).
- Para cada una, lee las caracteristicas clave en voz alta.
- Enfatiza los iconos: ✓ (garantia), ✗ (riesgo), $ (coste), ⏳ (tiempo).
- Senala el "cuando usarla" en cada tarjeta.

### Que decir
**Market order:**
- "Una market order dice: quiero ejecutar ahora. El precio que sea."
- "El libro te va llenando nivel a nivel: primero el best ask, luego el siguiente, hasta completar tu tamano."
- "El spread siempre lo pagas. Si tu orden es grande, ademas pagas slippage."
- "Eres taker: consumes liquidez que otros han puesto."

**Limit order:**
- "Una limit order dice: solo ejecuto si el mercado llega a mi precio."
- "Si pones un bid limit a 99.990 y el mejor ask esta a 100.010, tu orden se queda en el libro esperando."
- "Si el mercado baja y un vendedor acepta tu precio — fills."
- "Eres maker: aportas liquidez. En muchas plataformas te cobran menos fee, incluso te pagan."

**IOC y FOK:**
- "Son variantes de una market order con control sobre el residuo."
- "IOC: ejecuta lo que pueda ahora, cancela el resto. Nunca dejas residuo en el libro."
- "FOK: todo o nada. Si no hay liquidez para completar la orden, no ejecuta nada."
- "Las usareis mas en contextos institucionales, pero es importante conocerlas."

### Riesgo
- No entrar en variantes como GTC, GTD, MOO, MOC. Hoy solo market, limit, IOC, FOK.
- No confundir IOC con limit IOC (algunos exchanges permiten limit IOC). Simplificamos a market IOC.
- No hacer parecer que la limit order siempre es mejor. Tiene su propio riesgo.

### Salida
- "Market = ejecucion garantizada, precio incierto. Limit = precio garantizado, ejecucion incierta. IOC/FOK = control del residuo."

---

## Bloque 2: Simulador de matching (8 min)

### Objetivo
Que el alumno vea en tiempo real como las ordenes consumen el libro, como el spread cambia, y cual es la diferencia visual entre un market fill y una limit en cola.

### Accion en pantalla
1. Pulsa "Buy 0.5 BTC". Observa como el primer nivel del ask se consume parcialmente. Lee el fill log.
2. Pulsa "Buy 2.0 BTC". Observa como consume 2-3 niveles. Senala el slippage en el log.
3. Introduce un limit bid: precio = best bid - 5, tamano = 0.5. Pulsa el boton. Senala la barra cyan en el lado bid.
4. Pulsa "Sell 0.5 BTC". Observa el consumo del lado bid. Si tu limit order esta en el camino — fill.
5. Pulsa "IOC 1.5". Observa que ejecuta lo que puede y el residuo se cancela.
6. Pulsa "FOK 5.0". Con el libro parcialmente consumido, es probable que no haya liquidez suficiente — muestra el KILLED.
7. Pulsa "Reset" para restaurar el libro.

### Que decir
- "Fijate: cada vez que ejecutas una market buy, el ask side se encoge. El libro reacciona."
- "El flash blanco en un nivel indica que se ha consumido — total o parcialmente."
- "Las barras cyan son tus limit orders. Estan en el libro, esperando contrapartida."
- "IOC: ejecuto 0.8 de 1.5, el resto lo descarto. No queda rastro en el libro."
- "FOK con 5 BTC: necesito 5 BTC disponibles en el lado ask. Si no los hay, no ejecuto nada. Todo o nada."

### Riesgo
- No atascarse configurando limit orders perfectas. La demo debe fluir.
- No explicar FIFO en detalle aqui — lo vereis en el notebook.
- Dejar que el FOK falle naturalmente para mostrar el comportamiento "killed".

### Salida
- "El libro es dinamico. Cada orden lo cambia. Un market order agresivo puede mover el precio."

---

## Bloque 3: Coste y trade-off (5 min)

### Objetivo
Dar al alumno una intuicion cuantitativa del coste de la urgencia y del riesgo de la paciencia.

### Accion en pantalla
**Panel izquierdo — coste market:**
- Con 1 BTC: senala el spread ($11) + slippage (~$3). Total ~$14.
- Sube el slider a 5 BTC: senala como el slippage crece (no linealmente).
- Sube a 10 BTC: el coste total supera los $50.

**Panel derecho — probabilidad limit:**
- Con distancia $5 del mid: ~80% de probabilidad. "Cerca del mid, casi siempre ejecuta."
- Sube a $20: ~40%. "Te alejas del mid para conseguir un precio mejor — pero la mitad de las veces no ejecutas."
- Sube a $50: <15%. "Precio muy ventajoso, pero casi nunca ejecuta."

### Que decir
- "El spread no es un numero abstracto. Con 1 BTC a $100.000, pagas $11 solo por entrar y salir."
- "Y eso es el escenario ideal, sin slippage. Con una orden grande, ese coste crece."
- "La limit order ahorra ese coste — si ejecuta. Pero si el mercado no llega a tu nivel, tu posicion no se abre."
- "No hay una respuesta correcta. Depende de la urgencia, el tamano, y la volatilidad del momento."
- "Los algoritmos de ejecucion que vereis en L8-L9 tratan de resolver exactamente esto: ejecutar sin mover el precio en tu contra."

### Riesgo
- No entrar en modelos formales de market impact. La intuicion basta aqui.
- No hacer parecer que la limit siempre es mas barata — la opcion de no ejecutar tiene un coste implicito.

### Salida
- "El mercado no espera. Tu decides cuanto pagas por la urgencia."

---

## Cierre (1 min)

### Objetivo
Cerrar con la secuencia y preparar el notebook donde construiran el matching engine.

### Que decir
- "Hoy habeis visto los tres tipos fundamentales de ordenes y como interactuan con el LOB."
- "Market = taker, limit = maker, IOC/FOK = control del residuo."
- "En el notebook vais a construir un MatchingEngine en Python — el mismo mecanismo que acabais de ver en el simulador, pero en codigo."
- "Usareis los datos de L4: el mismo libro que analisteis la semana pasada, ahora con ordenes que lo transforman."
- "Siguiente clase: ya sabeis como se generan y ejecutan ordenes. En L6 construiremos un pipeline de ciencia de datos para modelizar variables del LOB — probabilidad de fill, imbalance futuro."

### Salida
- "El libro es la subasta. La orden es tu voz en ella. La eleccion importa."

---

## Checklist rapido

- [ ] He explicado la tension fundamental: market = ejecucion garantizada vs limit = precio garantizado.
- [ ] He mostrado las tres tarjetas: market, limit, IOC/FOK con sus garantias y riesgos.
- [ ] He usado el simulador para demostrar fills de market orders (consumo de niveles, slippage).
- [ ] He mostrado una limit order en cola (barra cyan en el libro).
- [ ] He demostrado IOC (residuo cancelado) y FOK (killed por liquidez insuficiente).
- [ ] He conectado con L4 (mismo LOB, ahora en movimiento).
- [ ] He plantado el bridge a L6 (modelizar el LOB con ciencia de datos).
- [ ] No he entrado en GTC, GTD, pro-rata, venue logic ni FIFO multi-queue.
