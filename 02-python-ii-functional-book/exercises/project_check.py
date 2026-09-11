"""Comprobaciones públicas de integración; importa solo TU exchange."""
from exchange.functional import best_prices, make_order
assert best_prices([make_order('buy', 99, 1), make_order('buy', 100, 2), make_order('sell', 102, 3)]) == (100, 102)
assert best_prices([]) == (None, None)
