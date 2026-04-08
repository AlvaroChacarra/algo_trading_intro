# Guión — L9: VWAP Dinámico + Cierre de Ciclo

**Presentación:** `vwap-dynamic-interactive.html`  
**Duración total:** 20 min  
**Tema visual:** Mission Control / terminal oscuro

---

## Checklist pre-clase

- [ ] Abrir `vwap-dynamic-interactive.html` en Chrome/Edge (fullscreen)
- [ ] Verificar que el botón "▶ Iniciar día" funciona (Hero)
- [ ] Tener `lesson.ipynb` abierto en Jupyter como segunda pestaña
- [ ] Recordar a los alumnos que L8 produjo `data/mean_profile.csv` que L9 carga

---

## Hero — Mission Control (2 min)

**Objetivo:** crear la sensación de que hoy ejecutamos en tiempo real, no en postproceso.

**Qué ves en pantalla:**
- Terminal tipo trading: "EXECUTING 10 BTC ACROSS THE DAY"
- Ring de progreso con 6 campos: executed, pending, interval, CF, decision, tracking
- Botón "▶ Iniciar día"

**Qué decir:**
> "En L8 construimos un schedule. Un plan. Pero los planes no sobreviven al contacto con el mercado."
>
> "Hoy ejecutamos en tiempo real. Vamos a ver qué pasa cuando el volumen real  
> no sigue exactamente el perfil histórico."
>
> [pulsa "▶ Iniciar día"]
>
> "Observad el campo CF — correction factor. Cada 25 minutos recalculamos.  
> Verde: el mercado es más activo de lo previsto. Rojo: más tranquilo."

**Riesgo:** Los alumnos pueden querer entender cada campo desde el principio.  
**Respuesta:** "Todo esto lo construimos en el notebook. Ahora solo observad el patrón."

**Salida:** "Pero antes de ver la animación completa, entendamos qué es el CF."

---

## Bloque 1 — Correction Factor (6 min)

**Objetivo:** el alumno entiende la fórmula `CF = realizado / predicho` y sus implicaciones.

**Qué ves en pantalla:**
- Slider: ratio 0.3× a 3.0×
- Badge CF que cambia de color (verde > 1, cyan = 1, rojo < 1)
- Carta con Schedule actual vs Schedule ajustado
- Veredicto: "Mercado activo → acelera / Mercado tranquilo → frena"

**Qué decir:**
> "La fórmula es simple: CF = lo que ejecutó el mercado / lo que predicíamos."
>
> [mover slider a 1.8×]
>
> "CF = 1.8 significa que el mercado fue 80% más activo que el histórico.  
> Si el perfil decía '0.048 BTC en este intervalo' y el mercado hizo 0.086 BTC —  
> multiplicamos el schedule restante por 1.8."
>
> [mover slider a 0.4×]
>
> "CF = 0.4: mercado muy tranquilo. Reducimos el ritmo.  
> No nos apresuramos a cruzar el spread cuando no hay liquidez."

**Pregunta al aula:**
> "¿Qué pasa si aplicamos siempre el CF del último bloque sin filtrar ruido?"

Esperar 30 segundos. Respuesta esperada: amplificamos el ruido.

> "Exacto. Por eso usamos ventanas de 25 min — no cada snapshot.  
> Es un filtro natural contra el ruido de microsegundos."

**Riesgo:** Alumnos preguntan por la fórmula exacta de ajuste.  
**Respuesta:** "Exactamente — `schedule[j+window:] *= cf`. Lo vemos en el notebook."

**Salida:** "Ahora que tenemos el CF, veamos si mejora el tracking en los 16 días."

---

## Bloque 2 — Backtest Race (5 min)

**Objetivo:** evidencia empírica de que el CF reduce el tracking deviation en la mayoría de días.

**Qué ves en pantalla:**
- Tabla de 16 días con dos barras (rojo = estático, verde = dinámico)
- Las barras crecen día a día con animación
- Badge "DINÁMICO GANA" / "ESTÁTICO GANA" por día
- Resumen final: ratio de victorias y mejora media

**Qué decir:**
> "16 días de evaluación. Walk-forward: para cada día, solo usamos los anteriores."
>
> [pulsar Play, observar la carrera]
>
> "El dinámico no gana siempre. Pero gana en la mayoría de días —  
> especialmente cuando el día es atípico respecto al histórico."

**Pregunta al aula:**
> "¿Por qué creen que hay días donde el estático gana?"

Respuesta esperada: cuando el día es muy cercano al histórico, el CF introduce ruido.

> "Correcto. El CF ayuda más cuando hay divergencia real entre el día y el histórico.  
> Si el día es perfectamente 'normal', el CF puede sobre-corregir."

**Timing ajustado (si vais cortos):**
- Pasar directamente al resumen numérico sin ver la animación completa.

**Salida:** "Estamos adaptando el ritmo. Pero ¿qué tipo de orden enviamos?"

---

## Bloque 3 — El Cuadro de Mando (6 min)

**Objetivo:** conectar L6/L7/L8/L9 en una sola decisión ejecutable.

**Qué ves en pantalla:**
- Tres gauges interactivos: imbalance (L6/L7), fill_prob (L7), volume_ratio (L8/L9)
- Tres sliders independientes para mover cada señal
- Panel semáforo grande: LIMIT / MARKET / WAIT con color y GSAP animation

**Qué decir:**
> "En los últimos 4 clases construimos 3 señales. Hoy las unimos."
>
> [mover imbalance a 0.7, fill_prob a 0.65]
>
> "imbalance > 0.55 y fill_prob > 0.50 — LOB alcista, alta probabilidad de que nuestra  
> limit order se ejecute. Decisión: LIMIT. Ponemos la orden pasiva y esperamos el fill."
>
> [mover imbalance a 0.3, fill_prob a 0.3, volume_ratio a 1.5]
>
> "LOB bajista, fill improbable, pero el mercado está muy activo.  
> No hay tiempo para esperar un fill — ejecutamos MARKET ahora."
>
> [mover todo a zona neutral]
>
> "Zona gris: nada claro. WAIT. Conservamos munición para el siguiente bloque."

**Punto pedagógico clave:**
> "Fijaos que cada gauge viene de una clase distinta.  
> En L2 construimos la clase Order con un método `decide()`.  
> Hoy tenemos `ExecutionDecision` — la misma idea, con señales reales."

**Riesgo:** Alumnos quieren más umbrales o lógica más sofisticada.  
**Respuesta:** "Esta es la heurística. En producción se calibra con datos reales.  
La estructura es lo que importa, no los thresholds exactos."

**Salida:** "Antes de pasar al notebook, veamos el cierre de ciclo."

---

## Cierre — L4 → L9 (1 min)

**Qué ves en pantalla:**
- Timeline L4→L9 con GSAP stagger: 6 cards aparecen una a una
- Cada card: clase, pregunta central, artefacto de código
- Bridge card: "L10 — Exam-Quiz I"

**Qué decir:**
> "En 6 clases pasamos de entender el libro de órdenes a construir un sistema  
> que decide qué orden mandar, de qué tipo, y cuánta cantidad."
>
> "L10 es el Exam-Quiz I. Cubre todo esto — L4 a L9.  
> Los ejercicios de hoy son la mejor preparación."

---

## Timing de emergencia (si hay retraso)

| Si te retrasas en... | Recorta aquí |
|----------------------|-------------|
| Hero (>3 min) | Limita la animación a 30 seg |
| B1 (>7 min) | Salta la pregunta al aula |
| B2 (>12 min) | Muestra solo el resumen final, no la animación completa |
| B3 (>17 min) | Muestra un solo escenario (LIMIT), menciona los otros |
| Cierre | Lee solo los artefactos de código, salta las preguntas centrales |
