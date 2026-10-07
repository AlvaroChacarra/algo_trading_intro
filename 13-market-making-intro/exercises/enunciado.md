# L13 · Tu puesto de intercambio

Vas a ofrecer dos precios, contabilizar fills confirmados y construir un maker que mueve sus quotes según el inventario.

Edita **maker.py**, **main.py** y, solo si quieres la ampliación, **opcionales.py**. Fill, PositionTracker y research_support.py ya están incluidos. Conserva una copia personal de esta carpeta antes de editar; no necesitas abrir otra lesson ni trasladar archivos.

Empieza con `python main.py --through 1A`. Al inicio verás `Completa 1A en maker.py.`: es el estado pendiente esperado. Completa cada apartado y ejecuta hasta su etiqueta; al final, `python main.py`. Las respuestas están en `solutions/solucion.md`, con archivos completos y comentarios de cada apartado.

**Modelo:** precios en unidades monetarias por unidad, inventario en unidades y caja/equity en unidades monetarias. Fills manuales confirmados, sin costes. Simulación sintética de horizonte 1; llegadas y shocks independientes, sin cola, latencia o impacto. No modela flujo informado ni acredita rentabilidad.

**Autonomía:** aplica Fill, consultas de equity y llamadas a funciones con menos ayuda. El centro por inventario y la diferencia entre tasa y probabilidad se guían explícitamente.

## Ejercicio 1 · Quotes y cuenta: ofrecer no es cobrar

### 1A · Construye dos quotes

En `maker.py`, Completa fixed_quotes(center, half_spread): devuelve bid como center menos half_spread y ask como center más half_spread; conserva un ancho total de dos medios spreads.

**Comprueba:** `python main.py --through 1A`. 99.40 / 100.60; ancho 1.20. Son precios ofrecidos, todavía no fills.

### 1B · Contabiliza la compra confirmada

En `main.py`, Crea tracker = PositionTracker() y aplica Fill("buy", bid, 0.1) al bid calculado; contabiliza únicamente esta compra confirmada.

**Comprueba:** `python main.py --through 1B`. Caja −9.94, q +0.1, equity 0.06 a mark 100. La compra cambia caja y posición.

### 1C · Cambia solo la valoración

En `main.py`, Guarda marked_equity consultando tracker.equity(99), sin aplicar otro fill ni cambiar caja o posición; predice qué columnas cambian.

**Comprueba:** `python main.py --through 1C`. Equity −0.04; caja −9.94 y q +0.1 se conservan. Revalorar no genera una venta.

### 1D · Completa la vuelta

En `main.py`, Aplica Fill("sell", ask, 0.1) a la misma tracker; este ejemplo confirma una venta al ask original, con quotes fijas y sin costes.

**Comprueba:** `python main.py --through 1D`. Caja/equity 0.12 y q 0. Esa vuelta exige ambos fills a las quotes fijas; no es un beneficio garantizado.

## Ejercicio 2 · Tu clase mueve el centro

### 2A · Una clase, el mismo constructor de quotes

En `maker.py`, Completa StudentMarketMaker.reservation_price(mid, tau): resta self.skew por self.inventory al mid; conserva tau en la firma aunque el skew fijo no lo utilice.

**Comprueba:** `python main.py --through 2A`. Con q=0.3, centro 99.40 y quotes 98.80 / 100.00. Hereda parámetros de MakerBase y sobrescribe el centro; quotes reutiliza fixed_quotes. tau queda disponible para la clase hija de L14.

### 2B · Separa centro y ancho

En `main.py`, Consulta flat_quotes con maker.inventory = 0 y long_quotes con maker.inventory = 0.3; compara el centro y el ancho sin modificar half_spread.

**Comprueba:** `python main.py --through 2B`. 99.40/100.60 frente a 98.80/100.00, ancho 1.20 en ambos. El centro baja 0.60; el ancho permanece.

### 2C · Una variante anunciada

En `main.py`, Crea wide_position con half_spread=0.5 y skew=1, fija inventory=2 y guarda variant_quotes para mid=100 y tau=1; anuncia el cambio de parámetros.

**Comprueba:** `python main.py --through 2C`. 97.50 / 98.50; centro 98 y ancho 1. Es una variante explícita, no el caso inicial.

### 2D · Invierte el inventario

En `main.py`, Fija maker.inventory = -0.3 y guarda short_quotes con mid=100 y tau=1; predice hacia dónde se moverán ambas quotes.

**Comprueba:** `python main.py --through 2D`. 100.00 / 101.20. Estar corto eleva ambos precios: el bid invita a comprar y el ask intenta frenar nuevas ventas. No garantiza liquidación.

### 2E · Valora una venta parcial

En `main.py`, Crea partial_tracker, compra 0.1 al bid y vende solo 0.04 al ask; guarda partial_equity a mark 100 y explica qué riesgo queda abierto.

**Comprueba:** `python main.py --through 2E`. q 0.06 y equity 0.084. Se realizó solo parte de la vuelta; la valoración depende del mark mientras quede posición.

## Ejercicio 3 · Tu maker entra en el simulador

### 3A · El cierre usa tu clase

En `main.py`, Crea simulation_maker = StudentMarketMaker() y guarda records = simulate(simulation_maker, seed=2026, sigma=0.5, steps=500); el simulador debe consumir tu clase.

**Comprueba:** `python main.py --through 3A`. cierre propio: pnl 2.2878; máximo q 0.400; pasos 500. Una semilla reproducible no garantiza rentabilidad ni menor riesgo para cada otra regla. simulate reinicia inventory y actualiza su propia caja; no llama a PositionTracker ni a ResearchBacktest.

`simulate(maker, seed, steps, sigma, intensity=50, kappa=1.5)` llama a `quotes(mid, tau)`, sortea contrapartidas y actualiza inventario/caja directamente. Reinicia el inventario; sus registros contienen `(PnL marcado, posición)`, `final_pnl` y `max_inventory`. Es distinto del replay: las fotos no crean llegadas pasivas.

### 3B · Lee el riesgo que quedó abierto

En `main.py`, Guarda terminal_q desde el último registro de records y max_q desde records.max_inventory; explica por qué el máximo absoluto no es la posición final.

**Comprueba:** `python main.py --through 3B`. El máximo absoluto se observa después de cada fill, incluso si dos fills del mismo paso se compensan. terminal_q describe el cierre y puede ser menor. PnL incluye valoración de inventario abierto, no solo vueltas cerradas.

## Ejercicio 4 · El ruido, el riesgo y las llegadas

### 4A · Conserva la escala del ruido

En `main.py`, Calcula shock_sd para sigma=2 y cuatro pasos de igual duración; suma sus varianzas independientes en total_variance y explica por qué no sumas desviaciones.

**Comprueba:** `python main.py --through 4A`. shock_sd=1 y total_variance=4. Para dt=1/4, desviación sigma×sqrt(dt); al sumar cuatro varianzas recuperas sigma², con independencia de los shocks.

### 4B · Utilidad antes de gamma

En `main.py`, Completa cara_utility(wealth, gamma) con -math.exp(-gamma * wealth); compara U(5) y U(10) con gamma=0.1, distinguiendo utilidad de dinero.

**Comprueba:** `python main.py --through 4B`. U(5)=−0.606531 y U(10)=−0.367879: mayor riqueza tiene mayor utilidad. Para gamma=0.5, la opción segura W=0 puntúa −1 y la lotería −1/+1 puntúa −1.127626; misma media, distinta preferencia. Utilidad es una puntuación, no euros; comparar dentro del mismo gamma.

### 4C · Intensidad antes de kappa

En `main.py`, Con A=1 y kappa=1.5, calcula lambda_near a distancia 0.2 y lambda_far a distancia 1.0; predice qué ocurre al mantener la tasa y reducir dt a la mitad.

**Comprueba:** `python main.py --through 4C`. Tasas 0.740818 y 0.223130 por horizonte. Más distancia reduce la tasa; no son probabilidades. Transferencia: p=1−exp(−lambda×dt), p_fina=1−exp(−lambda×dt/2). Disminuye, pero no es exactamente p/2. Lambda tiene unidades de 1/tiempo y puede superar 1; p está entre 0 y 1. No cambia el centro ni el ancho.

**Transferencia antes de consultar:** mantén lambda_near y calcula p para dt=1/500 y dt=1/1000 en la consola. Anticipa si la segunda es exactamente la mitad y justifica unidades. Esta prueba no requiere OPTIONAL.

## Ejercicio 5 · Variantes · OPTIONAL

### 5A · Inventario negativo

En `opcionales.py`, OPTIONAL: crea negative = StudentMarketMaker(), fija inventory=-0.5 y guarda negative_quotes para mid=100 y tau=1.

**Comprueba:** `python opcionales.py --through 5A`. 100.40 / 101.60. Usa la misma clase terminada; no hay una segunda implementación del maker.

### 5B · El centro se mueve, el ancho no

En `opcionales.py`, OPTIONAL: fija negative.inventory=0.5 y guarda positive_quotes; calcula same_width comparando ambos anchos con tolerancia 1e-9.

**Comprueba:** `python opcionales.py --through 5B`. 98.40 / 99.60 y same_width=True. La corrección tiene signo opuesto y conserva ancho 1.20.

### 5C · De tasa a probabilidad

En `opcionales.py`, OPTIONAL: calcula rate con A=50, kappa=1.5 y distancia 0.2; conviértela en probability por paso mediante 1 - exp(-rate / 500).

**Comprueba:** `python opcionales.py --through 5C`. Tasa 37.041 por horizonte; probabilidad 0.07140 por paso. El simulador admite como máximo un fill por lado y paso; al cruzar el mid fuerza probabilidad 1, una simplificación explícita.

## Cierre

Al ejecutar el principal debes ver las quotes iniciales, la cuenta de la vuelta, centro y ancho de tu clase y `cierre propio: pnl 2.2878; máximo q 0.400; pasos 500`. Explica qué parte del PnL corresponde a inventario abierto. Guarda tu intento y sus observaciones. El simulador usa tu implementación; cambiar de semilla exige interpretar de nuevo el resultado.

## Contrato proporcionado · consulta REQUIRED

Tu clase de investigación recibe `quotes(mid, tau)`; el SDK de referencia usa `Strategy`, órdenes LIMIT y callbacks. Compartir la interfaz de estrategias no crea por sí mismo llegadas pasivas. Este ejemplo está proporcionado: no es un ejercicio ni reemplaza StudentMarketMaker.

```python
from exchange import OrderBook as RefBook, Level as RefLevel, Fill as RefFill
from exchange.strategies.market_maker import MarketMaker as ReferenceMaker
reference = ReferenceMaker('XYZ', quote_size=0.1, half_spread=0.6,
                           inventory_skew=2.0)
reference_book = RefBook('XYZ', [RefLevel(99, 1)], [RefLevel(101, 1)])
reference_actions = reference.on_book_update(reference_book)
reference_q_before_fill = reference.inventory
buy_order = reference_actions[0].order
reference.on_fill(RefFill(buy_order.id, 'XYZ', 'buy', buy_order.price, 0.1))
reference_q_after_fill = reference.inventory
```

En Backtest, on_book_update propone acciones y on_fill confirma los fills del matching. En MMSimulation de referencia se llama directamente a quotes(book) y luego a on_fill por llegadas sintéticas. En nuestra práctica simulate llama a quotes(mid,tau) y actualiza inventory directamente. Mantén estos contratos separados.
