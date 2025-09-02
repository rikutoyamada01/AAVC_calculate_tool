import numpy as np
from datetime import date, timedelta
import sys
import io
from simulate_prices import generate_deterministic_price_path
from src.AAVC_calculate_tool.calculator import (
    AAVCHighestPriceResetStrategy,
    AAVCMovingAverageStrategy,
    AAVCStaticStrategy,
    AAVCDynamicStrategy,
    BaseAAVCStrategy,
)

# Set default encoding for stdout to UTF-8 for consistent console output
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def run_strategy_simulation(
    strategy: BaseAAVCStrategy,
    strategy_params: dict,
    price_path: list[float],
    dates: list[date],
    base_amount: float,
    num_years: int,
    trading_days_per_year: int = 252,
) -> dict:
    """Runs a simulation for a single AAVC strategy."""
    shares_owned = 0.0
    total_invested = 0.0
    portfolio_history = []
    
    num_trading_days = len(price_path)

    for i in range(num_trading_days):
        current_price = price_path[i]
        
        # Base parameters for all strategies
        params = {
            "base_amount": base_amount,
            "asymmetric_coefficient": 2.0,
            "max_investment_multiplier": 3.0,
            "investment_frequency": "daily",
        }
        # Add strategy-specific parameters
        params.update(strategy_params)

        investment_amount = strategy.calculate_investment(
            current_price=current_price,
            price_history=list(price_path[:i+1]),
            date_history=dates[:i+1],
            parameters=params,
        )
        
        if investment_amount > 0:
            shares_bought = investment_amount / current_price
            shares_owned += shares_bought
            total_invested += investment_amount
        
        portfolio_value = shares_owned * current_price
        portfolio_history.append(portfolio_value)

    final_value = portfolio_history[-1] if portfolio_history else 0.0
    
    # --- Performance Calculation ---
    annual_return = 0.0
    sharpe_ratio = 0.0
    if total_invested > 0 and num_years > 0:
        annual_return = ((final_value / total_invested)**(1/num_years) - 1) * 100

        portfolio_daily_returns = np.diff(portfolio_history) / portfolio_history[:-1]
        risk_free_rate_annual = 0.02
        risk_free_rate_daily = (1 + risk_free_rate_annual)**(1/trading_days_per_year) - 1

        if len(portfolio_daily_returns) > 0:
            excess_returns = portfolio_daily_returns - risk_free_rate_daily
            std_dev_excess_returns = np.std(excess_returns)
            
            if std_dev_excess_returns > 0:
                sharpe_ratio = np.mean(excess_returns) / std_dev_excess_returns * np.sqrt(trading_days_per_year)

    return {
        "Strategy": strategy.get_metadata().name,
        "Parameters": strategy_params,
        "Final Value": f"\u20a1{final_value/1000:.0f}k",
        "Ann. Return": f"{annual_return:.1f}%",
        "Sharpe Ratio": f"{sharpe_ratio:.2f}",
        "Total Invested": f"\u20a1{total_invested/1000:.0f}k",
    }

def run_all_simulations(
    initial_price: float,
    annual_growth_rate: float,
    amplitude: float,
    frequency: float,
    num_years: int,
    trading_days_per_year: int = 252,
    base_amount: float = 10000.0,
):
    """Runs simulations for all defined AAVC strategies."""
    num_trading_days = num_years * trading_days_per_year
    
    print("\n--- AAVC Strategy Comparison Simulation ---")
    print(f"Price Model: Initial={initial_price}, Growth={annual_growth_rate*100}%, Amplitude={amplitude*100}%, Frequency={frequency*trading_days_per_year} cycles/year")
    print(f"Simulation Period: {num_years} years ({num_trading_days} days)")
    print(f"Base Investment Amount: {base_amount}")
    print("----------------------------------------------------------")

    # Generate a single price path for all strategies to use
    price_path = generate_deterministic_price_path(
        initial_price,
        annual_growth_rate,
        amplitude,
        frequency,
        num_trading_days,
        trading_days_per_year,
    )
    
    # Create dummy dates for the simulation
    start_date = date(2020, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_trading_days)]

    # --- Define Strategies and their Parameters to Test ---
    strategies_to_test = [
        (AAVCStaticStrategy(), {"ref_price": initial_price}),
        (AAVCDynamicStrategy(), {"ref_price_reset_threshold": 1.5, "ref_price_reset_factor": 0.9}),
        (AAVCMovingAverageStrategy(), {"window_size": 50}),
        (AAVCMovingAverageStrategy(), {"window_size": 200}),
        (AAVCHighestPriceResetStrategy(), {"reset_factor": 0.85}),
        (AAVCHighestPriceResetStrategy(), {"reset_factor": 0.95}),
    ]

    results = []
    for strategy_instance, params in strategies_to_test:
        result = run_strategy_simulation(
            strategy=strategy_instance,
            strategy_params=params,
            price_path=price_path,
            dates=dates,
            base_amount=base_amount,
            num_years=num_years,
            trading_days_per_year=trading_days_per_year,
        )
        results.append(result)
    
    # --- Print Results Table ---
    print("\nResults:")
    # Header
    header = "| Strategy                       | Params                  | Final Value | Ann. Return | Sharpe Ratio | Total Invested |"
    print(header)
    print("|:-------------------------------|:------------------------|:------------|:------------|:-------------|:---------------|")
    
    # Rows
    for row in results:
        strategy_name = row['Strategy'].ljust(30)
        params_str = str(row['Parameters']).ljust(23)
        final_value = row['Final Value'].ljust(11)
        ann_return = row['Ann. Return'].ljust(11)
        sharpe_ratio = row['Sharpe Ratio'].ljust(12)
        total_invested = row['Total Invested'].ljust(14)
        print(f"| {strategy_name} | {params_str} | {final_value} | {ann_return} | {sharpe_ratio} | {total_invested} |")
        
    print("-----------------------------------------------------------------------------------------------------------------")


if __name__ == "__main__":
    # --- Scenario 1: Stagnant Market ---
    print("\n==========================================================")
    print("Running Scenario 1: Stagnant Market (0% growth)")
    print("==========================================================")
    run_all_simulations(
        initial_price=100.0,
        annual_growth_rate=0.0,
        amplitude=0.20,
        frequency=1/60,
        num_years=5,
    )

    # --- Scenario 2: Declining Market ---
    print("\n==========================================================")
    print("Running Scenario 2: Declining Market (-5% growth)")
    print("==========================================================")
    run_all_simulations(
        initial_price=100.0,
        annual_growth_rate=-0.05,
        amplitude=0.20,
        frequency=1/60,
        num_years=5,
    )