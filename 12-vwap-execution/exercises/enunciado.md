# L12 · Programa el encargo. Cuenta los fills.

Construye una estrategia que reparte una cantidad por un calendario conocido antes de operar. El calendario acumula el objetivo; solo los fills aumentan lo ejecutado. Al final informa lo que falta.

Guarda una copia de **esta carpeta completa** para tu trabajo. Todo lo necesario está incluido: no traslades clases de otras lessons. Edita `profiles.py`, `execution.py`, `main.py`; `opcionales.py` es independiente de la ruta requerida. El constructor, los datos y las llamadas de observación están proporcionados.

**Ruta:** 1A–3B LIVE (20 min); 4A–5A REQUIRED (34 min); 6A–6H OPTIONAL (43 min). Usa `python main.py --through 1A` para ver solo el apartado actual; sin argumentos ejecuta todo el principal. Los huecos posteriores no impiden esa comprobación. Los imports no ejecutan experimentos.

**Bases incluidas:** libro/adaptación, matching, ReplayMarket, cartera, Strategy/NewOrder/Order, ResearchBacktest y métricas. `exchange/` conserva los contratos SDK y datos de referencia; la clase que construyes y ejecutas aquí es **StudentVWAPStrategy**, no la VWAPStrategy del SDK.

**Datos y unidades:** `scenarios.py` aporta perfiles y snapshots sintéticos. `raw` representa volumen esperado relativo fijado antes de operar; intervalos de igual duración, un callback por foto hasta agotar el perfil. Pesos sin unidades; tamaños/target/executed en BTC; precios y arrival en USDT/BTC; fees en USDT; coste en bps. La profundidad anunciada limita fills, pero no es volumen negociado. Cada foto reemplaza el libro, sin impacto persistente, restricciones de financiación ni modelo de llegadas.

Primero repartes **5 BTC en cinco intervalos**. Para estudiar un fill parcial cambiamos explícitamente a **compra 1 BTC en dos intervalos**, sobre tres fotos. La tercera no amplía el calendario. El principal acaba con un caso incompleto. La serie precios/volumenes de 4F es otra población de sesión, observada después y nunca utilizada para decidir. Sin fills, las métricas incluidas devuelven `None`.

## Ejercicio 1 · Perfiles y cantidades · LIVE

### 1A · Normaliza el perfil

**Archivo:** `profiles.py`. **Encargo:** completa normalize_profile(raw): valida una lista no vacía de valores finitos no negativos y suma positiva; devuelve cada valor dividido por la suma.

**Comprobación:** `python main.py --through 1A`. **Resultado para contrastar:** Pesos [0.2]*5, suma 1. También [0,1,3] produce [0,0.25,0.75].

### 1B · Del peso al tamaño

**Archivo:** `profiles.py`. **Encargo:** completa slice_sizes(weights, total_size): devuelve cada peso multiplicado por total_size, sin modificar weights.

**Comprobación:** `python main.py --through 1B`. **Resultado para contrastar:** Cinco tamaños de 1 BTC, total 5. Todavía no son fills.

## Ejercicio 2 · Una Strategy con estado · LIVE

### 2A · Reinicia el estado

**Archivo:** `execution.py`. **Encargo:** completa on_start(ctx): reinicia step a 0, target y executed a 0.0; conserva el constructor proporcionado.

El constructor ya valida lado/tamaño, guarda los pesos y tamaños y llama on_start(None). No reescribas esa base. Cada prueba inicia una nueva ejecución.

**Comprobación:** `python main.py --through 2A`. **Resultado para contrastar:** step=0, target=0.0, executed=0.0.

### 2B · Avanza el objetivo

**Archivo:** `execution.py`. **Encargo:** completa advance_target(): devuelve False al agotar sizes; si queda intervalo, suma sizes[step] a target, incrementa step y devuelve True.

**Comprobación:** `python main.py --through 2B`. **Resultado para contrastar:** True, objetivo 0.5; confirmado 0.0.

### 2C · Confirma el fill

**Archivo:** `execution.py`. **Encargo:** completa on_fill(fill): suma solo fill.size a executed; enviar una orden no aumenta este contador.

**Comprobación:** `python main.py --through 2C`. **Resultado para contrastar:** Confirmado 0.25 BTC.

### 2D · Calcula el déficit

**Archivo:** `execution.py`. **Encargo:** completa pending_size(): devuelve max(0.0, target-executed), sin modificar el estado.

**Comprobación:** `python main.py --through 2D`. **Resultado para contrastar:** Tras avanzar otra vez: objetivo 1, confirmado 0.25, pendiente 0.75.

### 2E · Propón una orden hija

**Archivo:** `execution.py`. **Encargo:** completa on_book_update(book): avanza el objetivo; si queda horizonte y pending_size()>1e-12, devuelve una NewOrder MARKET de ese tamaño; en otro caso devuelve [].

**Comprobación:** `python main.py --through 2E`. **Resultado para contrastar:** Nueva traza inicial sin ejecución; el callback emitirá una acción o [].

### 2F · Predice el segundo envío

**Archivo:** `main.py`. **Encargo:** guarda first_action y second_action de trace.on_book_update(None), confirmando entre ambas un ExecutionFill de 0.25 BTC; predice el segundo tamaño y comprueba que no hay tercer envío.

`trace` ya está creado. Usa el mismo order.id para el fill manual. El remanente de una MARKET caduca: no quedan órdenes abiertas.

**Comprobación:** `python main.py --through 2F`. **Resultado para contrastar:** Primer envío 0.5, segundo 0.75; confirmado sigue en 0.25; tercer envío [].

## Ejercicio 3 · La misma clase en el runner · LIVE

### 3A · Conecta el runner

**Archivo:** `main.py`. **Encargo:** guarda strategy como StudentVWAPStrategy buy, total 1, perfil [1,1]; ejecuta ResearchBacktest con partial_rows, profundidad 1, cash 1000 y fee_bps=10; guarda execution.

**Comprobación:** `python main.py --through 3A`. **Resultado para contrastar:** (.25a 101,.75a 103), cantidad 1, déficit 0;3 fotos y 2 intervalos. Aquí había liquidez suficiente; el calendario no la garantiza.

### 3B · Cierra con coste y cantidad

**Archivo:** `main.py`. **Encargo:** fija arrival en el mid de la primera partial_rows antes de operar; guarda vwap_price con weighted_price, price_cost con execution_cost_bps y residual como total_size-executed.

**Comprobación:** `python main.py --through 3B`. **Resultado para contrastar:** Cantidad 1, residual 0, precio 102.5, coste 250 bps y fees 0.1025. El nombre VWAP del precio de fills no lo convierte en VWAP de mercado.

## Ejercicio 4 · Contrasta el experimento · REQUIRED

### 4A · Cambia el horizonte

**Archivo:** `main.py`. **Encargo:** guarda w20 normalizando veinte unos; calcula total20 sumando slice_sizes(w20,1); predice el peso de cada intervalo.

**Comprobación:** `python main.py --through 4A`. **Resultado para contrastar:** .05 y 1.0.

### 4B · Cambia el perfil

**Archivo:** `main.py`. **Encargo:** normaliza raw_u=[3,1,1,1,4] en pesos_u y calcula sizes_u para 5 BTC; conserva el total.

**Comprobación:** `python main.py --through 4B`. **Resultado para contrastar:** [.3,.1,.1,.1,.4] y[1.5,.5,.5,.5,2]BTC.

### 4C · Compara en el mismo replay

**Archivo:** `main.py`. **Encargo:** ejecuta tu clase buy de 5 BTC con [1]*5 y raw_u sobre schedule_rows; guarda twap_result y vwap_result; compara fills y precio ponderado.

**Comprobación:** `python main.py --through 4C`. **Resultado para contrastar:** Ambos 5 BTC a precio 101. Coincidir en una muestra no implica que todos los perfiles sean equivalentes.

### 4D · Comprueba el signo de venta

**Archivo:** `main.py`. **Encargo:** calcula coste_bps de una venta a 99974.5 frente al arrival 100000 y explica por qué un coste positivo es adverso.

**Comprobación:** `python main.py --through 4D`. **Resultado para contrastar:** 2.55 bps: precio de venta inferior a referencia.

### 4E · Reconstruye la media

**Archivo:** `main.py`. **Encargo:** calcula avg_manual para 0.25 BTC a 101 y 0.75 a 103; explica por qué 102, la media simple, no representa esos fills.

**Comprobación:** `python main.py --through 4E`. **Resultado para contrastar:** 102.5 y 102.5.

### 4F · Distingue las poblaciones

**Archivo:** `main.py`. **Encargo:** calcula vwap_sesion con precios [100,101,102] y volumenes [5,2,1]; contrasta con vwap_price y explica por qué el volumen futuro solo sirve para evaluar después.

**Comprobación:** `python main.py --through 4F`. **Resultado para contrastar:** 100.5 frente a 102.5; son poblaciones distintas.

### 4G · Repite vendiendo

**Archivo:** `main.py`. **Encargo:** ejecuta tu clase sell de 1 BTC con [1,1] sobre partial_rows; guarda sell_result y ejecutado como suma de tamaños de sus fills; explica el signo de final_position.

**Comprobación:** `python main.py --through 4G`. **Resultado para contrastar:** Ejecutado 1, posición −1 y coste 0 bps: 0.5 a 99 y 0.5 a 101 promedian 100. No significa ejecución gratuita frente a cada decision mid.

## Ejercicio 5 · Transfiere a liquidez insuficiente · REQUIRED

### 5A · El horizonte termina

**Archivo:** `main.py`. **Encargo:** copia partial_rows en short_rows y cambia solo ask_size_1 de la segunda foto a 0.5; ejecuta sparse_strategy y sparse_result, calcula shortfall y comprueba que otra foto líquida no abre un nuevo intervalo.

**Antes de ejecutar:** predice si añadir una cuarta foto muy líquida completaría el déficit sin alargar el perfil. Comprueba tu respuesta llamando de nuevo on_book_update(None), sin modificar la clase. Justifica la diferencia entre fin del calendario y completar el encargo.

**Comprobación:** `python main.py --through 5A`. **Resultado para contrastar:** Confirmado 0.75, déficit 0.25, 2 intervalos y 3 fotos; [] después. La liquidez del último intervalo limita la ejecución.

## Ejercicio 6 · Variantes y previsiones · OPTIONAL

### 6A · Escala el perfil

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: guarda a y b como pesos de dos estrategias buy de 1 BTC con perfiles [2]*5 y [1]*5; predice si cambian las proporciones.

**Comprobación:** `python opcionales.py --through 6A`. **Resultado para contrastar:** True y cinco pesos 0.2.

### 6B · Cambia el fill

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: crea variant buy de 1 BTC con [1,1], pide first, confirma un fill de 0.4 BTC y guarda next_size de la siguiente acción.

**Comprobación:** `python opcionales.py --through 6B`. **Resultado para contrastar:** .4 y 0.6 BTC.

### 6C · Media de una ventana

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: completa rolling_mean(xs,k): exige k entero entre 1 y len(xs), lanza ValueError fuera del dominio y devuelve la media de los últimos k valores.

**Comprobación:** `python opcionales.py --through 6C`. **Resultado para contrastar:** últimos dos: 3.5 toda la serie: 2.5

### 6D · Predice con pasado

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: guarda pred como media de los últimos tres volumes=[100,120,90,110,130], sin consultar un volumen futuro.

**Comprobación:** `python opcionales.py --through 6D`. **Resultado para contrastar:** próximo volumen estimado: 110.0

### 6E · Normaliza predicciones

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: guarda profile normalizando preds=[120,80,200] con tu función normalize_profile.

**Comprobación:** `python opcionales.py --through 6E`. **Resultado para contrastar:** perfil: [0.3, 0.2, 0.5] suma: 1.0

### 6F · Reparte un déficit

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: completa correction(target_so_far,executed,remaining_slices): exige valores finitos y 0<=executed<=target_so_far e intervalos enteros positivos; devuelve el déficit dividido por intervalos, o lanza ValueError.

Suponemos que no hay órdenes abiertas. El extra 0.1 por intervalo para (.5,.3,2) no es el tamaño total de la siguiente orden. Esta función no se conecta a la estrategia requerida.

**Comprobación:** `python opcionales.py --through 6F`. **Resultado para contrastar:** extra por intervalo: 0.1 sin déficit: 0.0 Es un extra por intervalo, no el tamaño total de la próxima orden.

### 6G · Una recta completa

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: completa slope(xs,ys) con productos centrados divididos por variación de x; exige pares finitos del mismo tamaño, al menos dos y x variable; calcula b, intercept y prediction para xs=[1,2,3], ys=[3,5,7], x nuevo 4.

Calcula mx y my; suma (x−mx)(y−my) y divide por suma (x−mx)². Intercepto=my−b·mx. Un par ilustrativo describe una recta; no valida predicción fuera de muestra ni permite usar volumen futuro como feature.

**Comprobación:** `python opcionales.py --through 6G`. **Resultado para contrastar:** pendiente: 2.0 intercepto: 1.0 predicción x=4: 9.0 El ajuste describe estos tres pares; no valida una predicción fuera de muestra.

### 6H · Transfiere fuera del mercado

**Archivo:** `opcionales.py`. **Encargo:** OPTIONAL: guarda plan de 100 barras normalizando demanda=[5,10,20,25,20,10,6,4] y usando slice_sizes; explica qué representa cada tamaño.

**Comprobación:** `python opcionales.py --through 6H`. **Resultado para contrastar:** plan de barras: [5.0, 10.0, 20.0, 25.0, 20.0, 10.0, 6.0, 4.0] total: 100.0

## Cierre

Guarda los cambios, abre una terminal nueva y repite `python main.py`. Ejecuta `python opcionales.py` solo si has completado la ruta OPTIONAL. Si te atascas, consulta el mismo apartado en [soluciones](solutions/solucion.md): cada archivo resuelto conserva el encargo y su respuesta debajo. La siguiente lesson cambia el generador de fills a llegadas pasivas; conserva signos, unidades y contabilidad.
