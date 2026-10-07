"""strategy.py — la interfaz enchufable. El corazón del framework.

Construido en L10. Una estrategia no sabe nada del motor: solo reacciona al libro
y a sus fills devolviendo acciones. Cualquier subclase de `Strategy` se puede
enchufar al mismo `Backtest` sin tocar nada más. Eso es lo que hace que VWAP, un
market maker, o la estrategia que escriba el alumno, sean intercambiables.

Contrato:
    on_start(ctx)              -> se llama una vez al empezar
    on_book_update(book)       -> se llama en cada snapshot; devuelve acciones
    on_fill(fill)              -> se llama cuando una orden tuya se cruza
    on_end(ctx)                -> se llama una vez al terminar
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from exchange.book import OrderBook
from exchange.orders import Order
from exchange.trades import Fill


@dataclass
class NewOrder:
    """Acción: enviar una orden al mercado."""
    order: Order


@dataclass
class Cancel:
    """Acción: cancelar una orden propia por id."""
    order_id: int


Action = NewOrder | Cancel


class Strategy(ABC):
    def on_start(self, ctx: "Context") -> None:  # noqa: F821
        """Gancho opcional de inicialización."""

    @abstractmethod
    def on_book_update(self, book: OrderBook) -> list[Action]:
        """Reacciona al estado del libro. Devuelve 0..N acciones."""
        raise NotImplementedError

    def on_fill(self, fill: Fill) -> None:
        """Gancho opcional: una orden tuya se cruzó."""

    def on_end(self, ctx: "Context") -> None:  # noqa: F821
        """Gancho opcional de cierre."""
