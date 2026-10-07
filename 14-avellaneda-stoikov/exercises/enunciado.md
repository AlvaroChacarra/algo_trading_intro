# L14 · Mismo inventario. ¿Mismas quotes?

Construye una regla que calcula centro y ancho según inventario, riesgo y tiempo restante; después contrástala con un control fijo.

Edita **maker.py** y **main.py**; **opcionales.py** es la ampliación. La clase padre de base_maker.py y simulate de research_support.py están incluidos. Guarda una copia personal de esta carpeta.

Empieza con `python main.py --through 1A`. Verás `Completa 1A en maker.py.` hasta resolver el primer método; los huecos futuros no bloquean su resultado. Continúa por etiqueta y, al terminar, ejecuta `python main.py`. Consulta `solutions/solucion.md`: un archivo completo por bloque, con los encargos y respuestas junto a su código.

**Modelo y unidades:** horizonte 1, tau fracción restante; sigma desviación de precio por horizonte, gamma aversión CARA por unidad monetaria, kappa sensibilidad de las llegadas por unidad de precio. Q mide unidades, centro/ancho precio por unidad; PnL marcado en unidades monetarias. Simulación sintética sin costes, cola, latencia, impacto o flujo informado. Es una aproximación de A–S bajo estas hipótesis, sin derivación ni calibración.

**Autonomía:** combina llamadas, instancias y tablas con menos ayuda; los cálculos nuevos tienen guía. No edites quotes ni el simulador: la hija sobrescribe el centro y el ancho. Gamma/kappa deben ser finitos y positivos; sigma, finita y no negativa.

## Ejercicio 1 · Construye tu clase

### 1A · Ajuste de inventario

En `maker.py`, completa StudentAvellanedaStoikov.inventory_adjustment(tau): devuelve self.inventory por self.gamma por self.sigma al cuadrado por tau; calcula el ajuste en unidades de precio.

**Comprueba:** `python main.py --through 1A`. Ajuste 0.125000 con q=1, gamma=.5, sigma=.5 y tau=1. Sigma es desviación por horizonte; sigma² es varianza. El ajuste positivo se restará al mid.

### 1B · Centro propio

En `maker.py`, completa reservation_price(mid, tau): resta al mid el resultado de self.inventory_adjustment(tau); reutiliza el método anterior para construir el centro.

**Comprueba:** `python main.py --through 1B`. Centro 99.875000. La llamada a tu método evita duplicar la regla. Un inventario negativo invierte el signo.

### 1C · Ancho total

En `maker.py`, completa spread(tau): suma risk = gamma por sigma al cuadrado por tau y flow = (2/gamma) por math.log1p(gamma/kappa); devuelve ancho total, que quotes dividirá entre dos.

**Comprueba:** `python main.py --through 1C`. Riesgo .125 + liquidez 1.150728 = ancho 1.275728; bid 99.237136, ask 100.512864. log1p(x) es ln(1+x), inversa de exp; quotes heredado coloca medio ancho a cada lado del centro.

## Ejercicio 2 · Comprueba sin azar

### 2A · Varía solo q

En `main.py`, fija maker.inventory=-1 y guarda short_quotes; después fija inventory=0 y guarda flat_quotes, siempre con mid=100 y tau=1; predice centro y ancho antes de ejecutar.

**Comprueba:** `python main.py --through 2A`. Con q=-1 el centro es 100.125; con q=0, 100. Ambos anchos son 1.275728. Q afecta al centro, no figura en spread.

### 2B · Varía solo tau

En `main.py`, fija maker.inventory=1 y guarda time_quotes como pares (tau, quotes) para tau 1, 0.5 y 0; explica qué cambia y qué sigue abierto al final.

**Comprueba:** `python main.py --through 2B`. Centros 99.875, 99.9375, 100; anchos 1.275728, 1.213228, 1.150728. A tau=0 queda el término de liquidez y q sigue en 1: calcular quotes no liquida. simulate cotiza tau=1-step/steps y no llama quotes en tau=0.

### 2C · Comprueba el signo sin azar

En `main.py`, crea sign_maker con gamma=0.5, sigma=0.5 y kappa=1.5; guarda centers para inventarios -2, 0 y 2, con mid=100 y tau=1, sin simular.

**Comprueba:** `python main.py --through 2C`. Centros [100.25, 100, 99.75]. Largo baja el centro; corto lo sube. Esto es una preferencia de flujo, no garantía de ejecución.

### 2D · Detecta el cuadrado de sigma

En `main.py`, crea un maker por cada sigma de (0.5, 1.0), fija q=1 y guarda sus inventory_adjustment(1) en sigma_adjustments; predice el factor antes de consultar.

**Comprueba:** `python main.py --through 2D`. Ajustes [.125, .5], factor 4. Duplicar sigma cuadruplica su varianza; esta comprobación detecta olvidar el cuadrado. Transferencia: al cambiar también q a -1, cambia el signo del ajuste, no su magnitud; el ancho depende de sigma, no de q.

**Transferencia antes de consultar:** invierte q a -1 en la prueba de sigma, predice qué cambiará en el ajuste y qué ocurrirá con el ancho. Justifica sin simular. No requiere OPTIONAL.

### 2E · Separa los términos del ancho

En `main.py`, guarda liquidity_width consultando maker.spread(0) y risk_width como spread(1) menos liquidity_width; separa los dos términos del ancho sin duplicar la fórmula.

**Comprueba:** `python main.py --through 2E`. Riesgo .125 y liquidez 1.150728. Tau apaga el primero, no el segundo. No son dos medios spreads ni probabilidades.

### 2F · Reconstruye el ancho observado

En `main.py`, consulta las quotes de maker para mid=100 y tau=1 y guarda observed_width como ask menos bid; contrasta el ancho observado con spread(1).

**Comprueba:** `python main.py --through 2F`. Observed_width 1.275728 coincide con spread(1), con tolerancia numérica. El promedio de bid/ask coincide con reservation_price.

### 2G · Una variante anunciada

En `main.py`, crea variant con gamma=0.5, sigma=2 y kappa=0.5, fija q=2 y guarda variant_quotes con mid=100 y tau=0.5; anuncia que este es otro caso.

**Comprueba:** `python main.py --through 2G`. Centro 98; ancho 4.772589, bid 95.613706 y ask 100.386294. Se han cambiado sigma y kappa a la vez; no atribuyas este cambio a un solo parámetro.

## Ejercicio 3 · Contrasta reglas

### 3A · Tu A–S entra en el mismo simulador

En `main.py`, crea simulation_maker con gamma=0.5, sigma=0.5 y kappa=1.5; guarda records = simulate(simulation_maker, seed=2026, steps=500, sigma=simulation_maker.sigma, kappa=simulation_maker.kappa).

**Comprueba:** `python main.py --through 3A`. El simulador consume tu clase y reinicia inventory. Conserva 500 registros, final_pnl y max_inventory después de cada fill. PnL marcado incluye inventario abierto; no se usa el replay ni PositionTracker.

Contrato proporcionado: `simulate(maker, seed=42, steps=500, sigma=.5, intensity=50, kappa=1.5)` llama a `quotes(mid,tau)`, actualiza caja/inventario y devuelve pares `(PnL, q)`, `final_pnl` y `max_inventory`. El máximo se observa después de cada fill. Tau vale `1-step/steps`: el último valor cotizado es 1/steps. Llegadas/shocks independientes, hasta un fill por lado y paso; una quote que cruza mid tiene p=1. Mantén sigma/kappa de la regla coherentes con el mercado.

### 3B · Conserva un control conocido

En `main.py`, guarda control_records simulando StudentMarketMaker() con seed=2026, steps=500, sigma=0.5 y kappa=1.5; conserva el control con skew=2 y half_spread=0.6.

**Comprueba:** `python main.py --through 3B`. Control: PnL 2.2878 y máximo q .4. Coincide con la regla de centro y ancho fijo proporcionada. No cambies control y regla simultáneamente.

### 3C · Compara todas las semillas

En `main.py`, completa compare_rules(seeds): por cada semilla crea control y StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5), simula cada uno con los mismos parámetros y devuelve filas (seed, nombre, PnL, máximo inventario).

**Comprueba:** `python main.py --through 3C`. Seis filas, tres semillas por cada regla, instancias nuevas y entorno común. Una semilla compartida mantiene las mismas tiradas de este simulador, pero reglas distintas pueden aceptar fills distintos.

### 3D · Resume sin borrar la dispersión

En `main.py`, extrae as_pnls de todas las filas StudentAvellanedaStoikov de comparison y guarda pnl_range=(mínimo, máximo); interpreta dispersión sin seleccionar solo la mejor semilla.

**Comprueba:** `python main.py --through 3D`. El rango conserva los extremos de las tres filas A–S; acompáñalo de las filas individuales y los máximos de inventario. No demuestra robustez ni rentabilidad real.

## Ejercicio 4 · Mecanismo y resultado

### 4A · Gamma mueve la fórmula

En `main.py`, guarda gamma_shifts con los ajustes de makers gamma=0.1 y 1.0, sigma=0.5, kappa=1.5 y q=1 a tau=1; separa este cálculo fijo de una simulación.

**Comprueba:** `python main.py --through 4A`. Ajustes [.025, .25]: multiplicar gamma por 10 multiplica este ajuste por 10 con el resto fijo. El término de liquidez también cambia; no presupongas monotonía del ancho total.

### 4B · Gamma cambia trayectorias

En `main.py`, guarda gamma_rows con (gamma, PnL, máximo inventario) para gamma=0.1 y 1.0, seed=3 y steps=50; usa sigma=0.5 y kappa=1.5 en regla y mercado y describe ambas filas sin imponer monotonía.

**Comprueba:** `python main.py --through 4B`. Conserva los dos PnLs y máximos observados. Cambiar gamma modifica las quotes y qué fills se aceptan; no garantiza una ordenación del riesgo o del beneficio entre trayectorias.

### 4C · Recupera centro y ancho del control

En `main.py`, crea control=StudentMarketMaker(), fija q=0.3 y guarda control_center y control_width consultando reservation_price(100,1) y spread(1).

**Comprueba:** `python main.py --through 4C`. Control: centro 99.40 y ancho 1.20. La hija A–S reemplaza el centro y el ancho, manteniendo quotes(mid,tau) y el consumidor.

### 4D · Cotizar no equivale a cobrar

En `main.py`, calcula ideal_round_trip como el ancho ask-bid de 1C por tamaño 0.1; explica qué fills confirmados exigiría cobrarlo y qué inventario puede quedar abierto.

**Comprueba:** `python main.py --through 4D`. Vuelta ideal .127572829: exige compra .1 al bid y venta .1 al ask originales, ambos confirmados, sin costes. No equivale al PnL de una trayectoria ni a un cobro por publicar quotes.

## Ejercicio 5 · Variantes · OPTIONAL

### 5A · Signo y tau cero

En `opcionales.py`, OPTIONAL: crea probe con gamma=0.5, sigma=0.5 y kappa=1.5, fija q=-1 y guarda centers a tau=1 y tau=0.

**Comprueba:** `python opcionales.py --through 5A`. Centros 100.125 y 100; q permanece -1 al consultar tau=0. El reloj no rellena órdenes.

### 5B · Duplica sigma

En `opcionales.py`, OPTIONAL: crea double_sigma con sigma=1.0 y q=-1; guarda quadrupled_shift como razón de los ajustes absolutos a tau=1 frente a probe.

**Comprueba:** `python opcionales.py --through 5B`. Factor 4 por sigma². La razón de magnitudes elimina el signo del inventario.

### 5C · Mide el ancho de las quotes

En `opcionales.py`, OPTIONAL: consulta las quotes de double_sigma para mid=100 y tau=1 y guarda quoted_width=ask-bid; contrasta con spread(1).

**Comprueba:** `python opcionales.py --through 5C`. Ancho 1.650728: riesgo .5 más liquidez 1.150728; medio ancho por lado.

### 5D · Equivalente cierto

En `opcionales.py`, OPTIONAL: completa equiv_certeza(media,gamma,var) con media menos gamma por var dividido entre dos; calcula barato y caro para media=100, var=30 y gamma 0.1 y 2.0.

**Comprueba:** `python opcionales.py --through 5D`. Barato 98.5, caro 70. Para riqueza normal y utilidad CARA, el equivalente cierto penaliza varianza por gamma/2. Es otro cálculo proporcionado para interpretar riesgo, no el PnL de simulate.

## Cierre y capstone

Comprueba ajustes, centro y ancho antes de interpretar las seis filas de tres semillas. No hay una ordenación impuesta entre PnLs o máximos de inventario. Guarda tus resultados y explica qué parte sigue expuesta al precio. El proyecto autónomo tiene su propio `CAPSTONE.md` y `capstone.py`: seis hitos, 90 minutos separados.

## SDK proporcionado · consulta REQUIRED

El SDK usa AvellanedaStoikov(symbol, quote_size, gamma, sigma, kappa, horizon), un reloj time y quotes(book). Su reservation_price(mid) y optimal_spread() usan ese reloj. Nuestra clase recibe tau desde simulate y expone spread(tau): no añade reloj interno. MMSimulation.run() devuelve SimResult con final_pnl/max_inventory. Strategy/on_book_update/on_fill pertenecen al SDK; el capstone y nuestra práctica usan quotes(mid,tau) y simulate directamente.
