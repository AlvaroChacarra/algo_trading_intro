# orders_demo.py - clase 4: el dict de orden se vuelve un OBJETO.
# Datos + comportamiento juntos. Ejecuta:  python orders_demo.py


class Order:
    def __init__(self, symbol, side, price, size):   # ej. 1
        self.symbol = symbol
        self.side = side
        self.price = price
        self.size = size

    def notional(self):                              # ej. 2
        return self.price * self.size

    def __repr__(self):                              # ej. 3
        return f"Order({self.side} {self.size} {self.symbol} @ {self.price})"


class Fill:
    def __init__(self, symbol, side, price, size):   # ej. 4
        self.symbol = symbol
        self.side = side
        self.price = price
        self.size = size

    def cash_flow(self):
        sign = -1 if self.side == "buy" else 1
        return sign * self.price * self.size


def main():                                          # ej. 5 y 6
    order = Order("BTCUSDT", "buy", 99950, 0.10)
    print(order)
    print("notional:", order.notional())

    buy = Fill("BTCUSDT", "buy", 99950, 0.10)
    sell = Fill("BTCUSDT", "sell", 100050, 0.10)
    print("cash compra:", buy.cash_flow())
    print("cash venta:", sell.cash_flow())
    print("total:", round(buy.cash_flow() + sell.cash_flow(), 2))
    # Quien suma todos los cash_flows en el tiempo? El PositionTracker (clase 5).


if __name__ == "__main__":
    main()
