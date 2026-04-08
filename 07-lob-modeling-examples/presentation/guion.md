# Guion — L7: LOB Modeling Examples

**Duración total:** 20 min  
**Secuencia:** HTML → lesson.ipynb (15 min) → ejercicios

---

## Checklist pre-clase

- [ ] Abrir `lob-modeling-interactive.html` en pantalla grande
- [ ] Tener `lesson.ipynb` listo en Jupyter (sin ejecutar)
- [ ] Verificar que `data/lob_modeling_features.csv` existe (o que `06-lob-data-science-pipeline/data/lob_features.csv` está disponible)
- [ ] Pantalla dividida no es necesaria — la presentación va completa primero

---

## Hero (2 min)

**Objetivo:** Recordar dónde quedamos en L6 y revelar las 2 palancas de mejora.

**Acción en pantalla:** El "49.3%" entra con animación GSAP (escala + fade), luego aparecen las dos tarjetas "Memoria temporal" y "Probabilidad de fill".

**Qué decir:**
> "La semana pasada construimos el pipeline completo y terminamos con una regresión logística que acertaba el 49.3% de las veces — peor que una moneda. ¿Eso significa que el LOB no tiene información predecible? No. Significa que estábamos mirando solo una foto fija. Hoy añadimos dos cosas: memoria — el pasado reciente — y una pregunta mejor: no '¿sube o baja?' sino '¿se llena mi orden?'"

**Riesgo:** Alumnos que no hicieron L6. Decir: *"No importa, en dos minutos tenéis el contexto en pantalla."*

**Salida:** Click scroll → Block 1.

---

## Block 1: Memoria temporal (6 min)

**Objetivo:** Entender por qué las features estáticas ignoran el contexto dinámico del LOB y cómo el rolling window añade memoria.

**Acción en pantalla:**
1. Mostrar el gráfico Chart.js con N=1 (raw imbalance, línea muy ruidosa).
2. Mover el slider despacio hasta N=5 — la línea se suaviza visiblemente.
3. Mover hasta N=10 — demasiado suave, pierde reactividad.
4. Volver a N=5 — "el sweet spot pedagógico".
5. Scroll al panel de 3 features y al bar chart de mejora.

**Qué decir:**
> "Esto es imbalance snapshot a snapshot — puro ruido. Cada tick toma una foto, pero el mercado tiene memoria. Cuando muevo la ventana a 5, estoy preguntando: '¿el imbalance ha sido consistentemente positivo en los últimos 5 snapshots?' Eso es una señal mucho más robusta."

> "Las tres features nuevas son: media del imbalance (¿tendencia?), momentum del mid (¿velocidad de cambio?) y varianza del imbalance (¿cuánta incertidumbre hay?). Con estas tres, la regresión logística pasa de 49.3% a 55.5%. No es enorme, pero es real y significativa."

**Riesgo:** Alguien pregunta "¿por qué no usar una ventana de 50?"  
→ *"Buena pregunta — con 484 muestras, una ventana de 50 recorta demasiados datos de entrenamiento. El trade-off entre señal y datos de entrenamiento lo vemos mejor en el block siguiente."*

**Salida:** Scroll → Block 2.

---

## Block 2: Overfitting (6 min)

**Objetivo:** Ver el problema de overfitting en acción con datos reales y entender la curva de complejidad.

**Acción en pantalla:**
1. Mostrar el complexity curve con max_depth=None — barra roja de test a 47.3%, barra verde de train al 100%.
2. Mover el slider hacia depth=2 — el gap se cierra, test sube.
3. Detenerse en depth=5 o 6 — suele ser el máximo test.
4. Mostrar el árbol D3 (los nodos se iluminan, las ramas se dibujan).
5. Señalar el primer split: `wmid ≤ 100200.5`.

**Qué decir:**
> "Con profundidad ilimitada, el árbol memoriza los 338 ejemplos de entrenamiento. Train accuracy: 100%. Test accuracy: 47.3%. Peor que tirar una moneda. El modelo ha aprendido el ruido, no la señal."

> "A medida que limitamos la profundidad, el árbol solo puede hacer pocos cortes y tiene que generalizar. El test sube. Esto es el trade-off bias-varianza: a la izquierda tienes un modelo demasiado simple que no aprende nada (high bias), a la derecha uno que memoriza todo (high variance)."

> "El árbol visualizado tiene 3 niveles. El primer split usa wmid — el precio ponderado. El segundo nivel ya usa imbalance_mean_5 — la feature temporal que acabamos de añadir. El modelo ha 'descubierto' que la memoria importa."

**Riesgo:** El slider del árbol es confuso para alumnos de fila de atrás.  
→ Hacer zoom en el árbol D3 antes de mostrar.

**Riesgo:** Alguien confunde "depth" con "número de árboles".  
→ *"Profundidad es cuántas preguntas hace el árbol en secuencia. Número de árboles es otra dimensión que vemos en el Random Forest."*

**Salida:** Scroll → Block 3.

---

## Block 3: Fill probability (5 min)

**Objetivo:** Reformular la predicción como "¿se llena mi orden límite?" y ver cómo el imbalance predice fills.

**Acción en pantalla:**
1. Mostrar la tabla LOB animada — pulsar "Simular fill" una o dos veces.
2. Señalar la columna bid: "tu orden está aquí esperando".
3. Mostrar las barras de buckets empíricos (aparecen en scroll).
4. Mover el slider de imbalance — el donut cambia, la recomendación cambia.
5. Mostrar recomendación LIMIT cuando imbalance > 0.3, MARKET cuando < -0.3.

**Qué decir:**
> "Hasta ahora preguntábamos '¿sube o baja el mid?' Pero como trader lo que me importa es: '¿se ejecuta mi orden en los próximos 3 snapshots?' Si el imbalance es muy positivo — hay mucho más compra que venta — la probabilidad de que alguien cruce el spread y llene mi bid es baja. Eso significa que esperar con una orden límite tiene sentido."

> "Si el imbalance es muy negativo — hay mucho más venta — el precio baja, mi bid no se llena, y me conviene ir al mercado. El modelo no predice precios; predice comportamiento de ejecución."

> "El Random Forest sobre fill_in_3 llega al 54.8% — 2.7 puntos sobre baseline. No es mucho, pero combinado con las features de dirección puede orientar la decisión de tipo de orden."

**Riesgo:** Alumnos preguntan "¿pero 54.8% es útil?"  
→ *"En trading algorítmico, un 2-3% de edge sobre baseline bien calibrado es explotable si tienes volumen. Lo importante es que el modelo está aprendiendo algo real, no ruido."*

**Salida:** Scroll → Cierre.

---

## Cierre (1 min)

**Qué decir:**
> "Tres ideas clave de hoy: uno, añadir memoria temporal mejora la predicción. Dos, más complejidad no siempre es mejor — el árbol sin límite es peor que una moneda. Tres, podemos usar el LOB para predecir ejecución, no solo precio. En la siguiente clase vemos VWAP: cómo fragmentar órdenes grandes para minimizar el impacto en el mercado."

---

## Tiempos de emergencia

| Situación | Acción |
|-----------|--------|
| Block 1 lleva más de 8 min | Saltar la parte de mejora %, ir directo a Block 2 |
| Block 2 demasiado largo | Mostrar solo la curva estática sin mover el slider |
| Sin tiempo para Block 3 | Decir: "Fill probability lo veis en el notebook y ejercicios" |
| Jupyter no carga | Abrir `lob_modeling_features.csv` en el explorador de archivos para mostrar las features |
