# Guión — Clase 6: LOB Data Science Pipeline

**Idea central:** El pipeline importa más que el modelo. Un modelo potente con un split o un target mal definido produce resultados inútiles — o peor, resultados que parecen buenos y en producción fallan.

**Tiempo total:** 20 min (presentación) + 15 min (notebook) + ejercicios

---

## Hero (2 min)

**Objetivo:** Abrir con la pregunta que la clase responde y establecer el tono.

**Acción en pantalla:**
- Señalar las tres preguntas del hero: "Sabes leer el libro. Sabes enviar órdenes. ¿Puedes predecir?"
- Señalar la flecha animada LOB → features → modelo → predicción (UP, p=0.61)
- Señalar el aviso: "El protagonista hoy no es el modelo. Es el pipeline."

**Qué decir:**
"En L4 aprendisteis a leer el libro. En L5, a enviar órdenes y observar fills. Hoy la pregunta cambia: ¿se puede predecir qué va a pasar? La respuesta es sí, con condiciones. Y las condiciones son el tema de hoy."

"Este output de aquí — UP con probabilidad 0.61 — es lo que vamos a construir. Pero el resultado no importa hasta que tengamos el pipeline bien hecho. Si el pipeline falla, el número miente aunque sea bonito."

**Riesgo:** No generar expectativas de que el modelo va a ser bueno. La clase es sobre construir el pipeline correctamente, no sobre 80% de accuracy.

**Salida:** "Cinco pasos. Vamos uno a uno."

---

## Bloque 1: El pipeline (6 min)

**Objetivo:** Que el alumno vea los cinco pasos del pipeline de una vez antes de entrar en detalles. Crear el mapa mental antes de los detalles.

**Acción en pantalla:**
1. Dejar que las partículas fluyan por el diagrama animado ~15 segundos. No decir nada. Que lo absorban.
2. Hacer clic en cada nodo en orden: LOB Snapshot → Feature Eng. → Target → Split Temporal → Baseline.
3. Para cada nodo, leer en voz alta el detalle que aparece en el panel lateral y añadir el comentario correspondiente.

**Qué decir por nodo:**

*LOB Snapshot:* "Los datos crudos: 500 snapshots de BTC. 40 columnas — precio y size de 10 niveles de bid y de ask. Son los mismos datos de L4. Ahora los vamos a convertir en señales."

*Feature Eng.:* "De 40 columnas crudas pasamos a 6 features con significado económico. El imbalance ya lo conocéis. El wmid es una versión ponderada del mid que pesa más a los niveles con más tamaño. El depth ratio compara toda la profundidad bid vs ask."

*Target:* "¿Qué queremos predecir? El precio exacto es muy difícil — demasiado ruido. Empezamos con dirección: sube o baja en el siguiente snapshot. 246 subidas, 253 bajadas — casi balanceado."

*Split Temporal:* "Aquí está la primera trampa clásica. Ahora la vemos."

*Baseline:* "Y aquí la segunda trampa: creer que un modelo complejo es mejor por defecto. El baseline es el suelo. Si no lo superas, vuelves al paso 2."

**Riesgo:** No pasar demasiado tiempo en la animación. Es introductoria. El detalle viene en el notebook.

**Salida:** "Cinco pasos. Dos de ellos tienen trampas clásicas que vamos a ver en detalle."

---

## Bloque 2: Split temporal y leakage (6 min)

**Objetivo:** Que el alumno entienda por qué el split temporal es obligatorio y qué es leakage con un ejemplo concreto de LOB.

**Acción en pantalla:**

*Parte A — Split (3 min):*
1. El modo temporal está activo por defecto — señalar que los puntos verdes están todos a la izquierda y los rojos a la derecha.
2. Hacer clic en "Split Aleatorio". Dejar que los alumnos vean los puntos rojos mezclados con los verdes.
3. Señalar el warning que aparece: "X test points en zona de entrenamiento".
4. Volver a "Split Temporal".

**Qué decir:**
"Cuando usáis `sklearn.train_test_split()` por defecto, el parámetro shuffle está activo. Mezcla el tiempo. Vuestro test set contiene snapshots del pasado y del futuro mezclados."

"¿Qué consecuencia tiene? El modelo puede ver durante el entrenamiento un snapshot del minuto 480. En el test set hay snapshots del minuto 5. El modelo aprende correlaciones entre momentos que no son causalmente relacionados."

"En evaluación parece funcionar. En producción, el tiempo fluye hacia adelante y el modelo falla. Regla: con series temporales, el test siempre está en el futuro del train."

*Parte B — Leakage (3 min):*
1. Señalar la fórmula: `realized_spread = ask_price_1[t+1] − bid_price_1[t]`
2. Hacer clic en "Revela el leak".
3. Señalar el `t+1` ahora en rojo y el aviso.
4. Señalar los dos acc pills: ~49% sin leakage, 88% con leakage.

**Qué decir:**
"El leakage es más sutil que el split. Mirad esta fórmula: realized_spread usa el ask price del snapshot siguiente. En el momento t, ese precio todavía no existe."

"Si añadimos este feature, ¿qué pasa con la accuracy? Del 49% al 88%. Un salto de 39 puntos porcentuales."

"Esa es la señal de alarma: si añadir un feature mejora la accuracy de forma inesperada y grande, pregunta: ¿este dato existía en el momento de la predicción? Si la respuesta es no, es leakage."

"La prueba concreta: el `.shift(-1)` en Python desplaza una columna hacia arriba — trae el futuro al presente. Cada vez que veáis `.shift(-N)` en un feature, preguntad por qué."

**Riesgo:** No entrar en técnicas avanzadas de detección (permutation importance, etc.). Solo intuición y ejemplo concreto.

**Salida:** "Si no puedes explicar por qué un feature existe en el momento t, no lo uses."

---

## Bloque 3: Baseline (5 min)

**Objetivo:** Que el alumno vea un modelo funcionando y entienda qué significa 54% de accuracy en términos de trading.

**Acción en pantalla:**
1. Señalar el scatter plot de imbalance vs cambio de precio. Mover el cursor sobre los puntos verdes (UP) y rojos (DOWN). Señalar que hay algo más de concentración de verde a la derecha (alto imbalance).
2. Mover el slider de umbral de imbalance de 0.30 a 0.70. Señalar cómo la barra del threshold cambia. Pararse en 0.60 donde da 54%.
3. Señalar las tres barras: "Siempre UP" ~50.7%, Threshold ~54%, LR ~49.3%.

**Qué decir:**

*Scatter:* "Este scatter tiene 150 puntos — el test set. Cada punto es un snapshot: eje X el imbalance, eje Y cuánto cambió el precio en el siguiente snapshot. Verde = subió, rojo = bajó. ¿Veis algún patrón? Hay algo — más verde a la derecha — pero hay mucho ruido."

*Slider:* "Si ponemos un umbral: si el imbalance supera X, predecimos UP; si no, DOWN. ¿Dónde funciona mejor? En 0.60 alcanzamos un 54%."

*Barras:* "Comparad los tres baselines. El modelo de regresión logística con los features que tenemos... queda en 49.3%. Por debajo de predecir siempre UP."

"Esto es perfectamente normal. Tenemos 349 ejemplos de entrenamiento, 2 features, y estamos en un mercado casi eficiente. La señal es débil."

"¿Por qué 54% puede tener valor si lo maximizamos? Porque si operas miles de veces con una ventaja estadística pequeña, esa ventaja se acumula. Pero solo si los costes de transacción son menores que esa ventaja. Con un spread de $11 en BTC, necesitarías una ventaja mucho mayor."

"En L7 vamos a intentar mejorar esto con más features y modelos más complejos."

**Riesgo:** No generar la expectativa de que el modelo va a ser útil. Mantener el framing honesto.

**Salida:** "54% es el punto de partida honesto. El pipeline está limpio. El modelo es simple. L7 mejora el modelo."

---

## Cierre (1 min)

**Acción en pantalla:** Los cinco takeaways aparecen uno a uno con el scroll.

**Qué decir:**
"Cinco ideas para hoy. El pipeline primero — antes que el modelo. Split respeta el tiempo. Baseline antes de complicar. Sospecha del salto de accuracy — es leakage. Y 54% es el punto de partida."

"En el notebook vais a construir todo esto desde cero: features, split, demo del leakage, y el primer clasificador corriendo. Después, los ejercicios."

---

## Checklist del instructor

- [ ] He explicado los cinco pasos del pipeline con el diagrama animado (clic en cada nodo)
- [ ] He mostrado la diferencia entre split temporal y split aleatorio con el visualizador
- [ ] He mostrado el ejemplo concreto de leakage con `realized_spread` y el salto de 49% → 88%
- [ ] He explicado los tres baselines y discutido qué significa 54% en términos de trading
- [ ] No he prometido que el modelo va a funcionar bien en producción
- [ ] No he entrado en modelos complejos, regularización, ni hyperparameter tuning
- [ ] He plantado el puente a L7: "el mismo pipeline, más features, más modelos"
