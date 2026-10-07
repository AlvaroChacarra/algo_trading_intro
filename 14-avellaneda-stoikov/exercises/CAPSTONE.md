# Capstone · diseña y contrasta tu market maker

**REQUIRED · 90 minutos.** Abre `capstone.py`, guarda una copia personal de la carpeta y empieza por **1A**, en los comentarios de `main`. Base y simulador incluidos. Edita únicamente `MiEstrategia.quotes` y tus anotaciones; conserva `BaselineMaker` intacto.

La plantilla funciona, pero sus quotes aún son idénticas al control. Avanza con `python capstone.py --through 2A`, después 3A y 4A. **Congela la regla antes de ejecutar 5A.** El comando sin `--through` ejecuta todo, incluido el contraste: úsalo tras cerrar el desarrollo. Consulta [el ejemplo completo](solutions/capstone.md) después de intentar tu hipótesis. La numeración 1A–6A de este proyecto es independiente del principal.

| Hito / apartado | Minutos | Evidencia para continuar |
| --- | ---: | --- |
| 1A · Hipótesis | 10 | Cambio, efecto esperado y caso de fallo. |
| 2A · Control | 15 | Centro/ancho en tres estados y referencia seed=2026. |
| 3A · Regla propia | 20 | Una modificación activada y explicada. |
| 4A · Desarrollo | 20 | Todas las filas de 2026, 7 y 314; parámetros finales. |
| 5A · Contraste congelado | 15 | 2718, 1618 y 5772 sin reajustar. |
| 6A · Explicación | 10 | Causalidad, dispersión, límites y reproducción. |

Los 90 minutos incluyen instrucciones y ayudas. Aplica clases, llamadas y tablas con menos guía; la decisión de cotización es tuya.

## Ejercicio 1 · Antes del código

### 1A · Formula una hipótesis

En los comentarios **1A** de `capstone.py:main`, escribe una decisión de centro, ancho o tamaño, el estado que la activa, su efecto esperado en fills/exposición/PnL y un caso que podría refutarla. No basta «mejorar el beneficio».

**Comprueba:** `python capstone.py --through 1A` termina sin simular. La evidencia es tu predicción escrita antes del resultado.

## Ejercicio 2 · Conserva un control

### 2A · Reproduce la referencia

Ejecuta `python capstone.py --through 2A`. El bloque proporcionado consulta BaselineMaker a q=0, +0.3 y -0.3 y lo simula con seed=2026. Anota centro/ancho sin modificar la clase.

**Comprueba:** mid=100; centros 100, 99.4, 100.6 y ancho 1.2. PnL 2.2878 y máximo |q| .400. Cambiar la base impediría atribuir el resultado a tu regla.

## Ejercicio 3 · Una decisión propia

### 3A · Implementa y prueba la activación

En `MiEstrategia.quotes`, implementa una única modificación de quotes después de escribir tu hipótesis; conserva bid <= ask y comprueba su activación con estados fijados. Puedes transformar la salida de `super().quotes(mid,tau)`. No modifiques el motor.

**Comprueba:** `python capstone.py --through 3A` crea una instancia nueva y muestra centro/ancho a q=0, +0.3 y -0.3. Elige además un estado donde actúe y otro donde no. Si cambias tamaño, declara esa decisión y su efecto en exposición/comparación.

**Transferencia antes de consultar:** si usas un umbral, predice y prueba el borde exacto y un valor por encima: por ejemplo, q=.2 y .2001 para un umbral .2. Esto comprueba el mecanismo, no rentabilidad.

<details><summary>Ayuda · Una decisión y su coste</summary>Elige centro, ancho o tamaño y un estado que active el cambio. Predice también un coste: alejar una quote puede reducir actividad y retrasar la salida de una posición. No necesitas imitar el ejemplo.</details>

## Ejercicio 4 · Desarrolla con todas las filas

### 4A · Compara y fija parámetros

Ejecuta `python capstone.py --through 4A`. compare crea control y regla propia por semilla, con sigma=.5, intensidad=50, kappa=1.5, 500 pasos y tamaño .1 salvo cambio declarado. Anota los parámetros finales junto al comentario **4A**.

**Comprueba:** seis filas para 2026, 7 y 314; PnL final y máximo |q| por regla. Promedio/rango acompañan las filas, no las sustituyen. No selecciones solo la semilla favorable.

## Ejercicio 5 · Congela antes de mirar

### 5A · Ejecuta el contraste

Con regla y parámetros anotados, ejecuta `python capstone.py --through 5A`. Conserva las filas de 2718, 1618 y 5772 y explica si apoyan tu predicción. No reajustes con ellas.

**Comprueba:** otras seis filas con código y condiciones congelados. Son semillas públicas de práctica; no equivalen a datos reales fuera de muestra ni a una evaluación secreta.

<details><summary>Ayuda · Si tu idea falla</summary>Confirma activación y control intacto. Conserva el resultado desfavorable; describe qué predicción falló y qué nuevo experimento estudiarías. No entrenes otra vez sobre el contraste.</details>

## Ejercicio 6 · Explica y reproduce

### 6A · Defiende la conclusión

En los comentarios **6A** de main, explica quotes → probabilidad de fills → exposición y PnL. Incluye todas las semillas, dispersión y un caso de fallo. Indica qué cambiaría con costes por fill, cola, latencia o selección adversa y qué evidencia necesitarías para un mercado real. Ejecuta `python capstone.py` para reproducir la regla congelada; importar el archivo no inicia simulaciones.

Entrega copia personal ejecutable y explicación en comentarios o texto adjunto. Una hipótesis bien contrastada puede dar resultados peores que el control. La referencia Markdown responde 1A–6A dentro del mismo programa completo y explica cada apartado.

**Modelo:** research_support.py proporciona el entorno pasivo L13–L14, horizonte 1, sigma por horizonte, shocks/llegadas independientes, hasta un fill por lado/paso. No es replay. Máximo inventario después de cada fill; PnL marcado al último precio, incluida posición abierta. Sin costes, cola, latencia, impacto o flujo informado; no acredita rentabilidad futura.

Feedback: código correcto, explicación causal, comparación justa y límites, por igual; sin nota automática por PnL. Pesos oficiales conservados: asistencia 10%, participación 20%, continuos 40%, final 30%. No crea otro peso ni reemplaza el final.
