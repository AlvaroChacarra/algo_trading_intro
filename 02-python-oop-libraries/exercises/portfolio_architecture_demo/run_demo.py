import argparse

from portfolio_app.app import PortfolioOptimizerApp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the lesson 2 portfolio architecture demo."
    )
    parser.add_argument(
        "--scenario",
        default="happy",
        choices=["happy", "data_fail", "bad_selection", "model_fail", "interactive"],
        help="Demo scenario to execute.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print("Portfolio Allocation Lab")
    print("=" * 72)
    print("Architecture: universe -> selector -> data_provider -> model -> app")
    print(
        "Goal: understand how classes collaborate and where to debug when something fails."
    )
    print()

    app = PortfolioOptimizerApp()
    app.run(scenario=args.scenario)


if __name__ == "__main__":
    main()
