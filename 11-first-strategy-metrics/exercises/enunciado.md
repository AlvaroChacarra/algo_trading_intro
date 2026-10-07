# L11 · El final no cuenta toda la historia.

**Objetivo.** Construir un diagnóstico que separe resultado, coste y riesgo del mismo backtest.

Edita `main.py`, `metrics.py` y `signals.py`. Empieza en **1A**, `main.py/practice`,
con `python main.py --through 1A` desde `exercises`. La plantilla imprime el escenario
y «Completa 1A en main.py»: ese estado incompleto es esperado. Completa por orden
con `--through 1B`, `--through 1C`…; no necesitas resolver huecos posteriores para
observar el apartado actual. Guarda tu intento personal antes de consultar la solución.

| Archivo | Papel |
|---|---|
| `metrics.py` | A completar: picos, caídas, drawdown, precio ponderado, coste, inventario y captura de referencia. |
| `signals.py` | A completar: la decisión de ImbalanceStrategy; constructor thr proporcionado. |
| `main.py` | A completar: experimentos y diagnóstico; llamadas y observaciones intermedias proporcionadas. |
| `known_strategies.py`, `runner.py` | Bases completas: Hold/BuyOnce/SellOnce y ResearchBacktest/ResearchResult. No modificarlas. |
| `market.py`, `matching.py`, `book.py`, `adapters.py`, `base_book.py`, `portfolio.py` | Bases locales incluidas desde sus respuestas canónicas; no modificarlas. |
| `metrics_support.py`, `scenarios.py`, `benchmarks.py` | Fotos/dibujo, helpers y control aleatorio proporcionados; no contienen tus métricas ni tu señal. |
| `exchange/` | Mensajes, contratos y referencia tipada proporcionados; la práctica ejecuta el runner local. |
| `opcionales.py` | Variantes 5A–5D OPTIONAL, separadas de la ruta requerida. |
| `solutions/solucion.md` | Respuesta por apartado y un archivo completo copiable por módulo. |

**Datos.** Cinco fotos sintéticas, mids 100/102/100/103/97, precios USDT/BTC,
tamaños BTC, caja 1000 y fees 0 salvo 4B. Foto 0: bid 99×2, asks 101×0.4/102×0.6.
Timestamp 0/1 explícito; después, índice 2/3/4 como orden docente. El mid se captura
antes de consumir el libro. Las filas no se modifican al repetir. Procedencia, CSV de
consulta y límites en `exchange/_data/README.md`; no hay descarga ni montaje previo.

**Contratos.** ResearchResult ofrece equity_curve, positions, fills, fees y resultados
finales. Un fill tiene side/price/size; pondera por size confirmado. Las métricas leen
esos registros y no modifican la cartera. Equity/coste/drawdown están en USDT;
posición y máximo inventario, en BTC; precio, en USDT/BTC; coste relativo, en bps.
Para equity la base es 1000; para una curva de PnL, 0. None sin fills significa ausencia,
no coste cero. execution_cost_bps exige un arrival finito positivo y fills de un solo lado.
Parent arrival precede al plan completo; decision mid precede a cada envío. Con una
única compra inicial coinciden. Fees se informan aparte. No hay financiación, margen
ni cola pasiva modelados; los cortos están permitidos.

**Autonomía.** Las métricas nuevas reciben guía. Las llamadas al runner y la composición
del diagnóstico reutilizan habilidades anteriores con menos pistas. Antes de 3E predice
si un umbral menor asegura mejor PnL y justifica la comparación; OPTIONAL no es necesario.

## Ejercicio 1 · Leer el recorrido

### 1A · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Ejecuta BuyOnce(1) con las cinco metric_rows, cash=1000 y sin fees; guarda result para medir el mismo experimento.

Usa metric_rows, BuyOnce(1) y un mercado nuevo; no rehagas su contabilidad. Después de la compra se conserva la posición y cambia el mark.

**Comprueba:** `python main.py --through 1A`.

<details><summary>Resultado para contrastar después del intento</summary>

Equity [998.4,1000.4,998.4,1001.4,995.4], dos fills (101×0.4,102×0.6), caja 898.4 y posición 1. La compra cambia caja/posición; después cambia el mark.

</details>

### 1B · running_peaks

**Dónde:** `metrics.py` → `running_peaks`.

**Qué y para qué:** Conserva el mayor pico visto en running_peaks, empezando en initial_equity; devuelve un pico por observación.

Inicializa peak con initial_equity y recorre en orden. La longitud de salida coincide con equity. Prueba también [] y [999,998] con base 1000.

**Comprueba:** `python main.py --through 1B`.

<details><summary>Resultado para contrastar después del intento</summary>

Picos [1000,1000.4,1000.4,1001.4,1001.4]. La caja inicial cuenta como primer pico aunque la primera equity ya tenga un coste.

</details>

### 1C · drawdowns

**Dónde:** `metrics.py` → `drawdowns`.

**Qué y para qué:** Compón running_peaks para devolver pico menos equity en cada observación, sin modificar la curva.

Usa running_peaks y los valores de la misma curva. Para una curva de PnL debes pasar initial_equity=0.

**Comprueba:** `python main.py --through 1C`.

<details><summary>Resultado para contrastar después del intento</summary>

Caídas [1.6,0,2,0,6] USDT: pico previo menos equity actual. La curva original no cambia.

</details>

### 1D · max_drawdown

**Dónde:** `metrics.py` → `max_drawdown`.

**Qué y para qué:** Devuelve la mayor caída calculada por drawdowns; una curva vacía devuelve 0.0.

Usa tus drawdowns; no calcules solo primera menos última equity. Predice la peor caída antes de ejecutar.

**Comprueba:** `python main.py --through 1D`.

<details><summary>Resultado para contrastar después del intento</summary>

Drawdown máximo 6 USDT, desde 1001.4 hasta 995.4. PnL final −4.6 USDT: mide otra pregunta. Curva vacía: 0.

</details>

## Ejercicio 2 · Medir coste y exposición

### 2A · weighted_price

**Dónde:** `metrics.py` → `weighted_price`.

**Qué y para qué:** Pondera price por size en weighted_price; divide por cantidad confirmada y devuelve None sin fills.

Los fills de result tienen tamaños 0.4 y 0.6. Razona por qué no valen lo mismo al promediar.

**Comprueba:** `python main.py --through 2A`.

<details><summary>Resultado para contrastar después del intento</summary>

Precio ponderado 101.6 USDT/BTC: (101×0.4+102×0.6)/1. La media simple 101.5 ignora tamaños. Sin fills: None.

</details>

### 2B · execution_cost_bps

**Dónde:** `metrics.py` → `execution_cost_bps`.

**Qué y para qué:** Calcula execution_cost_bps frente al arrival previo, con signo buy/sell; conserva las guardias proporcionadas y separa fees.

Las guardias de referencia, lado y agrupación ya están escritas. Compón weighted_price, aplica signo +1 buy/−1 sell y convierte la diferencia relativa a bps. Positivo=adverso, negativo=favorable; no sumes fees aquí.

**Comprueba:** `python main.py --through 2B`.

<details><summary>Resultado para contrastar después del intento</summary>

Arrival 100, coste adverso 160 bps; 1 bps=1/10000. BUY por encima o SELL por debajo da coste positivo. La comisión es otra cifra. Sin fills válidos: None; nunca precio ficticio cero.

</details>

### 2C · max_inventory

**Dónde:** `metrics.py` → `max_inventory`.

**Qué y para qué:** Devuelve el máximo valor absoluto de positions, o 0.0 si está vacío; mide inventario muestreado en BTC.

Las posiciones son cierres de cada foto. Explica qué puede perder ese muestreo si compras y vendes dentro de la misma foto.

**Comprueba:** `python main.py --through 2C`.

<details><summary>Resultado para contrastar después del intento</summary>

Máximo |q|=1 BTC, final=1 BTC. Con [0,−2,0], final 0 y máximo 2. Solo mide las posiciones registradas al cierre de cada foto: no el máximo entre fills.

</details>

## Ejercicio 3 · Comparar reglas con controles explícitos

### 3A · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Ejecuta Hold con las mismas filas, caja y fees que BuyOnce; guarda hold_result como control sin operaciones.

Usa las mismas cinco fotos, cash=1000 y fee_bps=0. Predice los resultados antes de ejecutar.

**Comprueba:** `python main.py --through 3A`.

<details><summary>Resultado para contrastar después del intento</summary>

Hold: 5 fotos, 0 fills, posición 0, PnL 0, drawdown 0. Es un control válido para el resultado; no ejecuta la misma cantidad que BuyOnce.

</details>

### 3B · capture_arrival

**Dónde:** `metrics.py` → `capture_arrival` y `main.py` → `practice`.

**Qué y para qué:** Completa capture_arrival y guarda arrival, pnl, pasos y n_fills del experimento original; separa equity de PnL.

Actúa en dos sitios: metrics.py/capture_arrival y main.py/practice. La función avanza un mercado nuevo una vez; el principal captura arrival y lee los otros tres valores de result.

**Comprueba:** `python main.py --through 3B`.

<details><summary>Resultado para contrastar después del intento</summary>

Arrival 100; PnL −4.6 USDT; 5 fotos y 2 fills. capture_arrival([]) devuelve None. El mercado de referencia es nuevo y no adelanta el experimento.

</details>

### 3C · ImbalanceStrategy.on_book_update

**Dónde:** `signals.py` → `ImbalanceStrategy.on_book_update`.

**Qué y para qué:** Implementa ImbalanceStrategy con thr parametrizable, imbalance(3) y clip 0.05 MARKET; None e igualdad devuelven [].

El constructor self.thr está proporcionado. El lado buy corresponde a imb>thr; sell a imb<−thr. Consulta imbalance(3) una vez y usa book.symbol. La variante no añade un límite de inventario.

**Comprueba:** `python main.py --through 3C`.

<details><summary>Resultado para contrastar después del intento</summary>

Imbalance(3), thr 0.3 y clip 0.05: 5 fills, posición 0.25 y PnL −1.1. Se usan hasta tres niveles disponibles; estas fotos tienen menos. None e igualdad no operan. Se conserva el runner, sin introducir límites adicionales.

</details>

### 3D · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Compara mi_equity con el rango de monos en fuera; justifica por qué ese rango no valida una señal.

La construcción de los tres controles y sus resultados está proporcionada, con semillas 7/21/99. Completa solo fuera usando mi_equity y monos. Escribe por qué debes mirar fills y exposición y por qué tres semillas no forman una prueba estadística.

**Comprueba:** `python main.py --through 3D`.

<details><summary>Resultado para contrastar después del intento</summary>

Controles: PnL [−1.05,−0.15,−0.5], fills [4,3,5]; fuera=True para −1.1. Dentro o fuera de tres resultados no valida edge. Comparten fotos, caja, tarifa y clip; su actividad y exposición no son iguales.

</details>

### 3E · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Predice y ejecuta los umbrales 0.1 y 0.5 en low/high; calcula ratio_a y ratio_b y explica las unidades de sus denominadores.

**Transferencia REQUIRED: predice antes de ejecutar.** Mantén datos, caja y tarifa; cambia solo thr. ¿Más actividad implica mejor resultado? Los ratios 30 USDT/2 BTC y 24 USDT/0.4 BTC son ejemplos separados, no resultados de esas filas: explica sus unidades y sus límites.

**Comprueba:** `python main.py --through 3E`.

<details><summary>Resultado para contrastar después del intento</summary>

thr 0.1: 5 fills, máximo inventario 0.25 BTC y PnL −1.1. thr 0.5: 0 fills, inventario 0 y PnL 0. Menor umbral no garantiza mejor PnL. Los ratios ilustrativos son 15 y 60 USDT/BTC, no Sharpe ni riesgo completo; elegir sobre la misma muestra no demuestra alpha.

</details>

## Ejercicio 4 · Componer el diagnóstico

### 4A · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Compón summary con pnl, drawdown, cost_bps y max_inventory del mismo result, sin redefinir las métricas.

Aplica las funciones ya construidas a result. Claves exactas: pnl, drawdown, cost_bps, max_inventory. Conserva el arrival previo y no redefinas funciones.

**Comprueba:** `python main.py --through 4A`.

<details><summary>Resultado para contrastar después del intento</summary>

summary: pnl −4.6 USDT, drawdown 6 USDT, cost_bps 160, max_inventory 1 BTC. Se componen funciones, sin rehacer la contabilidad ni cambiar ResearchResult.

</details>

### 4B · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Ejecuta otra vez BuyOnce con 10 bps en fee_result; conserva arrival y compara precio, comisión y resultado.

Predice qué cambia con 10 bps y qué queda igual. No es obligatorio que cualquier coste cambie el máximo drawdown: justifica también ese resultado en estas filas.

**Comprueba:** `python main.py --through 4B`.

<details><summary>Resultado para contrastar después del intento</summary>

Mismos fills, precio ponderado y coste 160 bps. Fee 0.1016 USDT; PnL −4.7016; equity final 995.2984. Drawdown máximo sigue en 6: restar ese mismo coste a pico y valle no cambia su diferencia en este caso.

</details>

## Ejercicio 5 · Variantes OPTIONAL

### 5A · practice · OPTIONAL

**Dónde:** `opcionales.py` → `practice`.

**Qué y para qué:** OPTIONAL: calcula dd_a y dd_b con initial_equity=0 para dos curvas que terminan en el mismo PnL.

OPTIONAL. Series de PnL [0,−1,−2] y [0,3,1,4,−2]. La caja inicial de esas series es 0; no son otros resultados de BuyOnce.

**Comprueba:** `python opcionales.py --through 5A`.

<details><summary>Resultado para contrastar después del intento</summary>

OPTIONAL. Ambas curvas acaban en −2 USDT; drawdowns 2 y 6. Una cuenta de PnL usa base 0; una de equity usa su caja inicial.

</details>

### 5B · practice · OPTIONAL

**Dónde:** `opcionales.py` → `practice`.

**Qué y para qué:** OPTIONAL: calcula exposure_a y exposure_b para dos recorridos que terminan planos, sin confundir final con máximo.

OPTIONAL. Recorridos [0,1,0] y [0,−3,0] BTC. Ambos terminan planos; compara sus máximos.

**Comprueba:** `python opcionales.py --through 5B`.

<details><summary>Resultado para contrastar después del intento</summary>

OPTIONAL. Ambas posiciones finales son 0; máximos absolutos 1 y 3 BTC. Terminar plano no describe la exposición anterior.

</details>

### 5C · practice · OPTIONAL

**Dónde:** `opcionales.py` → `practice`.

**Qué y para qué:** OPTIONAL: guarda curve del nuevo result y localiza el pico y valle de su peor caída; usa el dibujo proporcionado.

OPTIONAL. El auxiliar ya reconstruye result con las mismas fotos. No copies un resultado antiguo ni implementes gráficos. Usa la lista numérica para localizar pico y valle.

**Comprueba:** `python opcionales.py --through 5C`.

<details><summary>Resultado para contrastar después del intento</summary>

OPTIONAL. Curva de cinco puntos; pico en foto 3 (1001.4), valle en foto 4 (995.4), caída 6 USDT. En terminal la lista es la observación; el dibujo proporcionado está disponible si se ejecuta en un entorno con IPython.

</details>

### 5D · practice · OPTIONAL

**Dónde:** `opcionales.py` → `practice`.

**Qué y para qué:** OPTIONAL: calcula kcal por euro de las dos cestas y guarda mejor; explica qué mide y qué omite ese ratio.

OPTIONAL. Las cestas y precios ya están proporcionados. Compara solo kcal/€; mayor ratio no significa mejor nutrición.

**Comprueba:** `python opcionales.py --through 5D`.

<details><summary>Resultado para contrastar después del intento</summary>

OPTIONAL. A=300 y B=375 kcal/€; mejor=B según ese ratio. No mide calidad nutricional, como PnL por inventario no mide todo el riesgo.

</details>

## Cierre

Ejecuta `python main.py`: el diagnóstico separa PnL, caída, precio de ejecución, fees e inventario. L12 reutilizará las métricas ponderadas para comparar calendarios de ejecución. OPTIONAL: `python opcionales.py`, si eliges esas variantes.
