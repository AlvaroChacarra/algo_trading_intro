"""Dos reglas sobre el mismo dato: decidir no envía una orden."""
from abc import ABC, abstractmethod
from indicators import rsi


class Signal(ABC):
    def __init__(self, name='Signal'):
        # Proporcionado: estado común para identificar cualquier regla.
        self.name = name

    # TODO · Ejercicio 2A: marca decide como método abstracto.
    def decide(self, data: dict) -> str:
        raise NotImplementedError


# TODO · Ejercicio 3A: declara RSISignal como hija de Signal.
class RSISignal:
    def __init__(self, period=14, buy_level=30, sell_level=70):
        # Proporcionado: parámetros coherentes para esta regla pequeña.
        if type(period) is not int or period < 1:
            raise ValueError('period debe ser un entero positivo')
        if not 0 <= buy_level < sell_level <= 100:
            raise ValueError('usa 0 <= buy_level < sell_level <= 100')
        # TODO · Ejercicio 3A: inicializa el nombre heredado como 'RSI'.
        self.period = period
        self.buy_level = buy_level
        self.sell_level = sell_level

    def decide(self, data: dict) -> str:
        # Proporcionado: consume el indicador, no lo vuelve a construir.
        value = rsi(data.get('closes', []), self.period)
        if value is None:
            return 'hold'
        # TODO · Ejercicio 3B: interpreta value con los niveles de esta instancia:
        # compra en <= buy_level, vende en >= sell_level; interior -> hold.
        pass


class ImbalanceSignal(Signal):
    def __init__(self, threshold=0.3):
        # Proporcionado: la banda del desequilibrio es no negativa.
        if not 0 <= threshold <= 1:
            raise ValueError('threshold debe estar entre 0 y 1')
        # TODO · Ejercicio 4A: inicializa el nombre heredado como 'Imbalance'.
        self.threshold = threshold

    def decide(self, data: dict) -> str:
        # Proporcionado: misma entrada que RSI, campo diferente.
        imbalance = data.get('imbalance')
        # TODO · Ejercicio 4A: trata None antes de comparar.
        # TODO · Ejercicio 4B: aplica la banda estricta de la instancia.
        pass
