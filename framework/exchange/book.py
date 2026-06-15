"""book.py — el libro de órdenes: el estado del mercado.

Estructura construida en L4 (OOP II): un objeto que *contiene* niveles de
precio. Es el primer sitio donde el alumno ve composición — el libro está hecho
de otras piezas.

Las métricas de lectura de mercado (spread, mid, imbalance, depth, microprice)
se añaden en L5.
"""

from __future__ import annotations

from dataclasses import dataclass

from exchange.orders import Side


@dataclass
class Level:
    price: float
    size: float


class OrderBook:
    """Libro de dos lados.

    bids: ordenados de mayor a menor precio (el mejor bid es el primero).
    asks: ordenados de menor a mayor precio (el mejor ask es el primero).
    """

    def __init__(self, symbol: str, bids: list[Level], asks: list[Level]) -> None:
        self.symbol = symbol
        self.bids = sorted(bids, key=lambda lv: -lv.price)
        self.asks = sorted(asks, key=lambda lv: lv.price)

    # ---- construcción ------------------------------------------------------

    @classmethod
    def from_snapshot(cls, symbol: str, row: dict, depth: int = 10) -> "OrderBook":
        """Construye el libro desde una fila de snapshot (formato CSV del curso)."""
        bids, asks = [], []
        for i in range(1, depth + 1):
            bp, bs = row.get(f"bid_price_{i}"), row.get(f"bid_size_{i}")
            ap, as_ = row.get(f"ask_price_{i}"), row.get(f"ask_size_{i}")
            if bp is not None and bs is not None and float(bs) > 0:
                bids.append(Level(float(bp), float(bs)))
            if ap is not None and as_ is not None and float(as_) > 0:
                asks.append(Level(float(ap), float(as_)))
        return cls(symbol, bids, asks)

    def copy(self) -> "OrderBook":
        return OrderBook(
            self.symbol,
            [Level(lv.price, lv.size) for lv in self.bids],
            [Level(lv.price, lv.size) for lv in self.asks],
        )

    # ---- lectura de mercado (L5) ------------------------------------------

    @property
    def best_bid(self) -> float | None:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> float | None:
        return self.asks[0].price if self.asks else None

    @property
    def spread(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid

    @property
    def mid(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / 2

    @property
    def microprice(self) -> float | None:
        """Mid ponderado por el tamaño del lado contrario.

        Más peso al lado con menos tamaño porque es el que probablemente se
        mueva. Es un predictor de corto plazo mejor que el mid simple.
        """
        if not self.bids or not self.asks:
            return None
        bs, as_ = self.bids[0].size, self.asks[0].size
        return (self.best_bid * as_ + self.best_ask * bs) / (bs + as_)

    def imbalance(self, levels: int = 1) -> float | None:
        """Presión compradora vs vendedora en [-1, 1].

        +1 = solo bids, -1 = solo asks, 0 = equilibrio.
        """
        bid_vol = self.depth(Side.BUY, levels)
        ask_vol = self.depth(Side.SELL, levels)
        total = bid_vol + ask_vol
        if total == 0:
            return None
        return (bid_vol - ask_vol) / total

    def depth(self, side: Side, levels: int = 10) -> float:
        """Tamaño acumulado en los primeros `levels` niveles de un lado."""
        side = Side(side)
        book_side = self.bids if side is Side.BUY else self.asks
        return sum(lv.size for lv in book_side[:levels])

    # ---- mutación (L4 add/cancel; usado por el matching en L6) -------------

    def add_limit(self, side: Side, price: float, size: float) -> None:
        """Inserta liquidez en un lado manteniendo el orden."""
        side = Side(side)
        book_side = self.bids if side is Side.BUY else self.asks
        for lv in book_side:
            if lv.price == price:
                lv.size += size
                return
        book_side.append(Level(price, size))
        book_side.sort(key=lambda lv: -lv.price if side is Side.BUY else lv.price)

    def reduce(self, side: Side, price: float, size: float) -> None:
        """Consume `size` de liquidez en un nivel (lo usa el matching)."""
        side = Side(side)
        book_side = self.bids if side is Side.BUY else self.asks
        for lv in book_side:
            if lv.price == price:
                lv.size -= size
                break
        book_side[:] = [lv for lv in book_side if lv.size > 1e-12]

    def __repr__(self) -> str:
        bb = f"{self.best_bid:g}" if self.best_bid is not None else "-"
        ba = f"{self.best_ask:g}" if self.best_ask is not None else "-"
        return f"OrderBook({self.symbol} {bb} / {ba}, spread={self.spread})"
