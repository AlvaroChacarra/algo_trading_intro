class SelectionError(Exception):
    """Raised when user selection is invalid."""


class DataRetrievalError(Exception):
    """Raised when market data cannot be retrieved."""


class ModelComputationError(Exception):
    """Raised when the portfolio model cannot produce valid weights."""
