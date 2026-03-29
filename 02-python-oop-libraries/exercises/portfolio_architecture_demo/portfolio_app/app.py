from .data_provider import YahooFinanceDataProvider
from .exceptions import DataRetrievalError, ModelComputationError, SelectionError
from .model import PortfolioOptimizerModel
from .selector import UnderlyingSelector
from .universe import AssetUniverse


class PortfolioOptimizerApp:
    def __init__(
        self,
        universe: AssetUniverse | None = None,
        selector: UnderlyingSelector | None = None,
        data_provider: YahooFinanceDataProvider | None = None,
        model: PortfolioOptimizerModel | None = None,
    ) -> None:
        self.universe = universe or AssetUniverse()
        self.selector = selector or UnderlyingSelector(self.universe)
        self.data_provider = data_provider or YahooFinanceDataProvider()
        self.model = model or PortfolioOptimizerModel()

    def run(self, scenario: str = "happy") -> None:
        preset_selection = self._preset_selection_for(scenario)
        self.selector.set_preset_selection(preset_selection)

        try:
            selected_tickers = self.selector.prompt_selection()
            print(f"Seleccion validada: {', '.join(selected_tickers)}")
            print()

            snapshot = self.data_provider.get_market_snapshot(selected_tickers, scenario)
            weights = self.model.compute_weights(snapshot)

            print("Resultado de cartera")
            print("-" * 72)
            self._print_result_table(snapshot, weights)
            print()
            print(
                f"Suma de pesos: {sum(weights.values()):.4f} | Escenario: {scenario}"
            )
            print("Ownership correcto: selector -> provider -> model -> app")
        except SelectionError as error:
            self._print_failure(
                title="SelectionError",
                error=error,
                owner="portfolio_app/selector.py",
                reasoning="La entrada del usuario es invalida antes de tocar datos o modelo.",
            )
        except DataRetrievalError as error:
            self._print_failure(
                title="DataRetrievalError",
                error=error,
                owner="portfolio_app/data_provider.py",
                reasoning="La capa de datos fallo; todavia no toca depurar el modelo.",
            )
        except ModelComputationError as error:
            self._print_failure(
                title="ModelComputationError",
                error=error,
                owner="portfolio_app/model.py",
                reasoning="Los datos existen, pero la logica del modelo no puede producir pesos validos.",
            )

    def _preset_selection_for(self, scenario: str) -> str | None:
        if scenario == "interactive":
            return None

        scenario_presets = {
            "happy": "AAPL, MSFT, BTC, SPY",
            "data_fail": "AAPL, NVDA, SPY",
            "bad_selection": "AAPL, FAKE, MSFT",
            "model_fail": "XLF, BAC, SILVER",
        }
        return scenario_presets.get(scenario, "AAPL, MSFT, BTC, SPY")

    def _print_result_table(
        self, snapshot: dict[str, dict[str, float]], weights: dict[str, float]
    ) -> None:
        header = (
            f"{'Ticker':<10}{'Price':>12}{'ExpRet':>12}{'Vol':>10}{'Weight':>12}"
        )
        print(header)
        print("-" * len(header))
        for ticker, metrics in snapshot.items():
            weight = weights.get(ticker, 0.0)
            print(
                f"{ticker:<10}"
                f"{metrics['last_price']:>12.2f}"
                f"{metrics['expected_return']:>12.3f}"
                f"{metrics['volatility']:>10.3f}"
                f"{weight:>12.3f}"
            )

    def _print_failure(
        self, title: str, error: Exception, owner: str, reasoning: str
    ) -> None:
        print(f"{title}: {error}")
        print(f"Busca primero en: {owner}")
        print(f"Por que: {reasoning}")
