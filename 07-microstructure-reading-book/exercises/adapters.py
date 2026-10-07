"""La frontera de datos: vocabulario externo → niveles internos."""
from base_book import Level


def level_from_values(price, size):
    # TODO · Ejercicio 1A: convierte precio y tamaño a float; devuelve Level o None si faltan o size <= 0.
    pass


def levels_from_snapshot(row, depth):
    # TODO · Ejercicio 1B: reúne bids y asks usando level_from_values para cada sufijo de 1 a depth.
    pass


def snapshot_to_row(raw):
    # TODO · Ejercicio 5A: adapta price/volume a price/size sin mutar raw; construye los 24 libros en main.
    pass

