import os
from datetime import datetime
import sys

# Add src directory to Python path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AAVC_calculate_tool.calculator import AAVCHighestPriceResetStrategy
from AAVC_calculate_tool.data_loader import fetch_price_history, TickerNotFoundError, DataFetchError

# --- Configuration ---
TICKER = "SPY"       # S&P 500 ETF
AMOUNT = 40000      # 4万円
# ---------------------

def main():
    """
    Main function to calculate the investment amount and prepare a notification.
    """
    print(f"Starting calculation for ticker: {TICKER}")

    try:
        # 1. Fetch historical price data
        price_history = fetch_price_history(TICKER)
        if not price_history:
            print(f"Error: No historical data found for {TICKER}.")
            sys.exit(1)

        # 2. Prepare parameters for calculation
        current_price = price_history[-1]
        ref_price = price_history[0]  # Use the oldest price as the reference

        aavc_params = {
            "base_amount": AMOUNT,
            "ref_price": ref_price,
            "asymmetric_coefficient": 2.0,
            "max_investment_multiplier": 3.0,
            "investment_frequency": "daily" # Assumption for single calculation
        }

        # 3. Instantiate strategy and calculate investment amount
        # You can customize the strategy further if needed
        strategy = AAVCHighestPriceResetStrategy()
        calculated_amount = strategy.calculate_investment(
            current_price=current_price,
            price_history=price_history,
            date_history=[],  # Not strictly needed for this calculation
            parameters=aavc_params
        )

        # 4. Create the notification message
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Using a multiline string that can be safely handled by shell
        message = (
            f"Date: {today_str}\n"
            f"Ticker: {TICKER}\n"
            f"Base Amount: ${AMOUNT:,.2f}\n"
            f"--------------------\n"
            f"Latest Close Price: ${current_price:,.2f}\n"
            f"Reference Price (Oldest): ${ref_price:,.2f}\n"
            f"Calculated Investment Amount: ${calculated_amount:,.2f}"
        )

        # 5. Set the message as a GitHub Actions output variable
        # This special format is recognized by GitHub Actions
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
