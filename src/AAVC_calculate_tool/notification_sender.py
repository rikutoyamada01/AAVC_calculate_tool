import os
from datetime import datetime, timedelta, date # Added date
import sys
from typing import List, Tuple, Any # Added List, Tuple, Any

# Add src directory to Python path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AAVC_calculate_tool.calculator import AAVCHighestInHistoryStrategy
from AAVC_calculate_tool.data_loader import fetch_price_history_by_date, TickerNotFoundError, DataFetchError
from AAVC_calculate_tool.config_loader import load_config

# Load configuration
config = load_config(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..\..\config.yaml')))

# --- Configuration ---
TICKER = config.get("notification_sender", {}).get("ticker", "SPY")
AMOUNT = config.get("notification_sender", {}).get("amount", 40000)
# ---------------------

def _get_config_path() -> str:
    """Returns the absolute path to the config.yaml file."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..\..\config.yaml'))

def _fetch_and_prepare_data(ticker: str) -> Tuple[List[float], List[date], float, float]:
    """
    Fetches historical price data and prepares it for AAVC calculation.

    Args:
        ticker: The stock ticker symbol.

    Returns:
        A tuple containing:
            - price_history (List[float]): List of historical prices.
            - date_history (List[date]): List of corresponding dates.
            - current_price (float): The latest price.
            - ref_price (float): The reference price (oldest price in history).

    Raises:
        TickerNotFoundError: If the ticker is not found.
        DataFetchError: If there's an error fetching data.
        SystemExit: If no historical data is found.
    """
    end_date = datetime.utcnow().strftime('%Y-%m-%d')
    start_date = (datetime.utcnow() - timedelta(days=365 * 2)).strftime('%Y-%m-%d') # Last 2 years

    price_history, date_history = fetch_price_history_by_date(ticker, start_date, end_date)
    if not price_history:
        print(f"Error: No historical data found for {ticker} in the specified date range.")
        sys.exit(1)

    # Convert date_history from List[str] to List[date]
    date_history = [datetime.strptime(d, "%Y-%m-%d").date() for d in date_history]

    current_price = price_history[-1]
    ref_price = price_history[0]  # Use the oldest price as the reference

    return price_history, date_history, current_price, ref_price

def _calculate_investment_amount(
    current_price: float,
    price_history: List[float],
    date_history: List[date],
    amount: float,
    ref_price: float
) -> Tuple[float, float]:
    """
    Calculates the AAVC investment amount.

    Args:
        current_price: The current price of the stock.
        price_history: List of historical prices.
        date_history: List of corresponding dates.
        amount: The base investment amount.
        ref_price: The reference price for calculation.

    Returns:
        A tuple containing:
            - calculated_amount (float): The calculated investment amount.
            - actual_reference_price (float): The actual reference price used in calculation.
    """
    aavc_params = {
        "base_amount": amount,
        "ref_price": ref_price,
        "asymmetric_coefficient": 2.0,
        "max_investment_multiplier": 3.0,
        "investment_frequency": "daily" # Assumption for single calculation
    }

    strategy = AAVCHighestInHistoryStrategy()
    calculated_amount = strategy.calculate_investment(
        current_price=current_price,
        price_history=price_history,
        date_history=date_history,
        parameters=aavc_params
    )

    actual_reference_price = strategy._strategy_context.get("last_calculated_reference_price", ref_price)
    return calculated_amount, actual_reference_price

def _format_notification_message(
    ticker: str,
    amount: float,
    current_price: float,
    actual_reference_price: float,
    calculated_amount: float
) -> str:
    """
    Formats the notification message.

    Args:
        ticker: The stock ticker symbol.
        amount: The base investment amount.
        current_price: The latest close price.
        actual_reference_price: The actual reference price used in calculation.
        calculated_amount: The calculated investment amount.

    Returns:
        A formatted string for the notification body.
    """
    today_str = datetime.utcnow().strftime('%Y-%m-%d')

    message = (
        f"Date: {today_str}\n"
        f"Ticker: {ticker}\n"
        f"Base Amount: JPY {amount:,.2f}\n"
        f"--------------------\n"
        f"Latest Close Price: JPY {current_price:,.2f}\n"
        f"Actual Reference Price: JPY {actual_reference_price:,.2f}\n"
        f"Calculated Investment Amount: JPY {calculated_amount:,.2f}"
    )
    return message

def main():
    """
    Main function to calculate the investment amount and prepare a notification.
    """
    print(f"Starting calculation for ticker: {TICKER}")

    try:
        # Fetch and prepare data
        price_history, date_history, current_price, ref_price = _fetch_and_prepare_data(TICKER)

        # Calculate investment amount
        calculated_amount, actual_reference_price = _calculate_investment_amount(
            current_price, price_history, date_history, AMOUNT, ref_price
        )
        print(f"DEBUG: Actual reference price (before message): {actual_reference_price}")

        # Create the notification message
        message = _format_notification_message(
            TICKER, AMOUNT, current_price, actual_reference_price, calculated_amount
        )

        # Set the message as a GitHub Actions output variable
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'notification_body<<EOF', file=fh)
            print(message, file=fh)
            print(f'EOF', file=fh)
        print("Successfully prepared notification body.")

    except TickerNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except DataFetchError as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
