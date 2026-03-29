from .exceptions import ModelComputationError


class PortfolioOptimizerModel:
    def compute_weights(
        self, snapshot: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        if not snapshot:
            raise ModelComputationError("Snapshot is empty.")

        scores: dict[str, float] = {}
        for ticker, metrics in snapshot.items():
            self._validate_metrics(ticker, metrics)
            score = metrics["expected_return"] / metrics["volatility"]
            if score > 0:
                scores[ticker] = score

        if not scores:
            raise ModelComputationError(
                "No positive scores available. The model cannot build weights."
            )

        total_score = sum(scores.values())
        if total_score <= 0:
            raise ModelComputationError("Total score is not strictly positive.")

        return {ticker: score / total_score for ticker, score in scores.items()}

    def _validate_metrics(self, ticker: str, metrics: dict[str, float]) -> None:
        required_fields = {"last_price", "expected_return", "volatility"}
        missing = required_fields.difference(metrics)
        if missing:
            raise ModelComputationError(
                f"{ticker} is missing fields: {', '.join(sorted(missing))}."
            )

        if metrics["volatility"] <= 0:
            raise ModelComputationError(
                f"{ticker} has non-positive volatility, so score cannot be computed."
            )
