"""Indicador proporcionado: RSI de ventana simple, sin suavizado de Wilder."""


def rsi(closes, period=14):
    """Últimos period cambios; period + 1 cierres diarios, antiguos primero.

    Los cierres son números finitos. Devuelve None sin historia suficiente,
    50 para una ventana plana, 100 si solo sube y 0 si solo baja.
    """
    if type(period) is not int or period < 1:
        raise ValueError('period debe ser un entero positivo')
    if len(closes) < period + 1:
        return None
    window = closes[-(period + 1):]
    changes = [current - previous for previous, current in zip(window, window[1:])]
    average_gain = sum(max(change, 0) for change in changes) / period
    average_loss = sum(max(-change, 0) for change in changes) / period
    if average_gain == average_loss == 0:
        return 50.0
    if average_loss == 0:
        return 100.0
    strength = average_gain / average_loss
    return 100 - 100 / (1 + strength)
