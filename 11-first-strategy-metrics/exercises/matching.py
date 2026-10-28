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
    # Ejercicio 1A: devuelve los asks para BUY y los bids para SELL, conservando la lista del libro.
    return book.asks if order.side is Side.BUY else book.bids


def take_from_level(remaining, level):
    # Ejercicio 1B: devuelve take = min(remaining, level.size) y el nuevo pendiente, sin modificar el nivel.
    take = min(remaining, level.size)
    return take, max(0.0, remaining - take)


def crosses(order, level_price):
    # Ejercicio 1C: acepta cualquier precio en MARKET; en las demás políticas compara el límite según BUY o SELL.
    if order.order_type is OrderType.MARKET:
        return True
    if order.side is Side.BUY:
        return level_price <= order.price
    return level_price >= order.price


def plan_fills(order, levels):
    # Ejercicio 2A: construye pares (level, take) con crosses y take_from_level; devuelve plan y pendiente sin mutar.
    remaining = order.size
    plan = []
    for level in levels:
        if remaining <= EPS or not crosses(order, level.price):
            break
        take, remaining = take_from_level(remaining, level)
        if take > EPS:
            plan.append((level, take))
    return plan, max(0.0, remaining)


def commit_plan(order, book, plan, timestamp=None):
    # Ejercicio 2B: consume cada par del plan, crea ExecutionFill con timestamp y retira niveles agotados.
    fills = []
    for level, take in plan:
        level.size -= take
        fills.append(ExecutionFill(order.id, order.symbol, order.side,
                                   level.price, take, timestamp))
    book.bids[:] = [lv for lv in book.bids if lv.size > EPS]
    book.asks[:] = [lv for lv in book.asks if lv.size > EPS]
    return fills


def rest_limit(order, book, remaining):
    # Ejercicio 3D: añade el remanente LIMIT al lado propio, agrega cantidades al mismo precio y conserva el orden.
    if remaining <= EPS:
        return
    own = book.bids if order.side is Side.BUY else book.asks
    for level in own:
        if level.price == order.price:
            level.size += remaining
            break
    else:
        own.append(Level(order.price, remaining))
    own.sort(key=lambda lv: -lv.price if order.side is Side.BUY else lv.price)


def validate_plan(order, remaining):
    # Ejercicio 3F: acepta FOK solo si el pendiente es cero dentro de EPS; las demás políticas admiten parciales.
    return order.order_type is not OrderType.FOK or remaining <= EPS


class PlannedEngine:
    def process(self, order, book, timestamp=None):
        # Ejercicio 4A: conecta selección, plan, validación, commit y remanente LIMIT en process; transmite timestamp.
        if order.symbol != book.symbol:
            raise ValueError("orden y libro deben tener el mismo símbolo")
        levels = opposite_levels(order, book)
        plan, remaining = plan_fills(order, levels)
        if not validate_plan(order, remaining):
            return []
        fills = commit_plan(order, book, plan, timestamp)
        if order.order_type is OrderType.LIMIT and remaining > EPS:
            rest_limit(order, book, remaining)
        return fills


def effective_price(fills):
    # Ejercicio 5A: devuelve el precio ponderado por tamaño de los fills, o None cuando no hay ejecución.
    quantity = sum(fill.size for fill in fills)
    if quantity == 0:
        return None
    return sum(fill.price * fill.size for fill in fills) / quantity


def compare_engine(engine_class, side, size, kind, price=None):
    # Ejercicio 6B: compara los fills y ambos lados finales de tu motor con la referencia sobre libros nuevos.
    student_book = fresh_book()
    reference_book = ReferenceBook('BTC',[ReferenceLevel(99,1)],
                                    [ReferenceLevel(101,.4),ReferenceLevel(102,1.6)])
    first = Order('BTC',side,size,price=price,order_type=kind)
    second = Order('BTC',side,size,price=price,order_type=kind)
    student_fills = engine_class().process(first,student_book)
    reference_fills = ReferenceEngine().process(second,reference_book)
    return (fill_signature(student_fills)==fill_signature(reference_fills)
            and book_state(student_book)==book_state(reference_book))
