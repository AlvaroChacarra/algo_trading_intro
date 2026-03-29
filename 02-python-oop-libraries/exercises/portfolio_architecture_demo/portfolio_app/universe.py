class AssetUniverse:
    def __init__(self) -> None:
        self._assets_by_category = {
            "tech": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"],
            "financials": ["JPM", "GS", "BAC", "MS", "BLK"],
            "alts": ["BTC", "GOLD", "SILVER"],
            "etfs": ["SPY", "QQQ", "XLK", "XLF", "IWM"],
        }

    def get_assets_by_category(self) -> dict[str, list[str]]:
        return {
            category: tickers[:]
            for category, tickers in self._assets_by_category.items()
        }

    def get_all_tickers(self) -> list[str]:
        all_tickers: list[str] = []
        for tickers in self._assets_by_category.values():
            all_tickers.extend(tickers)
        return all_tickers
