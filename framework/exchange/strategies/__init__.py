"""Estrategias enchufables sobre el framework. Todas heredan de `Strategy`."""

from exchange.strategies.vwap import VWAPStrategy
from exchange.strategies.market_maker import MarketMaker, AvellanedaStoikov

__all__ = ["VWAPStrategy", "MarketMaker", "AvellanedaStoikov"]
