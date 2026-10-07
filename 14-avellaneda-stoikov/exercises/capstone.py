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
        # Pendiente: esta plantilla conserva exactamente el control.
        return bid, ask

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
    # Mi hipótesis y predicción: …
    # Caso de fallo: …
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
    # Mi explicación: …
    if through == '6A': return locals()

    return locals()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--through', choices=('1A','2A','3A','4A','5A','6A'))
    main(parser.parse_args().through)
