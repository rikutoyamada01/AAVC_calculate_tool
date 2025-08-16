import argparse
import sys
from datetime import datetime

from AAVC_calculate_tool.calculator import calculate_aavc_investment
from AAVC_calculate_tool.data_loader import fetch_price_history, TickerNotFoundError, DataFetchError
# from AAVC_calculate_tool.config_loader import load_config, ConfigError # Will be implemented in Feature 3

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
        "--ticker", "-t", type=str, help="Ticker symbol for the asset (e.g., AAPL, 7203.T)."
    )
    calc_group.add_argument(
        "--config", "-c", type=str, help="Path to a YAML configuration file."
    )
    calc_parser.add_argument(
        "--amount", "-a", type=float, help="Base investment amount (required with --ticker)."
    )
    calc_parser.add_argument(
        "--ref-price", "-r", type=float, help="Reference price. If not specified, uses the oldest price from history."
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
            
            print_calc_result(args.ticker, calculated_amount)

        except TickerNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except DataFetchError as e:
            print(f"Error fetching data: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    elif args.config:
        # Config file mode (placeholder for now)
        print(f"Config file mode is not yet implemented for calc command: {args.config}")
        print("Please use --ticker, --amount, --ref-price for now.")
        sys.exit(1)

def print_calc_result(ticker, amount):
    today = datetime.now().strftime("%Y-%m-%d")
    print("\n--- Calculation Result ---")
    print(f"Ticker: {ticker}")
    print(f"Date: {today}")
    print(f"Investment Amount: JPY {amount:,.0f}")
    print("--------------------------\n")

if __name__ == "__main__":
    main()