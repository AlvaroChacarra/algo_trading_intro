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
        # TODO · Ejercicio 1A: completa StudentAvellanedaStoikov.inventory_adjustment(tau): devuelve self.inventory por self.gamma por self.sigma al cuadrado por tau; calcula el ajuste en unidades de precio.
        raise NotImplementedError('Completa 1A en maker.py.')

    def reservation_price(self, mid, tau):
        # TODO · Ejercicio 1B: completa reservation_price(mid, tau): resta al mid el resultado de self.inventory_adjustment(tau); reutiliza el método anterior para construir el centro.
        raise NotImplementedError('Completa 1B en maker.py.')

    def spread(self, tau):
        # TODO · Ejercicio 1C: completa spread(tau): suma risk = gamma por sigma al cuadrado por tau y flow = (2/gamma) por math.log1p(gamma/kappa); devuelve ancho total, que quotes dividirá entre dos.
        raise NotImplementedError('Completa 1C en maker.py.')
