from .exceptions import SelectionError
from .universe import AssetUniverse


class UnderlyingSelector:
    def __init__(
        self,
        universe: AssetUniverse,
        min_choices: int = 2,
        max_choices: int = 5,
        preset_selection: str | None = None,
        input_reader=input,
    ) -> None:
        self.universe = universe
        self.min_choices = min_choices
        self.max_choices = max_choices
        self.preset_selection = preset_selection
        self.input_reader = input_reader

    def set_preset_selection(self, preset_selection: str | None) -> None:
        self.preset_selection = preset_selection

    def prompt_selection(self) -> list[str]:
        self._print_universe()
        if self.preset_selection is None:
            raw_selection = self.input_reader(
                "Selecciona entre 2 y 5 tickers separados por comas: "
            )
        else:
            raw_selection = self.preset_selection
            print(f"Seleccion simulada: {raw_selection}")

        return self._parse_selection(raw_selection)

    def _print_universe(self) -> None:
        print("Universo disponible")
        print("-" * 72)
        for category, tickers in self.universe.get_assets_by_category().items():
            print(f"{category:<12}: {', '.join(tickers)}")
        print()

    def _parse_selection(self, raw_selection: str) -> list[str]:
        if raw_selection is None:
            raise SelectionError("No selection received.")

        tickers = [
            piece.strip().upper()
            for piece in raw_selection.split(",")
            if piece.strip()
        ]

        if len(tickers) < self.min_choices or len(tickers) > self.max_choices:
            raise SelectionError(
                f"Selection must contain between {self.min_choices} and {self.max_choices} tickers."
            )

        duplicates = sorted({ticker for ticker in tickers if tickers.count(ticker) > 1})
        if duplicates:
            raise SelectionError(f"Duplicate tickers detected: {', '.join(duplicates)}.")

        allowed_tickers = set(self.universe.get_all_tickers())
        invalid = sorted(ticker for ticker in tickers if ticker not in allowed_tickers)
        if invalid:
            raise SelectionError(f"Unknown tickers: {', '.join(invalid)}.")

        return tickers
