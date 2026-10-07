# Capstone · consulta por apartados

Este es un ejemplo defendible, no la respuesta única. Intenta primero los seis hitos.
Copia tu intento antes de consultar. Los 90 minutos incluyen diseño, contraste y explicación;
no añadas otro proyecto ni una evaluación nueva.

## Respuestas por apartado

**1A · Hipótesis.** Si |q| supera .2, ampliar el ancho un 50% puede reducir llegadas. Conservo centro y tamaño. Puede fallar al retrasar una venta antes de una caída; no predigo mejor PnL o menor máximo inventario para cada trayectoria.

**2A · Control.** La base incluida se conserva intacta. Con mid=100 y q=0, +0.3 y −0.3, los centros son 100, 99.4 y 100.6; el ancho es 1.2. La semilla 2026 da PnL 2.2878 y máximo |q| 0.4 antes de cambiar la regla.

**3A · Activación.** Con q=0 y q=0.2 el ancho es 1.2; con q=±0.3 pasa a 1.8 y el centro sigue siendo 100−2q. El borde es estricto: |q| > 0.2; q=0.2001 sí activa la regla. La implementación está junto al comentario 3A del programa completo.

## Archivo completo · capstone.py

Guarda el programa completo en `capstone.py`, junto al simulador incluido. Ejecuta hasta el hito elegido con `python capstone.py --through 2A` y conserva tu copia personal. La base ya está incluida. Los comentarios identifican cada encargo junto a su respuesta.

<!-- El emisor amplía esta única clase canónica con la base y el experimento proporcionados. -->
```python
"""Capstone: programa de investigación. Lee CAPSTONE.md."""

from pathlib import Path
import sys

# Código proporcionado: el simulador está junto a los ejercicios.
exercise_dir = Path(__file__).resolve().parent
if not (exercise_dir / 'research_support.py').is_file():
    exercise_dir = exercise_dir.parent
if str(exercise_dir) not in sys.path:
    sys.path.insert(0, str(exercise_dir))


def fixed_quotes(center, half_spread):
    # Base proporcionada L13 · Ejercicio 1A: completa fixed_quotes(center, half_spread): devuelve bid como center menos half_spread y ask como center más half_spread; conserva un ancho total de dos medios spreads.
    return center - half_spread, center + half_spread


from research_support import MakerBase, simulate
class StudentMarketMaker(MakerBase):
    def reservation_price(self, mid, tau):
        # Base proporcionada L13 · Ejercicio 2A: completa StudentMarketMaker.reservation_price(mid, tau): resta self.skew por self.inventory al mid; conserva tau en la firma aunque el skew fijo no lo utilice.
        return mid - self.skew * self.inventory

    # Proporcionado: conserva ancho y usa el centro del mismo objeto.
    def spread(self, tau):
        return 2 * self.half_spread

    def quotes(self, mid, tau):
        center = self.reservation_price(mid, tau)
        return fixed_quotes(center, self.spread(tau) / 2)


class BaselineMaker(StudentMarketMaker):
    """Control intacto: cierre canónico de L13."""
    pass

class MiEstrategia(BaselineMaker):
    def quotes(self, mid, tau):
        bid, ask = super().quotes(mid, tau)
        # Ejercicio 3A: implementa una única modificación de quotes en MiEstrategia, después de escribir tu hipótesis; conserva bid <= ask y comprueba su activación con estados fijados.
        center = (bid + ask) / 2
        half = (ask - bid) / 2
        if abs(self.inventory) > 0.2:
            half *= 1.5
        return center - half, center + half

def compare(seeds):
    """Mismas semillas y parámetros para ambas reglas; muestra todas las filas."""
    rows = []
    for seed in seeds:
        for maker_class in (BaselineMaker, MiEstrategia):
            result = simulate(maker_class(), seed=seed, steps=500,
                              sigma=0.5, intensity=50.0, kappa=1.5)
            rows.append((seed, maker_class.__name__, result.final_pnl,
                         result.max_inventory))
    return rows


def show(rows):
    print('semilla estrategia pnl máximo_inventario')
    for seed, name, pnl, maximum in rows:
        print(f'{seed} {name} {pnl:.4f} {maximum:.3f}')
    for name in ('BaselineMaker', 'MiEstrategia'):
        pnls = [pnl for _, label, pnl, _ in rows if label == name]
        print(f'{name}: PnL medio={sum(pnls) / len(pnls):.4f}; '
              f'rango=[{min(pnls):.4f}, {max(pnls):.4f}]')


def main(through=None):
    # Ejercicio 1A: escribe una hipótesis sobre quotes/fills/inventario y un caso que podría refutarla antes de cambiar la regla.
    # Respuesta: ampliar ancho un 50% cuando |q| > .2 puede reducir llegadas, conservando centro y tamaño.
    # Respuesta: puede retrasar la venta antes de una caída; no prometo menor inventario ni mayor PnL.
    if through == '1A': return locals()

    # Ejercicio 2A: reproduce el control incluido sin modificarlo; comprueba centro/ancho a q=0, +0.3 y -0.3 y después la referencia seed=2026.
    baseline_probe = BaselineMaker()
    for inventory in (0, 0.3, -0.3):
        baseline_probe.inventory = inventory
        bid, ask = baseline_probe.quotes(100, 0.5)
        print(f'control q={inventory:.1f}; bid={bid:.3f}; ask={ask:.3f}; '
              f'centro={(bid + ask) / 2:.3f}; ancho={ask - bid:.3f}')
    baseline_records = simulate(BaselineMaker(), seed=2026, steps=500,
                                sigma=0.5, intensity=50.0, kappa=1.5)
    print(f'control seed=2026; pnl={baseline_records.final_pnl:.4f}; '
          f'máximo_inventario={baseline_records.max_inventory:.3f}')
    if through == '2A': return locals()

    # Observación 3A: crea una instancia nueva después de editar la clase y contrasta las quotes con tu hipótesis.
    probe = MiEstrategia()
    for inventory in (0, 0.3, -0.3):
        probe.inventory = inventory
        bid, ask = probe.quotes(100, 0.5)
        print(f'inventario={inventory:.1f}; centro={(bid + ask) / 2:.3f}; '
              f'ancho={ask - bid:.3f}')
    if through == '3A': return locals()

    # Ejercicio 4A: conserva todas las filas de desarrollo y anota los parámetros finales; compara PnL y exposición sin elegir la mejor semilla.
    development = compare((2026, 7, 314))
    show(development)
    if through == '4A': return locals()

    # Ejercicio 5A: congela la regla antes de ejecutar estas tres semillas y conserva resultados sin retocar parámetros.
    print('Contraste: regla congelada; no reajustar con estas semillas.')
    contrast = compare((2718, 1618, 5772))
    show(contrast)
    if through == '5A': return locals()

    # Ejercicio 6A: explica mecanismo, todas las filas, dispersión y límites; indica qué evidencia faltaría para un mercado real.
    # Respuesta: mayor distancia cambia p(fill); el contraste tiene un PnL peor en 1618.
    # Faltan escenarios, calibración y datos independientes, con costes, cola y latencia.
    # La media no sustituye las filas; no hay garantía de rentabilidad.
    if through == '6A': return locals()

    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--through', choices=('1A','2A','3A','4A','5A','6A'))
    main(parser.parse_args().through)
```

## Respuestas 4A–5A · Desarrollo y contraste

**4A · Desarrollo.** Conservo las seis filas de las semillas 2026, 7 y 314, con media y rango por regla. Anoto umbral 0.2 y factor 1.5 como parámetros finales, sin cambiar el mercado ni el control.

**5A · Contraste.** Congelo esos parámetros antes de ejecutar las semillas 2718, 1618 y 5772. Conservo las otras seis filas sin recalibrar: 1618 contradice una promesa de mayor PnL en todas las trayectorias.

## Resultado reproducible del ejemplo

```text
semilla estrategia pnl máximo_inventario
2026 BaselineMaker 2.2878 0.400
2026 MiEstrategia 2.4506 0.400
7 BaselineMaker 2.5186 0.300
7 MiEstrategia 2.6086 0.300
314 BaselineMaker 2.6918 0.300
314 MiEstrategia 2.9120 0.300
BaselineMaker: PnL medio=2.4994; rango=[2.2878, 2.6918]
MiEstrategia: PnL medio=2.6571; rango=[2.4506, 2.9120]
Contraste: regla congelada; no reajustar con estas semillas.
semilla estrategia pnl máximo_inventario
2718 BaselineMaker 2.7671 0.400
2718 MiEstrategia 2.8092 0.400
1618 BaselineMaker 1.7396 0.300
1618 MiEstrategia 1.7180 0.300
5772 BaselineMaker 1.7633 0.200
5772 MiEstrategia 1.7633 0.200
BaselineMaker: PnL medio=2.0900; rango=[1.7396, 2.7671]
MiEstrategia: PnL medio=2.0968; rango=[1.7180, 2.8092]
```

La variante obtiene menor PnL que la base en la semilla 1618. El máximo inventario coincide con el control en las seis semillas. Las demás filas también cuentan: no selecciones solo la favorable. Una regla que aleja ambas quotes puede dejar inventario abierto durante más tiempo; una caída persistente del mid después de comprar es un caso económico donde puede fallar. No se ha demostrado robustez frente a esos escenarios: este paseo aleatorio y seis semillas no modelan selección adversa, comisiones, colas ni latencia. El PnL mostrado es bruto. Antes de atribuir una mejora a la regla harían falta escenarios distintos, calibración y datos independientes.

## Respuesta 6A · Explicación y transferencia

**6A.** La ampliación cambia la distancia de cada quote, luego la probabilidad de fill y la exposición.
Con esta muestra no hay una mejora universal. Añadir costes por fill resta coste × número de fills;
no basta restar una comisión única al PnL. Una latencia o cola cambia la selección de ejecuciones,
no solo la contabilidad. Harían falta escenarios de tendencia y saltos, parámetros calibrados
y datos independientes antes de sacar conclusiones para mercado real.

**Transferencia:** en q=0.2 exacto la regla no se activa; en 0.2001 sí. Si el centro cambiara
al ampliar únicamente el ancho, habría un error de implementación. Esto verifica mecanismo,
no rentabilidad ni calibración.
