import argparse
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Set matplotlib backend to 'Agg' for non-interactive plotting
import matplotlib
matplotlib.use('Agg')

# Set default encoding for stdout to UTF-8 for consistent console output (compatible with older Python versions)
import io
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from .backtester import ComparisonResult, run_comparison_backtest
from .calculator import AAVCStrategy  # For calc command, still uses the direct function
from .config_loader import (
    ConfigError,
    ConfigNotFoundError,
    ConfigParseError,
    load_config,
    prepare_calculation_jobs,
)
from .data_loader import (
    DataFetchError,
    TickerNotFoundError,
    fetch_price_history,
)
from .display import generate_dynamic_summary_table
from .plotter import plot_multi_algorithm_chart
from .recorder import LogEntry, LogWriteError, record_investment


def parse_algorithm_parameters(param_string: str) -> Dict[str, Dict[str, Any]]:
    """Parses algorithm-specific parameters from a comma-separated string of algorithm groups.
    Each group is "algo_name:param1=val1;param2=val2" (using semicolon for inner params).
    Example: "aavc:ref_price=100;asymmetric_coefficient=2.0,dca:base_amount=200"
    """
    if not param_string:
        return {}

    algorithm_params = {}

    # Split by comma to get individual algorithm groups
    for param_group_str in param_string.split(","):
        param_group_str = param_group_str.strip()
        if not param_group_str or ":" not in param_group_str:
            continue

        algorithm_name, params_inner_str = param_group_str.split(":", 1)
        algorithm_name = algorithm_name.strip().strip('""')

        if algorithm_name not in algorithm_params:
            algorithm_params[algorithm_name] = {}

        # Split inner parameters by semicolon
        for param_assignment in params_inner_str.split(";"): # Changed from comma to semicolon
            param_assignment = param_assignment.strip()
            if "=" not in param_assignment:
                continue

            param_name, param_value_str = param_assignment.split("=", 1)
            param_name = param_name.strip().strip('""')
            param_value_str = param_value_str.strip().strip('""')

            try:
                if "." in param_value_str:
                    param_value = float(param_value_str)
                else:
                    param_value = int(param_value_str)
            except ValueError:
                param_value = param_value_str

            algorithm_params[algorithm_name][param_name] = param_value

    return algorithm_params


def main():
    parser = argparse.ArgumentParser(
        description="AAVC Calculate Tool: Calculate investment amounts or run backtests."
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- 'calc' subcommand ---
    calc_parser = subparsers.add_parser(
        "calc", help="Calculate today's investment amount for a ticker or from a config file."
    )
    calc_group = calc_parser.add_mutually_exclusive_group(required=True)
    calc_group.add_argument(
        "--ticker", "-t", type=str,
        help="Ticker symbol for the asset (e.g., AAPL, 7203.T)."
    )
    calc_group.add_argument(
        "--config", "-c", type=str, help="Path to a YAML configuration file."
    )
    calc_parser.add_argument(
        "--amount", "-a", type=float,
        help="Base investment amount (required with --ticker)."
    )
    calc_parser.add_argument(
        "--ref-price", "-r", type=float,
        help="Reference price. If not specified, uses the oldest price from history."
    )
    calc_parser.add_argument(
        "--log-file", type=str, default="investment_log.csv",
        help="Path to the investment log CSV file (default: investment_log.csv)."
    )
    calc_parser.add_argument(
        "--asymmetric-coefficient", type=float,
        help="Asymmetric coefficient for AAVC calculation (default: 2.0)."
    )
    calc_parser.add_argument(
        "--max-multiplier", type=float,
        help="Maximum investment multiplier for AAVC calculation (default: 3.0)."
    )
    calc_parser.add_argument(
        "--ref-ma-period", type=int,
        help="Period for moving average reference price (default: 200)."
    )

    # --- 'backtest' subcommand ---
    backtest_parser = subparsers.add_parser(
        "backtest",
        help="Run a backtest comparison for AAVC, DCA, and Buy & Hold strategies."
    )
    backtest_parser.add_argument("--ticker", "-t", type=str, required=True,
                                 help="Ticker symbol for backtest.")
    backtest_parser.add_argument("--start-date", type=str, required=True,
                                 help="Start date for backtest (YYYY-MM-DD).")
    backtest_parser.add_argument("--end-date", type=str, required=True,
                                 help="End date for backtest (YYYY-MM-DD).")
    backtest_parser.add_argument("--amount", "-a", type=float, required=True,
                                 help="Base investment amount.")
    # New arguments for multi-algorithm comparison
    backtest_parser.add_argument(
        "--algorithms",
        type=str,
        help="Comma-separated list of algorithms to compare (e.g., aavc,dca,buy_and_hold). "
             "Defaults to all registered algorithms."
    )
    backtest_parser.add_argument(
        "--algorithm-params",
        type=str,
        help="Algorithm-specific parameters (e.g., aavc:ref_price=100,dca:base_amount=200)."
    )
    backtest_parser.add_argument(
        "--compare-mode",
        choices=["simple", "detailed"],
        default="simple",
        help="Comparison display mode (default: simple)."
    )
    backtest_parser.add_argument("--plot", action="store_true",
                                 help="Generate and save comparison chart.")
    backtest_parser.add_argument(
        "--investment-frequency",
        choices=["daily", "monthly"],
        default="monthly",
        help="Investment frequency (default: monthly)."
    )

    args = parser.parse_args()

    if args.command == "calc":
        handle_calc_command(args)
    elif args.command == "backtest":
        handle_backtest_command(args)
    else:
        parser.print_help()
        sys.exit(1)

def handle_calc_command(args):
    # This part still uses the direct AAVCStrategy for calculation
    # as it's a single calculation, not a comparison.
    if args.ticker:
        # Single ticker mode
        if args.amount is None:
            print("Error: --amount is required when --ticker is specified.")
            sys.exit(1)

        try:
            price_path = fetch_price_history(args.ticker)
            if not price_path:
                print(f"Error: No historical data found for {args.ticker}.")
                sys.exit(1)

            # Instantiate AAVCStrategy for single calculation
            aavc_strategy_instance = AAVCStrategy()

            # Prepare parameters for AAVCStrategy
            aavc_params = {
                "base_amount": args.amount,
                "reference_price": args.ref_price if args.ref_price is not None else price_path[0],
            }
            if args.asymmetric_coefficient is not None:
                aavc_params["asymmetric_coefficient"] = args.asymmetric_coefficient
            if args.max_multiplier is not None:
                aavc_params["max_investment_multiplier"] = args.max_multiplier
            if args.ref_ma_period is not None:
                aavc_params["reference_price_ma_period"] = args.ref_ma_period

            calculated_amount = aavc_strategy_instance.calculate_investment(
                current_price=price_path[-1],
                price_history=price_path,
                date_history=[],  # Not used in this context, but required by interface
                parameters=aavc_params
            )

            log_entry: LogEntry = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "ticker": args.ticker,
                "base_amount": args.amount,
                "reference_price": aavc_params["reference_price"],
                "calculated_investment": calculated_amount,
            }
            try:
                record_investment(log_entry, args.log_file)
            except LogWriteError as e:
                print(f"Warning: Could not write to log file: {e}")

            print_calc_result(args.ticker, calculated_amount)

        except TickerNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except DataFetchError as e:
            print(f"Error fetching data: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.config:
        # Config file mode
        try:
            config = load_config(args.config)
            jobs = prepare_calculation_jobs(config)

            for job in jobs:
                ticker = job["ticker"]
                base_amount = job["base_amount"]
                ref_price = job.get("reference_price")
                asymmetric_coefficient = job.get("asymmetric_coefficient")
                max_investment_multiplier = job.get("max_investment_multiplier")
                reference_price_ma_period = job.get("reference_price_ma_period")

                try:
                    price_path = fetch_price_history(ticker)

                    # Instantiate AAVCStrategy for single calculation
                    aavc_strategy_instance = AAVCStrategy()

                    # Prepare parameters for AAVCStrategy
                    aavc_params = {
                        "base_amount": base_amount,
                        "reference_price": ref_price if ref_price is not None else price_path[0],
                    }
                    if asymmetric_coefficient is not None:
                        aavc_params["asymmetric_coefficient"] = asymmetric_coefficient
                    if max_investment_multiplier is not None:
                        aavc_params["max_investment_multiplier"] = max_investment_multiplier
                    if reference_price_ma_period is not None:
                        aavc_params["reference_price_ma_period"] = reference_price_ma_period

                    calculated_amount = aavc_strategy_instance.calculate_investment(
                        current_price=price_path[-1],
                        price_history=price_path,
                        date_history=[],  # Not used in this context, but required by interface
                        parameters=aavc_params
                    )

                    log_entry = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "ticker": ticker,
                        "base_amount": base_amount,
                        "reference_price": aavc_params["reference_price"],
                        "calculated_investment": calculated_amount,
                    }
                    try:
                        record_investment(log_entry, args.log_file)
                    except LogWriteError as e:
                        print(f"Warning for {ticker}: Could not write to log file: {e}")

                    print_calc_result(ticker, calculated_amount)

                except TickerNotFoundError as e:
                    print(f"Error for {ticker}: {e}. Skipping.")
                except DataFetchError as e:
                    print(f"Error fetching data for {ticker}: {e}. Skipping.")
                except Exception as e:
                    print(f"Error for {ticker}: {e}. Skipping.")

        except ConfigNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except ConfigParseError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except ConfigError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

def print_calc_result(ticker, amount):
    today = datetime.now().strftime("%Y-%m-%d")
    print("\n--- Calculation Result ---")
    print(f"Ticker: {ticker}")
    print(f"Date: {today}")
    print(f"Investment Amount: JPY {amount:.0f}")
    print("--------------------------\n")


def handle_backtest_command(args):
    """Handle the backtest command"""
    try:
        # Parse algorithms
        algorithms_to_run: Optional[List[str]] = None
        if args.algorithms:
            algorithms_to_run = [algo.strip() for algo in args.algorithms.split(",")]

        # Parse algorithm-specific parameters
        algo_specific_params = parse_algorithm_parameters(args.algorithm_params)

        # Prepare base parameters for all algorithms
        base_parameters = {
            "base_amount": args.amount,
            # Add other common parameters here if needed
        }

        # Merge base parameters with algorithm-specific parameters
        # Note: This simple merge assumes no conflicts. For more complex scenarios,
        # a deeper merge or validation might be needed.
        for algo_name, params in algo_specific_params.items():
            if algo_name in base_parameters:
                base_parameters[algo_name].update(params)
            else:
                base_parameters[algo_name] = params

        print(f"DEBUG: algo_specific_params: {algo_specific_params}")
        print(f"DEBUG: base_parameters before run_comparison_backtest: {base_parameters}")
        # Run comparison backtest
        comparison_result: ComparisonResult = run_comparison_backtest(
            ticker=args.ticker,
            start_date_str=args.start_date,
            end_date_str=args.end_date,
            base_parameters=base_parameters,
            algorithm_names=algorithms_to_run
        )

        # Display summary table
        summary_table = generate_dynamic_summary_table(
            comparison_result, mode=args.compare_mode
        )
        print(summary_table)

        # --- Add custom output for AAVC investment details ---
        if "aavc" in comparison_result.results:
            aavc_result = comparison_result.results["aavc"]
            actual_max_investment = max(aavc_result.investment_history) if aavc_result.investment_history else 0
            actual_total_invested = sum(aavc_result.investment_history)

            print(f"\n--- AAVC Investment Details ---")
            print(f"Actual Max Single Period Investment (AAVC): JPY {actual_max_investment:.0f}")
            print(f"Actual Total Invested (AAVC): JPY {actual_total_invested:.0f}")
            print(f"-------------------------------")
        # --- End custom output ---

        # Generate chart if requested
        if args.plot:
            chart_path = plot_multi_algorithm_chart(
                comparison_result,
                f"multi_algorithm_comparison_{args.ticker}_{args.start_date}_{args.end_date}.png"
            )
            print(f"\nChart saved to: {os.path.abspath(chart_path)}")

    except TickerNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except DataFetchError as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
