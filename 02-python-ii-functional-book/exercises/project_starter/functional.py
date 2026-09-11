"""L2: reutilizar el cálculo para distintas fotos del mercado."""
def best_prices(orders):
    raise NotImplementedError("L2: completa best_prices")


def make_order(side, price, size):
    if side not in ('buy', 'sell') or price <= 0 or size <= 0:
        raise ValueError('lado válido, precio y tamaño positivos requeridos')
    return {'side': side, 'price': price, 'size': size}
