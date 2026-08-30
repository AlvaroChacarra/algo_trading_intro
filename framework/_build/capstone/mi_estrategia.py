"""mi_estrategia.py — TU market maker para el capstone.

Este es el único archivo que editas. La plantilla es deliberadamente
incompleta: implementa `reservation_price` antes de obtener feedback puntuado.
Después puedes extenderla o partir de `AvellanedaStoikov`.

Cuando la tengas, corrígete con:

    python capstone_check.py

Ideas para empezar (todas legales, todas del curso):
  · ajustar `half_spread`: más ancho = más margen por vuelta, menos fills.
  · ajustar `inventory_skew`: más skew = vuelves a plano antes (menos riesgo).
  · partir de AvellanedaStoikov y ajustar `gamma` o tu lógica de inventario.
  · sobrescribir `quotes()` o `reservation_price()` con tu propia lógica.
"""

from __future__ import annotations

from exchange.strategies import MarketMaker  # , AvellanedaStoikov


class MiEstrategia(MarketMaker):
    """Starter no evaluable hasta completar la decisión de inventario."""

    def __init__(self, symbol: str = "BTC") -> None:
        super().__init__(
            symbol,
            quote_size=0.01,      # tamaño de cada cotización
            half_spread=1.0,
            inventory_skew=2.0,
        )

    def reservation_price(self, mid: float) -> float:
        """Decide el centro de tus cotizaciones usando `mid` e inventario.

        Sustituye este TODO por tu lógica. Mientras siga sin implementar, el
        corrector no emite puntuación ni código de resultado.
        """
        raise NotImplementedError(
            "implementa reservation_price(mid) antes de evaluar el capstone"
        )


if __name__ == "__main__":
    # atajo: `python mi_estrategia.py` corre el corrector
    import capstone_check
    capstone_check.main()
