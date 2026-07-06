"""mi_estrategia.py — TU market maker para el capstone.

Este es el único archivo que editas. Define una clase `MiEstrategia` que herede
de `MarketMaker` o de `AvellanedaStoikov` (todo lo que construiste en L13-L14) y
tunéala para maximizar la nota del baremo público (ver CAPSTONE.md).

Cuando la tengas, corrígete con:

    python capstone_check.py

Ideas para empezar (todas legales, todas del curso):
  · ajustar `half_spread`: más ancho = más margen por vuelta, menos fills.
  · ajustar `inventory_skew`: más skew = vuelves a plano antes (menos riesgo).
  · partir de AvellanedaStoikov y tocar `gamma` / `sigma` / `kappa`.
  · sobrescribir `quotes()` o `reservation_price()` con tu propia lógica.
"""

from __future__ import annotations

from exchange.strategies.market_maker import MarketMaker  # , AvellanedaStoikov


class MiEstrategia(MarketMaker):
    """Tu market maker. De partida, un MarketMaker naive razonable.

    Mejóralo: el baremo premia capturar spread SIN acumular inventario.
    """

    def __init__(self, symbol: str = "BTC") -> None:
        super().__init__(
            symbol,
            quote_size=0.01,      # tamaño de cada cotización
            half_spread=1.0,      # <-- TUNÉAME: distancia de bid/ask al centro
            inventory_skew=2.0,   # <-- TUNÉAME: cuánto corriges por inventario
        )

    # Opcional: sobrescribe el centro de tus cotizaciones.
    # def reservation_price(self, mid: float) -> float:
    #     return mid - self.inventory_skew * self._inventory


if __name__ == "__main__":
    # atajo: `python mi_estrategia.py` corre el corrector
    import capstone_check
    capstone_check.main()
