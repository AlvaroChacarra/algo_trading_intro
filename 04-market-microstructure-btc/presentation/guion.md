# Guion — Clase 4: Microestructura de Mercado (BTC)

La presentacion tiene 3 bloques + hero + cierre. Duracion total: 20 minutos.

## Idea central

**El precio que ves no es un hecho — es el resultado de una subasta continua. El LOB es esa subasta.**

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
Abrir con el contraste: el precio de BTC no es un numero estatico — es el resultado de miles de ordenes compitiendo en tiempo real.

### Accion en pantalla
- Senala el LOB animado del hero: bids en verde a la izquierda, asks en rojo a la derecha.
- Senala las tres metricas en vivo: best bid, spread, best ask.
- Senala el mid price debajo.
- Senala los 3 iconos: LOB, Profundidad, Imbalance.

### Que decir
- "En las clases anteriores habeis trabajado con precios como datos fijos: `price = 100000`."
- "Hoy vamos a ver de donde sale ese numero. Spoiler: no es un hecho — es el resultado de una subasta."
- "La clase tiene tres partes: que es un LOB, como leerlo, y que nos dice el imbalance sobre presion de mercado."

### Riesgo
- No presentar esto como teoria de finanzas abstracta. Mantenlo visual y concreto.
- No asumir que los alumnos han visto un order book antes.

### Salida
- "El precio de BTC no existe hasta que un comprador y un vendedor se ponen de acuerdo."

---

## Bloque 1: Que es un LOB (6 min)

### Objetivo
Que el alumno entienda la estructura basica: bids a la izquierda, asks a la derecha, best bid/ask, spread y mid price.

### Accion en pantalla
- Senala el LOB interactivo con 10 niveles por lado.
- Observa como las ordenes aparecen y desaparecen (animacion continua).
- Senala las metricas en vivo: best bid, best ask, spread, mid price.
- Senala como el spread cambia cuando se mueven las ordenes.

### Que decir
- "Un LOB es una lista de ordenes limitadas. Los compradores ponen bids — el maximo que estan dispuestos a pagar. Los vendedores ponen asks — el minimo que aceptan."
- "El best bid es el precio mas alto que alguien ofrece comprar. El best ask es el precio mas bajo que alguien ofrece vender."
- "El spread es la diferencia: ask menos bid. Es el coste implicito de operar. Si compras y vendes inmediatamente, pierdes el spread."
- "El mid price es el punto medio: bid mas ask dividido entre dos. Es la referencia mas neutral de donde esta el mercado."
- "En BTC, el spread suele ser unos pocos dolares sobre 100.000. En acciones poco liquidas puede ser el 1% del precio."

### Riesgo
- No entrar en tipos de ordenes (market, limit, stop). Eso es Lesson 5.
- No explicar el matching engine. Solo la estructura del libro.
- No usar jerga sin definirla primero (bid, ask, spread — definir cada una).

### Salida
- "Bid y ask son intencion. El spread es el coste de la inmediatez."

---

## Bloque 2: Leer el libro — Profundidad y market orders (7 min)

### Objetivo
Mostrar que el LOB tiene profundidad (multiples niveles) y que una market order consume niveles.

### Accion en pantalla
- Senala la depth chart: volumen acumulado por lado.
- Usa el slider de niveles para mostrar como cambia la profundidad al incluir mas niveles.
- Pulsa "Market Buy 0.5 BTC". Senala como se consumen niveles del ask.
- Observa el slippage: el precio efectivo es peor que el best ask.
- Pulsa "Market Buy 2.0 BTC" para ver mayor impacto.
- Senala los detalles del fill: niveles consumidos, precio promedio, slippage.

### Que decir
- "El best ask te dice el precio del primer nivel. Pero si quieres comprar mas de lo que hay en ese nivel, empiezas a comer el siguiente."
- "Eso es profundidad: cuanto volumen hay detras del mejor precio."
- "Una market order dice: quiero comprar ahora, al precio que sea. El LOB te va rellenando nivel a nivel."
- "El slippage es la diferencia entre el precio que esperabas y el que realmente pagaste. A mas volumen, mas slippage."
- "Por eso un fondo grande no puede comprar todo de golpe — moveria el precio en su contra."

### Riesgo
- No entrar en la mecanica del matching engine (FIFO, pro-rata). Eso es L5.
- No complicar con ordenes parciales o cancellations.
- No perder mas de 2 minutos con el slider — es una demo, no un juguete.

### Salida
- "La profundidad te dice cuanto puedes operar antes de mover el precio."

---

## Bloque 3: Que nos dice el imbalance (5 min)

### Objetivo
Introducir el imbalance como metrica de presion compradora vs vendedora, y su valor predictivo limitado.

### Accion en pantalla
- Senala la formula del imbalance: `bid_vol / (bid_vol + ask_vol)`.
- Senala el gauge: > 0.5 = presion compradora, < 0.5 = presion vendedora.
- Observa el historico: imbalance vs movimiento de precio en las siguientes snapshots.
- Senala la correlacion: cuando el imbalance sube, el precio tiende a subir (pero no siempre).
- Destaca el scatter plot y la linea de tendencia.

### Que decir
- "El imbalance mide quien tiene mas peso en el libro: compradores o vendedores."
- "Si hay mucho volumen en bids y poco en asks, hay presion compradora. El imbalance esta por encima de 0.5."
- "Esto no predice el futuro con certeza. Pero es una senal: si los compradores estan empujando, el precio tiene mas probabilidad de subir."
- "En la practica, el imbalance se usa como feature en modelos de prediccion, no como senal unica."
- "En el notebook vais a calcular esto con los 500 snapshots y ver la correlacion vosotros mismos."

### Riesgo
- No vender el imbalance como indicador infalible. Es una senal debil pero real.
- No entrar en modelos predictivos o machine learning. Solo la intuicion.
- No dedicar demasiado tiempo a la formula — es una division simple.

### Salida
- "El imbalance no predice — informa. Te dice donde esta la presion ahora."

---

## Cierre (1 min)

### Objetivo
Cerrar con la secuencia memorable y preparar el notebook.

### Que decir
- "Hoy habeis entendido de donde sale el precio: de una subasta continua con bids y asks."
- "LOB -> spread -> profundidad -> imbalance. Esa es la secuencia."
- "En el notebook vais a cargar 500 snapshots reales de BTCUSDT y calcular todas estas metricas con pandas."
- "Siguiente clase: ya entendeis la estructura del LOB. En Lesson 5 veremos que pasa cuando envias una orden — tipos de ordenes y como el matching engine las procesa."

### Salida
- "El precio es consenso. El LOB es la negociacion."

---

## Checklist rapido

- [ ] He explicado bid, ask, spread y mid price con el LOB interactivo.
- [ ] He mostrado la profundidad y el efecto de una market order (slippage).
- [ ] He introducido el imbalance como metrica de presion con correlacion visual.
- [ ] He conectado con L1-L3 (precios como datos fijos → ahora su origen).
- [ ] He plantado el bridge a L5 (tipos de ordenes y matching).
- [ ] No he entrado en tipos de ordenes, matching engine ni modelos predictivos.
