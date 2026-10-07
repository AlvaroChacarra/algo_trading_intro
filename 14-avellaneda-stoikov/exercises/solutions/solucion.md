# L14 · Solución de consulta

Copia cada bloque completo a su archivo local; conserva la base y el simulador incluidos. El comentario reproduce el mismo encargo del enunciado, seguido de su respuesta.

| Apartado | Archivo / símbolo |
| --- | --- |
| 1A | maker.py:inventory_adjustment |
| 1B | maker.py:reservation_price |
| 1C | maker.py:spread |
| 2A | main.py:practice |
| 2B | main.py:practice |
| 2C | main.py:practice |
| 2D | main.py:practice |
| 2E | main.py:practice |
| 2F | main.py:practice |
| 2G | main.py:practice |
| 3A | main.py:practice |
| 3B | main.py:practice |
| 3C | main.py:practice |
| 3D | main.py:practice |
| 4A | main.py:practice |
| 4B | main.py:practice |
| 4C | main.py:practice |
| 4D | main.py:practice |
| 5A | opcionales.py:practice |
| 5B | opcionales.py:practice |
| 5C | opcionales.py:practice |
| 5D | opcionales.py:practice |

## `maker.py`

```python
"""Tu regla A–S: la base y el consumidor están proporcionados."""
import math
from base_maker import StudentMarketMaker

class StudentAvellanedaStoikov(StudentMarketMaker):
    def __init__(self, gamma=0.1, sigma=0.5, kappa=1.5, size=0.1):
        if not all(math.isfinite(x) for x in (gamma, sigma, kappa)) or gamma <= 0 or sigma < 0 or kappa <= 0:
            raise ValueError('gamma/kappa positivos; sigma no negativa')
        super().__init__(size=size)
        self.gamma, self.sigma, self.kappa = gamma, sigma, kappa

    def inventory_adjustment(self, tau):
        # Ejercicio 1A: completa StudentAvellanedaStoikov.inventory_adjustment(tau): devuelve self.inventory por self.gamma por self.sigma al cuadrado por tau; calcula el ajuste en unidades de precio.
        return self.inventory * self.gamma * self.sigma ** 2 * tau

    def reservation_price(self, mid, tau):
        # Ejercicio 1B: completa reservation_price(mid, tau): resta al mid el resultado de self.inventory_adjustment(tau); reutiliza el método anterior para construir el centro.
        return mid - self.inventory_adjustment(tau)

    def spread(self, tau):
        # Ejercicio 1C: completa spread(tau): suma risk = gamma por sigma al cuadrado por tau y flow = (2/gamma) por math.log1p(gamma/kappa); devuelve ancho total, que quotes dividirá entre dos.
        risk = self.gamma * self.sigma ** 2 * tau
        flow = 2 / self.gamma * math.log1p(self.gamma / self.kappa)
        return risk + flow
```

## `main.py`

```python
"""L14: construye centro/ancho, luego contrasta tus quotes."""
import math
from maker import StudentAvellanedaStoikov
from base_maker import StudentMarketMaker
from research_support import simulate

STEPS = ('1A', '1B', '1C', '2A', '2B', '2C', '2D', '2E', '2F', '2G', '3A', '3B', '3C', '3D', '4A', '4B', '4C', '4D')

def practice(through=None):
    maker = StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5)
    maker.inventory = 1
    # Observación 1A
    print(f'ajuste: {maker.inventory_adjustment(1):.6f}')
    if through == '1A': return locals()

    # Observación 1B
    print(f'centro: {maker.reservation_price(100, 1):.6f}')
    if through == '1B': return locals()

    # Observación 1C
    print(f'ancho total: {maker.spread(1):.6f}')
    bid, ask = maker.quotes(100, 1)
    print(f'quotes: {bid:.6f} / {ask:.6f}; centro {(bid+ask)/2:.6f}')
    if through == '1C': return locals()

    # Ejercicio 2A: fija maker.inventory=-1 y guarda short_quotes; después fija inventory=0 y guarda flat_quotes, siempre con mid=100 y tau=1; predice centro y ancho antes de ejecutar.
    maker.inventory = -1
    short_quotes = maker.quotes(100, 1)
    maker.inventory = 0
    flat_quotes = maker.quotes(100, 1)
    # Observación 2A
    print(f'q=-1: centro {sum(short_quotes)/2:.6f}; ancho {short_quotes[1]-short_quotes[0]:.6f}')
    print(f'q=0: centro {sum(flat_quotes)/2:.6f}; ancho {flat_quotes[1]-flat_quotes[0]:.6f}')
    if through == '2A': return locals()

    # Ejercicio 2B: fija maker.inventory=1 y guarda time_quotes como pares (tau, quotes) para tau 1, 0.5 y 0; explica qué cambia y qué sigue abierto al final.
    maker.inventory = 1
    time_quotes = [(tau, maker.quotes(100, tau)) for tau in (1, 0.5, 0)]
    # Observación 2B
    for tau, (b, a) in time_quotes:
        print(f'tau={tau}: centro {(b+a)/2:.6f}; ancho {a-b:.6f}; q {maker.inventory}')
    if through == '2B': return locals()

    # Ejercicio 2C: crea sign_maker con gamma=0.5, sigma=0.5 y kappa=1.5; guarda centers para inventarios -2, 0 y 2, con mid=100 y tau=1, sin simular.
    sign_maker = StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5)
    centers = []
    for q in (-2, 0, 2):
        sign_maker.inventory = q
        centers.append(sign_maker.reservation_price(100, 1))
    # Observación 2C
    print('centros por signo:', centers)
    if through == '2C': return locals()

    # Ejercicio 2D: crea un maker por cada sigma de (0.5, 1.0), fija q=1 y guarda sus inventory_adjustment(1) en sigma_adjustments; predice el factor antes de consultar.
    sigma_adjustments = []
    for sigma in (0.5, 1.0):
        check_maker = StudentAvellanedaStoikov(gamma=0.5, sigma=sigma, kappa=1.5)
        check_maker.inventory = 1
        sigma_adjustments.append(check_maker.inventory_adjustment(1))
    # Observación 2D
    print('ajustes sigma 0.5/1.0:', sigma_adjustments, '; factor:', sigma_adjustments[1]/sigma_adjustments[0])
    if through == '2D': return locals()

    # Ejercicio 2E: guarda liquidity_width consultando maker.spread(0) y risk_width como spread(1) menos liquidity_width; separa los dos términos del ancho sin duplicar la fórmula.
    liquidity_width = maker.spread(0)
    risk_width = maker.spread(1) - liquidity_width
    # Observación 2E
    print(f'ancho riesgo {risk_width:.6f}; liquidez {liquidity_width:.6f}')
    if through == '2E': return locals()

    # Ejercicio 2F: consulta las quotes de maker para mid=100 y tau=1 y guarda observed_width como ask menos bid; contrasta el ancho observado con spread(1).
    width_bid, width_ask = maker.quotes(100, 1)
    observed_width = width_ask - width_bid
    # Observación 2F
    print(f'ancho en quotes: {observed_width:.6f}; método: {maker.spread(1):.6f}')
    if through == '2F': return locals()

    # Ejercicio 2G: crea variant con gamma=0.5, sigma=2 y kappa=0.5, fija q=2 y guarda variant_quotes con mid=100 y tau=0.5; anuncia que este es otro caso.
    variant = StudentAvellanedaStoikov(gamma=0.5, sigma=2, kappa=0.5)
    variant.inventory = 2
    variant_quotes = variant.quotes(100, 0.5)
    # Observación 2G
    print(f'variante: centro {sum(variant_quotes)/2:.6f}; ancho {variant_quotes[1]-variant_quotes[0]:.6f}')
    if through == '2G': return locals()

    # Ejercicio 3A: crea simulation_maker con gamma=0.5, sigma=0.5 y kappa=1.5; guarda records = simulate(simulation_maker, seed=2026, steps=500, sigma=simulation_maker.sigma, kappa=simulation_maker.kappa).
    simulation_maker = StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5)
    records = simulate(simulation_maker, seed=2026, steps=500, sigma=simulation_maker.sigma, kappa=simulation_maker.kappa)
    # Observación 3A
    print(f'cierre propio: pnl {records.final_pnl:.4f}; máximo q {records.max_inventory:.3f}; pasos {len(records)}')
    if through == '3A': return locals()

    # Ejercicio 3B: guarda control_records simulando StudentMarketMaker() con seed=2026, steps=500, sigma=0.5 y kappa=1.5; conserva el control con skew=2 y half_spread=0.6.
    control_records = simulate(StudentMarketMaker(), seed=2026, steps=500, sigma=0.5, kappa=1.5)
    # Observación 3B
    print(f'control L13: pnl {control_records.final_pnl:.4f}; máximo q {control_records.max_inventory:.3f}')
    if through == '3B': return locals()

    # Ejercicio 3C: completa compare_rules(seeds): por cada semilla crea control y StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5), simula cada uno con los mismos parámetros y devuelve filas (seed, nombre, PnL, máximo inventario).
    def compare_rules(seeds):
        rows = []
        for seed in seeds:
            makers = (StudentMarketMaker(), StudentAvellanedaStoikov(gamma=0.5, sigma=0.5, kappa=1.5))
            for current in makers:
                result = simulate(current, seed=seed, steps=500, sigma=0.5, kappa=1.5)
                rows.append((seed, type(current).__name__, result.final_pnl, result.max_inventory))
        return rows
    # Observación 3C
    comparison = compare_rules((2026, 7, 314))
    for seed, name, pnl, maximum in comparison:
        print(f'comparación {seed} {name}: pnl {pnl:.4f}; máximo {maximum:.3f}')
    if through == '3C': return locals()

    # Ejercicio 3D: extrae as_pnls de todas las filas StudentAvellanedaStoikov de comparison y guarda pnl_range=(mínimo, máximo); interpreta dispersión sin seleccionar solo la mejor semilla.
    as_pnls = [pnl for _, name, pnl, _ in comparison if name == 'StudentAvellanedaStoikov']
    pnl_range = (min(as_pnls), max(as_pnls))
    # Observación 3D
    print(f'rango A-S: {pnl_range[0]:.4f} / {pnl_range[1]:.4f}; semillas {len(as_pnls)}')
    if through == '3D': return locals()

    # Ejercicio 4A: guarda gamma_shifts con los ajustes de makers gamma=0.1 y 1.0, sigma=0.5, kappa=1.5 y q=1 a tau=1; separa este cálculo fijo de una simulación.
    gamma_shifts = []
    for gamma in (0.1, 1.0):
        current = StudentAvellanedaStoikov(gamma=gamma, sigma=0.5, kappa=1.5)
        current.inventory = 1
        gamma_shifts.append(current.inventory_adjustment(1))
    # Observación 4A
    print('ajustes gamma:', gamma_shifts)
    if through == '4A': return locals()

    # Ejercicio 4B: guarda gamma_rows con (gamma, PnL, máximo inventario) para gamma=0.1 y 1.0, seed=3 y steps=50; usa sigma=0.5 y kappa=1.5 en regla y mercado y describe ambas filas sin imponer monotonía.
    gamma_rows = []
    for gamma in (0.1, 1.0):
        current = StudentAvellanedaStoikov(gamma=gamma, sigma=0.5, kappa=1.5)
        result = simulate(current, seed=3, steps=50, sigma=current.sigma, kappa=current.kappa)
        gamma_rows.append((gamma, result.final_pnl, result.max_inventory))
    # Observación 4B
    for gamma, pnl, maximum in gamma_rows:
        print(f'gamma {gamma}: pnl {pnl:.4f}; máximo {maximum:.3f}')
    if through == '4B': return locals()

    # Ejercicio 4C: crea control=StudentMarketMaker(), fija q=0.3 y guarda control_center y control_width consultando reservation_price(100,1) y spread(1).
    control = StudentMarketMaker()
    control.inventory = 0.3
    control_center = control.reservation_price(100, 1)
    control_width = control.spread(1)
    # Observación 4C
    print(f'control: centro {control_center:.2f}; ancho {control_width:.2f}')
    if through == '4C': return locals()

    # Ejercicio 4D: calcula ideal_round_trip como el ancho ask-bid de 1C por tamaño 0.1; explica qué fills confirmados exigiría cobrarlo y qué inventario puede quedar abierto.
    ideal_round_trip = (ask - bid) * 0.1
    # Observación 4D
    print(f'vuelta ideal: {ideal_round_trip:.6f}')
    if through == '4D': return locals()

    return locals()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## `opcionales.py`

```python
"""OPTIONAL: variantes separadas de la ruta requerida."""
from maker import StudentAvellanedaStoikov

STEPS = ("5A", "5B", "5C", "5D")

def practice(through=None):
    # Ejercicio 5A: OPTIONAL: crea probe con gamma=0.5, sigma=0.5 y kappa=1.5, fija q=-1 y guarda centers a tau=1 y tau=0.
    probe = StudentAvellanedaStoikov(gamma=0.5,sigma=0.5,kappa=1.5)
    probe.inventory = -1
    centers = (probe.reservation_price(100,1), probe.reservation_price(100,0))
    # Observación 5A
    print('centros:', centers, '; q:', probe.inventory, '; ancho final:', round(probe.spread(0),6))
    if through == '5A': return locals()

    # Ejercicio 5B: OPTIONAL: crea double_sigma con sigma=1.0 y q=-1; guarda quadrupled_shift como razón de los ajustes absolutos a tau=1 frente a probe.
    double_sigma = StudentAvellanedaStoikov(gamma=0.5,sigma=1.0,kappa=1.5)
    double_sigma.inventory = -1
    quadrupled_shift = abs(double_sigma.inventory_adjustment(1)) / abs(probe.inventory_adjustment(1))
    # Observación 5B
    print('factor por duplicar sigma:', quadrupled_shift)
    if through == '5B': return locals()

    # Ejercicio 5C: OPTIONAL: consulta las quotes de double_sigma para mid=100 y tau=1 y guarda quoted_width=ask-bid; contrasta con spread(1).
    b, a = double_sigma.quotes(100,1)
    quoted_width = a-b
    # Observación 5C
    print(f'ancho de quotes {quoted_width:.6f}; método {double_sigma.spread(1):.6f}')
    if through == '5C': return locals()

    # Ejercicio 5D: OPTIONAL: completa equiv_certeza(media,gamma,var) con media menos gamma por var dividido entre dos; calcula barato y caro para media=100, var=30 y gamma 0.1 y 2.0.
    def equiv_certeza(media, gamma, var):
        return media - gamma * var / 2
    barato = equiv_certeza(100, 0.1, 30)
    caro = equiv_certeza(100, 2.0, 30)
    # Observación 5D
    print('equivalente gamma 0.1:', barato, 'gamma 2:', caro)
    if through == '5D': return locals()

    return locals()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", choices=STEPS)
    args = parser.parse_args()
    try:
        practice(args.through)
    except NotImplementedError as pending:
        print(pending)
```

## `base_maker.py`

```python
"""Dos quotes y una clase de market making: precios, no fills."""
from research_support import MakerBase


def fixed_quotes(center, half_spread):
    # Ejercicio 1A: completa fixed_quotes(center, half_spread): devuelve bid como center menos half_spread y ask como center más half_spread; conserva un ancho total de dos medios spreads.
    return center - half_spread, center + half_spread


class StudentMarketMaker(MakerBase):
    def reservation_price(self, mid, tau):
        # Ejercicio 2A: completa StudentMarketMaker.reservation_price(mid, tau): resta self.skew por self.inventory al mid; conserva tau en la firma aunque el skew fijo no lo utilice.
        return mid - self.skew * self.inventory

    # Proporcionado: conserva ancho y usa el centro del mismo objeto.
    def spread(self, tau):
        return 2 * self.half_spread

    def quotes(self, mid, tau):
        center = self.reservation_price(mid, tau)
        return fixed_quotes(center, self.spread(tau) / 2)
```

## Respuestas y decisiones por apartado

**1A** · Ajuste 0.125000 con q=1, gamma=.5, sigma=.5 y tau=1. Sigma es desviación por horizonte; sigma² es varianza. El ajuste positivo se restará al mid.

**1B** · Centro 99.875000. La llamada a tu método evita duplicar la regla. Un inventario negativo invierte el signo.

**1C** · Riesgo .125 + liquidez 1.150728 = ancho 1.275728; bid 99.237136, ask 100.512864. log1p(x) es ln(1+x), inversa de exp; quotes heredado coloca medio ancho a cada lado del centro.

**2A** · Con q=-1 el centro es 100.125; con q=0, 100. Ambos anchos son 1.275728. Q afecta al centro, no figura en spread.

**2B** · Centros 99.875, 99.9375, 100; anchos 1.275728, 1.213228, 1.150728. A tau=0 queda el término de liquidez y q sigue en 1: calcular quotes no liquida. simulate cotiza tau=1-step/steps y no llama quotes en tau=0.

**2C** · Centros [100.25, 100, 99.75]. Largo baja el centro; corto lo sube. Esto es una preferencia de flujo, no garantía de ejecución.

**2D** · Ajustes [.125, .5], factor 4. Duplicar sigma cuadruplica su varianza; esta comprobación detecta olvidar el cuadrado. Transferencia: al cambiar también q a -1, cambia el signo del ajuste, no su magnitud; el ancho depende de sigma, no de q.

**2E** · Riesgo .125 y liquidez 1.150728. Tau apaga el primero, no el segundo. No son dos medios spreads ni probabilidades.

**2F** · Observed_width 1.275728 coincide con spread(1), con tolerancia numérica. El promedio de bid/ask coincide con reservation_price.

**2G** · Centro 98; ancho 4.772589, bid 95.613706 y ask 100.386294. Se han cambiado sigma y kappa a la vez; no atribuyas este cambio a un solo parámetro.

**3A** · El simulador consume tu clase y reinicia inventory. Conserva 500 registros, final_pnl y max_inventory después de cada fill. PnL marcado incluye inventario abierto; no se usa el replay ni PositionTracker.

**3B** · Control: PnL 2.2878 y máximo q .4. Coincide con la regla de centro y ancho fijo proporcionada. No cambies control y regla simultáneamente.

**3C** · Seis filas, tres semillas por cada regla, instancias nuevas y entorno común. Una semilla compartida mantiene las mismas tiradas de este simulador, pero reglas distintas pueden aceptar fills distintos.

**3D** · El rango conserva los extremos de las tres filas A–S; acompáñalo de las filas individuales y los máximos de inventario. No demuestra robustez ni rentabilidad real.

**4A** · Ajustes [.025, .25]: multiplicar gamma por 10 multiplica este ajuste por 10 con el resto fijo. El término de liquidez también cambia; no presupongas monotonía del ancho total.

**4B** · Conserva los dos PnLs y máximos observados. Cambiar gamma modifica las quotes y qué fills se aceptan; no garantiza una ordenación del riesgo o del beneficio entre trayectorias.

**4C** · Control: centro 99.40 y ancho 1.20. La hija A–S reemplaza el centro y el ancho, manteniendo quotes(mid,tau) y el consumidor.

**4D** · Vuelta ideal .127572829: exige compra .1 al bid y venta .1 al ask originales, ambos confirmados, sin costes. No equivale al PnL de una trayectoria ni a un cobro por publicar quotes.

**5A** · Centros 100.125 y 100; q permanece -1 al consultar tau=0. El reloj no rellena órdenes.

**5B** · Factor 4 por sigma². La razón de magnitudes elimina el signo del inventario.

**5C** · Ancho 1.650728: riesgo .5 más liquidez 1.150728; medio ancho por lado.

**5D** · Barato 98.5, caro 70. Para riqueza normal y utilidad CARA, el equivalente cierto penaliza varianza por gamma/2. Es otro cálculo proporcionado para interpretar riesgo, no el PnL de simulate.
