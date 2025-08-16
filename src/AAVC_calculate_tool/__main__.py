import argparse
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

    # --- 'backtest' subcommand (placeholder for now) ---
    backtest_parser = subparsers.add_parser(
        "backtest", help="Run a backtest for a strategy."
    )
    # Placeholder arguments for backtest
    backtest_parser.add_argument("--ticker", type=str, help="Ticker symbol for backtest.")
    backtest_parser.add_argument("--start-date", type=str, help="Start date for backtest (YYYY-MM-DD).")
    backtest_parser.add_argument("--end-date", type=str, help="End date for backtest (YYYY-MM-DD).")


    args = parser.parse_args()

    if args.command == "calc":
        handle_calc_command(args)
    elif args.command == "backtest":
        print("Backtest command is not yet implemented.")
        sys.exit(1)
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

if __name__ == "__main__":
    main()
