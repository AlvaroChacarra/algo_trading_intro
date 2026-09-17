"""L3: el programa importa TU módulo de L2; importar no ejecuta una demo."""
from exchange.functional import best_prices, make_order


def describe(orders):
    raise NotImplementedError("L3: completa describe")


if __name__ == '__main__':
    print(describe([make_order('buy', 99, 2), make_order('sell', 101, 3)]))
