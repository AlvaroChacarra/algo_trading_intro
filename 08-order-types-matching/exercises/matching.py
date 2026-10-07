"""Tu matching engine: funciones pequeñas y una clase que las conecta."""
from base_book import Level
from exchange.orders import Order, OrderType, Side
from exchange.trades import Fill as ExecutionFill
from scenarios import fresh_book, book_state, fill_signature

# Proporcionado: solo compare_engine usa este oráculo independiente.
from exchange.book import OrderBook as ReferenceBook, Level as ReferenceLevel
from exchange.matching import MatchingEngine as ReferenceEngine

EPS = 1e-12


def opposite_levels(order, book):
    # TODO · Ejercicio 1A: devuelve los asks para BUY y los bids para SELL, conservando la lista del libro.
    raise NotImplementedError('Completa 1A en matching.py.')


def take_from_level(remaining, level):
    # TODO · Ejercicio 1B: devuelve take = min(remaining, level.size) y el nuevo pendiente, sin modificar el nivel.
    raise NotImplementedError('Completa 1B en matching.py.')


def crosses(order, level_price):
    # TODO · Ejercicio 1C: acepta cualquier precio en MARKET; en las demás políticas compara el límite según BUY o SELL.
    raise NotImplementedError('Completa 1C en matching.py.')


def plan_fills(order, levels):
    # TODO · Ejercicio 2A: construye pares (level, take) con crosses y take_from_level; devuelve plan y pendiente sin mutar.
    raise NotImplementedError('Completa 2A en matching.py.')


def commit_plan(order, book, plan, timestamp=None):
    # TODO · Ejercicio 2B: consume cada par del plan, crea ExecutionFill con timestamp y retira niveles agotados.
    raise NotImplementedError('Completa 2B en matching.py.')


def rest_limit(order, book, remaining):
    # TODO · Ejercicio 3D: añade el remanente LIMIT al lado propio, agrega cantidades al mismo precio y conserva el orden.
    raise NotImplementedError('Completa 3D en matching.py.')


def validate_plan(order, remaining):
    # TODO · Ejercicio 3F: acepta FOK solo si el pendiente es cero dentro de EPS; las demás políticas admiten parciales.
    raise NotImplementedError('Completa 3F en matching.py.')


class PlannedEngine:
    def process(self, order, book, timestamp=None):
        # TODO · Ejercicio 4A: conecta selección, plan, validación, commit y remanente LIMIT en process; transmite timestamp.
        raise NotImplementedError('Completa 4A en matching.py.')


def effective_price(fills):
    # TODO · Ejercicio 5A: devuelve el precio ponderado por tamaño de los fills, o None cuando no hay ejecución.
    raise NotImplementedError('Completa 5A en matching.py.')


def compare_engine(engine_class, side, size, kind, price=None):
    # TODO · Ejercicio 6B: compara los fills y ambos lados finales de tu motor con la referencia sobre libros nuevos.
    raise NotImplementedError('Completa 6B en matching.py.')
