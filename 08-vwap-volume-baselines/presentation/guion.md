# Guion — L8: VWAP Volume Baselines

**Duración total:** 20 min  
**Secuencia:** HTML → lesson.ipynb (15 min) → ejercicios

---

## Checklist pre-clase

- [ ] Abrir `vwap-volume-baselines-interactive.html` en pantalla grande
- [ ] Verificar que Chart.js y D3 cargan (requiere red para CDN)
- [ ] Abrir `lesson.ipynb` en Jupyter con kernel listo (sin ejecutar)
- [ ] Comprobar que `data/btc_volume_intraday.csv` existe (6048 filas)
- [ ] Número memorizado: comprar 10 BTC de golpe cuesta $41.80/BTC más = $368 extra

---

## Bloque previo al HTML (1 min)

**Qué decir:**
> "La semana pasada predecíamos dirección del precio con un 55.5% de accuracy — señal micro, snapshots del LOB. Hoy cambiamos completamente de escala. Pregunta de hoy: tienes un millón de dólares en BTC que comprar. ¿Cómo lo haces sin mover el mercado?"

---

## Hero (2 min)

**Objetivo:** El alumno siente el problema antes de recibir la respuesta.

**Acción en pantalla:** Mostrar el hero con la pregunta central. Hacer clic en "Compra todo ahora" delante de la clase.

**Qué decir:**
> "10 BTC. 4 horas. Un millón de dólares. Si lo compras todo ahora mismo, ¿qué pasa?"

[clic en "Compra todo ahora"] — dejar que la animación corra

> "El libro se vacía nivel a nivel. El primer nivel es a 100.000. El segundo a 100.010. El décimo a 100.090. Cuando has comprado los 10 BTC has pagado un promedio de 100.041,80 — es decir, $41,80 más por BTC. En 10 BTC, son $368 tirados a la basura solo por la forma en que enviaste la orden."

> "VWAP es la respuesta: fragmentar la ejecución para seguir el ritmo del mercado. Y para fragmentar bien, necesitas predecir cuándo hay liquidez."

**Riesgo:** La animación D3 puede tardar 2-3 segundos en completarse. Dejar el silencio — es dramático.

**Salida:** "Primero entendamos por qué el tamaño de cada slice importa."

---

## Bloque 1: Market Impact (6 min)

**Objetivo:** Hacer visceral la diferencia entre ejecutar de golpe y fragmentar.

**Acción en pantalla:** Mover el slider de "Tamaño de la orden" de 1 a 10 BTC lentamente. La clase ve el slippage crecer en tiempo real.

**Qué decir con 1 BTC:**
> "Con 1 BTC solo consumo el primer nivel del libro — el más barato. Slippage: 5 dólares. Casi nada."

**Qué decir moviendo a 10 BTC:**
> "Con 10 BTC consumo 6 niveles. El libro tiene 10 niveles pero los primeros 6 ya tienen 10 BTC sumados. Cada nivel siguiente es más caro. Precio promedio: $100.041,80. Slippage: $41,80 por BTC."

**El número para anclar:**
> "Si eres un fondo comprando 1.000 BTC — normal en institutional — eso son 42.000 dólares de slippage en una sola ejecución. Por eso los algoritmos de ejecución son un negocio de cientos de millones de dólares."

**Qué NO decir:** No entrar en market impact permanente vs temporal, no mencionar modelos de Almgren-Chriss. Solo la intuición.

**Salida:** "Para fragmentar bien necesitas saber cuándo hay liquidez. Y el volumen tiene una forma clara..."

---

## Bloque 2: Perfil Intradiario (6 min)

**Objetivo:** El alumno ve la forma U, entiende que no es ruido, y nota el efecto lunes.

**Acción en pantalla — parte A (3 min):**
1. La curva U media se anima al entrar en la sección.
2. Señalar los picos: "Este es el open (00:00 UTC), este es el close (23:55 UTC)."
3. Señalar el valle: "Esto es mediodía UTC — Europa ha comido, América no ha abierto."

**Qué decir:**
> "Esta es la forma U. El open de BTC es 2.28 veces más activo que el mediodía. Siempre. No es ruido — es comportamiento de mercado. Asia ejecuta a las 00:00 UTC, Wall Street cierra a las 20:00-24:00 UTC. El valle es el hueco entre los dos."

**Acción en pantalla — parte B (3 min):**
1. Clic en "Lun" para activar el perfil del lunes (rojo).
2. Clic en "Vie" para añadir el viernes (verde).
3. Señalar la diferencia visual: el pico del lunes es claramente más bajo.

**Qué decir:**
> "Ahora miren la diferencia. El lunes en rojo — el viernes en verde. El lunes tiene 21.000 BTC de volumen medio. El viernes tiene 28.000. Un 33% más. Si ignoro esto y uso la media global para un lunes, mi schedule va a sobreestimar cuánto ejecutar al open."

**Interacción para la clase:** Preguntar: "¿Por qué creéis que el lunes tiene menos volumen?" (respuesta: los traders institucionales llegan el lunes a recoger posiciones, publican órdenes más tarde del día)

**Salida:** "Con esto en mano, ya podemos construir el schedule."

---

## Bloque 3: VWAP Schedule (6 min)

**Objetivo:** Ver que la función es sorprendentemente simple y que el RMSE del lunes favorece mean_monday.

**Acción en pantalla — parte A (2 min):** Las 3 líneas de código aparecen con GSAP stagger.

**Qué decir:**
> "Esto es todo lo que hace VWAP básico. Tres líneas. Normaliza el perfil — divide por su suma para que sume 1. Multiplica por la cantidad total. Fin. Si en el intervalo 0 el mercado históricamente concentra el 0.48% del volumen diario, tú envías el 0.48% de tu orden en ese intervalo."

> "La dificultad no está en la función. Está en predecir bien el perfil."

**Acción en pantalla — parte B (2 min):** Cambiar entre los 4 radios de baseline.

**Qué decir al cambiar a "Media lunes":**
> "Fíjense: el bar del open es más bajo en mean_monday. El lunes históricamente arranca más despacio. Si ejecuto un lunes usando el perfil global, estoy enviando demasiado al open."

**Acción en pantalla — parte C (2 min):** Clic en "Revelar resultados".

**Qué decir:**
> "Revelemos los números. ¿Qué baseline predice mejor el perfil real? [clic] El ganador global es mean_all — la media de todos los días. Pero para los lunes, mean_monday es un 19% mejor en RMSE. Eso es el valor del contexto: si sabes que es lunes, usa el perfil del lunes."

**Riesgo:** Alguien pregunta qué es RMSE.
→ *"RMSE es la distancia promedio entre el perfil que predecimos y el perfil real. Más bajo es mejor."*

**Salida:** "En el notebook vamos a construir esto paso a paso."

---

## Cierre (1 min)

**Acción en pantalla:** Scroll al cierre. Takeaways aparecen con stagger.

**Qué decir:**
> "Tres ideas. Uno: el market impact es real — $368 en una ejecución de 10 BTC. Dos: el volumen tiene forma — U-shape más efecto día de la semana, señales macro estables. Tres: el contexto mejora el baseline — la media del lunes bate a la media global en un 19% de RMSE para los lunes."

**Bridge a L9:**
> "Hoy el schedule es estático — lo fijamos antes de empezar. La semana que viene añadiremos una capa dinámica: los últimos 5 minutos de volumen real como corrección en tiempo real. El schedule ya no será fijo."

---

## Tiempos de emergencia

| Situación | Acción |
|-----------|--------|
| B1 lleva más de 8 min | Saltar el slider, mostrar solo las stat cards |
| B2 sin tiempo para DOW | Mostrar solo la curva U media, sin activar días |
| B3 sin tiempo para RMSE | Mostrar solo el schedule de mean_all |
| CDN falla (sin internet) | Abrir `lesson.ipynb` directamente y ejecutar las celdas de visualización |
