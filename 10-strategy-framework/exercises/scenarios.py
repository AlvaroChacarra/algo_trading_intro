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


# Control L10: USDT/BTC, BTC; timestamp 0/1 indica orden, no tiempo real.
rows = [
    {'timestamp':0,'bid_price_1':99,'bid_size_1':2,
     'ask_price_1':101,'ask_size_1':.4,'ask_price_2':102,'ask_size_2':.6},
    {'timestamp':1,'bid_price_1':101,'bid_size_1':2,
     'ask_price_1':103,'ask_size_1':1},
]
