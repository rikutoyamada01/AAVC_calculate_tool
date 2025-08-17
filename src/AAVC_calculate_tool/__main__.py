import argparse
import os
import sys
from datetime import datetime

from .calculator import calculate_aavc_investment
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
from .recorder import LogEntry, LogWriteError, record_investment
from .backtester import run_comparison_backtest, BacktestParams
from .display import generate_summary_table
from .plotter import plot_comparison_chart


def main():
    parser = argparse.ArgumentParser(
        description="AAVC Calculate Tool: Calculate investment amounts or run backtests."
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- 'calc' subcommand ---
    calc_parser = subparsers.add_parser(
        "calc", help="Calculate today\'s investment amount for a ticker or from a config file."
    )
    calc_group = calc_parser.add_mutually_exclusive_group(required=True)
    calc_group.add_argument(
        "--ticker", "-t", type=str, help="Ticker symbol for the asset (e.g., AAPL, 7203.T)."
    )
    calc_group.add_argument(
        "--config", "-c", type=str, help="Path to a YAML configuration file."
    )
    calc_parser.add_argument(
        "--amount", "-a", type=float, help="Base investment amount (required with --ticker)."
    )
    calc_parser.add_argument(
        "--ref-price", "-r", type=float, help="Reference price. If not specified, uses the oldest price from history.",
    )
    calc_parser.add_argument(
        "--log-file", type=str, default="investment_log.csv",
        help="Path to the investment log CSV file (default: investment_log.csv)."
    )

    # --- 'backtest' subcommand ---
    backtest_parser = subparsers.add_parser(
        "backtest", help="Run a backtest comparison for AAVC, DCA, and Buy & Hold strategies."
    )
    backtest_parser.add_argument("--ticker", "-t", type=str, required=True, help="Ticker symbol for backtest.")
    backtest_parser.add_argument("--start-date", type=str, required=True, help="Start date for backtest (YYYY-MM-DD).")
    backtest_parser.add_argument("--end-date", type=str, required=True, help="End date for backtest (YYYY-MM-DD).")
    backtest_parser.add_argument("--amount", "-a", type=float, required=True, help="Base investment amount.")
    backtest_parser.add_argument("--ref-price", type=float, help="Reference price. If not specified, uses the oldest price from history.")
    backtest_parser.add_argument("--asymmetric-coefficient", type=float, default=1.0, help="Asymmetric coefficient for AAVC strategy (default: 1.0).")
    backtest_parser.add_argument("--volatility-period", type=int, default=20, help="Volatility calculation period (default: 20).")
    backtest_parser.add_argument("--plot", action="store_true", help="Generate and save comparison chart.")


    args = parser.parse_args()

    if args.command == "calc":
        handle_calc_command(args)
    elif args.command == "backtest":
        handle_backtest_command(args)
    else:
        parser.print_help()
        sys.exit(1)

def handle_calc_command(args):
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

            reference_price = args.ref_price if args.ref_price is not None else price_path[0]

            calculated_amount = calculate_aavc_investment(
                price_path=price_path,
                base_amount=args.amount,
                reference_price=reference_price
            )

            log_entry: LogEntry = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "ticker": args.ticker,
                "base_amount": args.amount,
                "reference_price": reference_price,
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

                try:
                    price_path = fetch_price_history(ticker)
                    if not price_path:
                        print(f"Error: No historical data found for {ticker}. Skipping.")
                        continue

                    reference_price = ref_price if ref_price is not None else price_path[0]

                    kwargs = {
                        "price_path": price_path,
                        "base_amount": base_amount,
                        "reference_price": reference_price,
                    }
                    if asymmetric_coefficient is not None:
                        kwargs["asymmetric_coefficient"] = asymmetric_coefficient

                    calculated_amount = calculate_aavc_investment(**kwargs)
                    log_entry = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "ticker": ticker,
                        "base_amount": base_amount,
                        "reference_price": reference_price,
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
        # Fetch price history for the specified period
        price_path = fetch_price_history(args.ticker)
        if not price_path:
            print(f"Error: No historical data found for {args.ticker}.")
            sys.exit(1)
        
        # Set reference price
        reference_price = args.ref_price if args.ref_price is not None else price_path[0]
        
        # Prepare backtest parameters
        backtest_params: BacktestParams = {
            "ticker": args.ticker,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "base_amount": args.amount,
            "reference_price": reference_price,
            "asymmetric_coefficient": args.asymmetric_coefficient,
            "volatility_period": args.volatility_period
        }
        
        # Run comparison backtest
        results = run_comparison_backtest(backtest_params)
        
        # Display summary table
        summary_table = generate_summary_table(
            results, args.ticker, args.start_date, args.end_date
        )
        print(summary_table)
        
        # Generate chart if requested
        if args.plot:
            chart_path = plot_comparison_chart(
                results, args.ticker, args.start_date, args.end_date
            )
            print(f"\nChart saved to: {os.path.abspath(chart_path)}")
            
    except TickerNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except DataFetchError as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
