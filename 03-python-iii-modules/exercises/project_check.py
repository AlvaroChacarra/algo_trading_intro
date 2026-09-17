"""Comprobaciones públicas de integración; importa solo TU exchange."""
from exchange.application import describe
assert describe([{'side':'buy','price':98}, {'side':'sell','price':102}]) == {'mid':100, 'spread':4}
assert describe([]) == {'mid':None, 'spread':None}
