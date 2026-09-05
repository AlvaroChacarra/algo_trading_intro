"""Comprobaciones públicas de integración; importa solo TU exchange."""
from exchange import snapshot
assert snapshot.spread == 2
assert snapshot.mid == 100
