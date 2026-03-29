# Portfolio Architecture Demo

Mini repo for lesson 2: a small portfolio allocation app designed to show how classes and modules collaborate in a clean OOP architecture.

## Teaching goal

This exercise is not about building a real optimizer.
It is about teaching:

- modularity
- encapsulation
- clear ownership
- reusable code
- debugging by responsibility

## Architecture

The demo is split into five main responsibilities:

- `AssetUniverse`: defines which assets exist
- `UnderlyingSelector`: validates what the user selected
- `YahooFinanceDataProvider`: simulates market data retrieval
- `PortfolioOptimizerModel`: converts data into weights
- `PortfolioOptimizerApp`: orchestrates the full workflow

## Folder structure

- `run_demo.py` - CLI entrypoint
- `teaching_notes.md` - teaching script and debugging prompts
- `portfolio-architecture-interactive.html` - interactive presentation for introducing the architecture
- `portfolio_app/universe.py` - asset catalog
- `portfolio_app/selector.py` - input parsing and validation
- `portfolio_app/data_provider.py` - fake Yahoo-style data retrieval
- `portfolio_app/model.py` - simple score-based weighting model
- `portfolio_app/app.py` - orchestration and output
- `portfolio_app/exceptions.py` - custom exception types

## Scenarios

Run from this folder:

```bash
python run_demo.py --scenario happy
python run_demo.py --scenario data_fail
python run_demo.py --scenario bad_selection
python run_demo.py --scenario model_fail
python run_demo.py --scenario interactive
```

## What students should notice

- errors should be traced to the module that owns the behavior
- the model does not know how the user typed the tickers
- the selector does not know how weights are computed
- the data provider does not decide the final portfolio
- the app connects components, but does not contain all the logic

## Notes

- market data is local and deterministic
- no internet connection is required
- classes use explicit `__init__` methods
- no external dependencies are required
