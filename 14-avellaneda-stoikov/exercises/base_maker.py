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
