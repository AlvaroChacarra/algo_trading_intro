from .exceptions import DataRetrievalError


class YahooFinanceDataProvider:
    def __init__(self) -> None:
        self._market_data = {
            "AAPL": {"last_price": 214.0, "expected_return": 0.11, "volatility": 0.22},
            "MSFT": {"last_price": 427.0, "expected_return": 0.10, "volatility": 0.18},
            "NVDA": {"last_price": 912.0, "expected_return": 0.16, "volatility": 0.35},
            "AMZN": {"last_price": 183.0, "expected_return": 0.09, "volatility": 0.24},
            "GOOGL": {"last_price": 167.0, "expected_return": 0.085, "volatility": 0.20},
            "JPM": {"last_price": 198.0, "expected_return": 0.07, "volatility": 0.16},
            "GS": {"last_price": 431.0, "expected_return": 0.072, "volatility": 0.19},
            "BAC": {"last_price": 38.0, "expected_return": 0.055, "volatility": 0.18},
            "MS": {"last_price": 96.0, "expected_return": 0.06, "volatility": 0.17},
            "BLK": {"last_price": 803.0, "expected_return": 0.068, "volatility": 0.21},
            "BTC": {"last_price": 91250.0, "expected_return": 0.18, "volatility": 0.55},
            "GOLD": {"last_price": 2185.0, "expected_return": 0.045, "volatility": 0.11},
            "SILVER": {"last_price": 24.8, "expected_return": 0.05, "volatility": 0.19},
            "SPY": {"last_price": 512.0, "expected_return": 0.075, "volatility": 0.14},
            "QQQ": {"last_price": 438.0, "expected_return": 0.09, "volatility": 0.20},
            "XLK": {"last_price": 215.0, "expected_return": 0.088, "volatility": 0.19},
            "XLF": {"last_price": 41.0, "expected_return": 0.058, "volatility": 0.15},
            "IWM": {"last_price": 206.0, "expected_return": 0.07, "volatility": 0.23},
        }

    def get_market_snapshot(
        self, tickers: list[str], scenario: str = "happy"
    ) -> dict[str, dict[str, float]]:
        snapshot: dict[str, dict[str, float]] = {}

        for ticker in tickers:
            if ticker not in self._market_data:
                raise DataRetrievalError(f"Ticker {ticker} is missing from the provider.")

            if scenario == "data_fail" and ticker == "NVDA":
                raise DataRetrievalError(
                    "Simulated Yahoo Finance timeout while retrieving NVDA."
                )

            snapshot[ticker] = dict(self._market_data[ticker])

        if scenario == "model_fail":
            for ticker in snapshot:
                snapshot[ticker]["expected_return"] = -0.01

        return snapshot
