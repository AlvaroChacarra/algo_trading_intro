"""exchange — motor de microestructura y framework de estrategias.

Implementación de referencia del curso "Introducción al Algo Trading con Python".
Cada lección construye una pieza de este paquete. Este es el estado final (L14).

Capas:
    orders / trades   -> modelo de datos          (L4)
    book / portfolio  -> estado del mercado        (L5)
    matching          -> dinámica del mercado      (L8)
    market            -> loop de simulación        (L9)
    strategy/backtest -> interfaz y runner         (L10)
    strategies/vwap   -> ejecución                 (L12)
    strategies/*      -> market making             (L13-L14)
"""

from exchange.orders import Order, Side, OrderType
from exchange.trades import Fill
from exchange.book import OrderBook, Level
from exchange.portfolio import PositionTracker
from exchange.matching import MatchingEngine
from exchange.market import Market
from exchange.strategy import Strategy, NewOrder, Cancel, Action
from exchange.backtest import Backtest, BacktestResult

__all__ = [
    "Order", "Side", "OrderType",
    "Fill",
    "OrderBook", "Level",
    "PositionTracker",
    "MatchingEngine",
    "Market",
    "Strategy", "NewOrder", "Cancel", "Action",
    "Backtest", "BacktestResult",
]
