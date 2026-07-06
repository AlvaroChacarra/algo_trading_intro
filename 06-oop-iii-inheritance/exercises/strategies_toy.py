# strategies_toy.py - tu primera familia de estrategias (clase 6).
# Herencia + polimorfismo: la semilla del framework Strategy de la clase 10.
# Ejecuta:  python strategies_toy.py
from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def decide(self, imbalance):
        ...


class Momentum(Strategy):          # sigue al mercado
    def decide(self, imbalance):
        return "buy" if imbalance > 0 else "sell"


class Contrarian(Strategy):        # apuesta contra el mercado
    def decide(self, imbalance):
        return "sell" if imbalance > 0 else "buy"


def main():
    strategies = [Momentum(), Contrarian()]
    for imbalance in (0.5, -0.5):
        decisions = [s.decide(imbalance) for s in strategies]
        print("imbalance", imbalance, "->", decisions)
    # mismo bucle, estrategias distintas: eso es polimorfismo.


if __name__ == "__main__":
    main()
