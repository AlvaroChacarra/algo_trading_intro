"""exchange — motor de microestructura y framework de estrategias.

Implementación de referencia del curso "Introducción al Algo Trading con Python".
Cada lección construye una pieza de este paquete. Este es el estado final (L14).

Capas:
    orders / trades   -> modelo de datos          (L3)
    book / portfolio  -> estado del mercado        (L4-L5)
    matching          -> dinámica del mercado      (L6)
    market            -> loop de simulación        (L7)
    strategy          -> interfaz enchufable       (L8)
    backtest          -> runner que lo cablea todo (L8-L9)
    strategies/*      -> VWAP y market making       (L10-L14)
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
