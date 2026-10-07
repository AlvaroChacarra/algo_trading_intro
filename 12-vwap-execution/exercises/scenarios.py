"""Datos proporcionados, sintéticos e independientes del trabajo del alumno.

raw/raw_u: volumen esperado RELATIVO conocido antes de operar.
Intervalos de igual duración, uno por foto hasta agotar el perfil.
partial_rows: precio USDT/BTC, tamaño visible BTC, tres fotos y solo dos envíos.
precios/volumenes: otra sesión ilustrativa observada al terminar; no decide órdenes.
Cada snapshot reemplaza el libro: no hay impacto persistente ni streaming.
"""
raw = [1,1,1,1,1]
total_size = 5.0
raw_u = [3,1,1,1,4]
partial_rows = [
    {'bid_price_1':99,'bid_size_1':2,'ask_price_1':101,'ask_size_1':.25},
    {'bid_price_1':101,'bid_size_1':2,'ask_price_1':103,'ask_size_1':.75},
    {'bid_price_1':103,'bid_size_1':2,'ask_price_1':105,'ask_size_1':5},
]
schedule_rows = [dict(bid_price_1=99,bid_size_1=2,ask_price_1=101,ask_size_1=2) for _ in range(5)]
precios = [100,101,102]
volumenes = [5,2,1]

"""Bancos de pruebas proporcionados: no ejecutan el matching."""
from book import SnapshotBook

sample_row = {'bid_price_1': '99', 'bid_size_1': '1',
              'ask_price_1': '101', 'ask_size_1': '0.4',
              'ask_price_2': '102', 'ask_size_2': '1.6'}


def fresh_book():
    """Otra instancia, con niveles nuevos: 99×1; 101×0.4 y 102×1.6."""
    return SnapshotBook.from_snapshot('BTC', sample_row, depth=2)


def book_state(book):
    """Firma legible de ambos lados; no modifica el libro."""
    return ([(level.price, round(level.size, 9)) for level in book.bids],
            [(level.price, round(level.size, 9)) for level in book.asks])


def fill_signature(fills):
    """Ignora IDs distintos al comparar órdenes equivalentes."""
    return [(fill.side.value, fill.price, round(fill.size, 9)) for fill in fills]
