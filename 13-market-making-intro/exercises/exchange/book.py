"""book.py — el libro de órdenes: el estado del mercado.

Estructura construida en L5 (OOP II): un objeto que *contiene* niveles de
precio. Es el primer sitio donde el alumno ve composición — el libro está hecho
de otras piezas.

Spread, mid e imbalance llegan en L5. La construcción desde filas externas,
depth y microprice llegan en L7; la mutación se añade cuando L8 la necesita.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math

from exchange.orders import Side


# State effects are measured against the requested economic change, never
# against the (possibly enormous) level.  One part per trillion absorbs the
# ordinary subtraction noise exercised by the course while failing closed when
# a float cannot record the requested liquidity faithfully.  Fraction keeps
# the comparison itself exact, including at subnormal magnitudes.
_EFFECT_FIDELITY_DENOMINATOR = 10**12


def _has_faithful_effect(before: float, after: float, expected: float) -> bool:
    """Whether two stored states encode the expected economic change."""
    if (not math.isfinite(before) or not math.isfinite(after)
            or not math.isfinite(expected) or expected == 0.0):
        return False
    actual_exact = Fraction.from_float(after) - Fraction.from_float(before)
    expected_exact = Fraction.from_float(expected)
    if actual_exact == 0 or (actual_exact > 0) != (expected_exact > 0):
        return False
    error = abs(actual_exact - expected_exact)
    return error * _EFFECT_FIDELITY_DENOMINATOR <= abs(expected_exact)


@dataclass
class Level:
    price: float
    size: float

    def __post_init__(self) -> None:
        if isinstance(self.price, bool) or isinstance(self.size, bool):
            raise ValueError("level price and size must be numeric, not boolean")
        self.price = float(self.price)
        self.size = float(self.size)
        if not math.isfinite(self.price) or self.price <= 0:
            raise ValueError("level price must be finite and positive")
        if not math.isfinite(self.size) or self.size <= 0:
            raise ValueError("level size must be finite and positive")


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
        if isinstance(depth, bool) or not isinstance(depth, int) or depth <= 0:
            raise ValueError("depth must be a positive integer")
        bids, asks = [], []
        for i in range(1, depth + 1):
            bp, bs = row.get(f"bid_price_{i}"), row.get(f"bid_size_{i}")
            ap, as_ = row.get(f"ask_price_{i}"), row.get(f"ask_size_{i}")
            for price, size, destination in ((bp, bs, bids), (ap, as_, asks)):
                if price is None or size is None:
                    continue
                if isinstance(price, bool) or isinstance(size, bool):
                    raise ValueError("snapshot levels must be numeric, not boolean")
                numeric_size = float(size)
                if not math.isfinite(numeric_size) or numeric_size < 0:
                    raise ValueError("snapshot level size must be finite and non-negative")
                if numeric_size == 0:
                    continue
                destination.append(Level(float(price), numeric_size))
        return cls(symbol, bids, asks)

    # ---- lectura de mercado (L5 y L7) --------------------------------------

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
        # Interpolation cannot overflow for two positive finite endpoints and
        # still preserves the smallest subnormal when both endpoints equal it.
        return self.best_bid + (self.best_ask - self.best_bid) / 2

    @property
    def microprice(self) -> float | None:
        """Mid ponderado por el tamaño del lado contrario.

        Más peso al lado con menos tamaño porque es el que probablemente se
        mueva. Es un predictor de corto plazo mejor que el mid simple.
        """
        if not self.bids or not self.asks:
            return None
        bs, as_ = self.bids[0].size, self.asks[0].size
        scale = max(bs, as_)
        bid_weight = as_ / scale
        ask_weight = bs / scale
        ask_share = ask_weight / (bid_weight + ask_weight)
        # Interpolation stays between two finite positive prices and avoids
        # both product and size-sum overflow.
        return self.best_bid + (self.best_ask - self.best_bid) * ask_share

    def imbalance(self, levels: int = 1) -> float | None:
        """Presión compradora vs vendedora en [-1, 1].

        +1 = solo bids, -1 = solo asks, 0 = equilibrio.
        """
        bid_vol = self.depth(Side.BUY, levels)
        ask_vol = self.depth(Side.SELL, levels)
        scale = max(bid_vol, ask_vol)
        if scale == 0:
            return None
        scaled_bid, scaled_ask = bid_vol / scale, ask_vol / scale
        return (scaled_bid - scaled_ask) / (scaled_bid + scaled_ask)

    def depth(self, side: Side, levels: int = 10) -> float:
        """Tamaño acumulado en los primeros `levels` niveles de un lado."""
        if isinstance(levels, bool) or not isinstance(levels, int) or levels <= 0:
            raise ValueError("levels must be a positive integer")
        side = Side(side)
        book_side = self.bids if side is Side.BUY else self.asks
        return math.fsum(lv.size for lv in book_side[:levels])

    # ---- mutación (L8; usada por el matching) -------------------------------

    def add_limit(self, side: Side, price: float, size: float) -> None:
        """Inserta liquidez en un lado manteniendo el orden."""
        side = Side(side)
        if isinstance(price, bool) or isinstance(size, bool):
            raise ValueError("price and size must be numeric, not boolean")
        price, size = float(price), float(size)
        if not math.isfinite(price) or price <= 0:
            raise ValueError("price must be finite and positive")
        if not math.isfinite(size) or size <= 0:
            raise ValueError("size must be finite and positive")
        book_side = self.bids if side is Side.BUY else self.asks
        for lv in book_side:
            if lv.price == price:
                next_size = lv.size + size
                if not math.isfinite(next_size):
                    raise OverflowError("aggregated level size must stay finite")
                if not _has_faithful_effect(lv.size, next_size, size):
                    raise OverflowError("added size is not representable at this level")
                lv.size = next_size
                return
        book_side.append(Level(price, size))
        book_side.sort(key=lambda lv: -lv.price if side is Side.BUY else lv.price)

    def reduce(self, side: Side, price: float, size: float) -> None:
        """Consume `size` de liquidez en un nivel (lo usa el matching)."""
        side = Side(side)
        if isinstance(price, bool) or isinstance(size, bool):
            raise ValueError("price and size must be numeric, not boolean")
        price, size = float(price), float(size)
        if not math.isfinite(price) or price <= 0:
            raise ValueError("price must be finite and positive")
        if not math.isfinite(size) or size <= 0:
            raise ValueError("size must be finite and positive")
        book_side = self.bids if side is Side.BUY else self.asks
        for lv in book_side:
            if lv.price == price:
                # Never erase a positive residual merely because it is small.
                # Matching passes at most the visible size, while the public
                # method keeps its historical consume-to-zero behaviour.
                next_size = 0.0 if size >= lv.size else lv.size - size
                if size < lv.size:
                    if not _has_faithful_effect(lv.size, next_size, -size):
                        raise OverflowError(
                            "reduced size is not representable at this level"
                        )
                lv.size = next_size
                break
        book_side[:] = [lv for lv in book_side if lv.size > 0.0]

    def __repr__(self) -> str:
        bb = f"{self.best_bid:g}" if self.best_bid is not None else "-"
        ba = f"{self.best_ask:g}" if self.best_ask is not None else "-"
        return f"OrderBook({self.symbol} {bb} / {ba}, spread={self.spread})"
