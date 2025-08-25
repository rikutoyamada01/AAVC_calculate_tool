import numpy as np
from datetime import date, datetime
import sys
import io
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from src.AAVC_calculate_tool.data_loader import fetch_price_history_by_date
from src.AAVC_calculate_tool.calculator import (
    AAVCStaticStrategy,
    DCAStrategy,
    BuyAndHoldStrategy,
    BaseAlgorithm,
)

# Set default encoding for stdout to UTF-8
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def run_strategy_simulation(
    strategy: BaseAlgorithm,
    strategy_params: dict,
    price_history: list[float],
    date_history: list[date],
) -> dict:
    """Runs a simulation for a single strategy and returns results including portfolio history."""
    shares_owned = 0.0
    total_invested = 0.0
    portfolio_history = []
    
    if isinstance(strategy, BuyAndHoldStrategy):
        dca_base_amount = strategy_params.get("dca_base_amount", 1000.0)
        num_investments = len(set(d.strftime("%Y-%m") for d in date_history))
        strategy_params["initial_amount"] = dca_base_amount * num_investments

    for i in range(len(price_history)):
        current_price = price_history[i]
        investment_amount = strategy.calculate_investment(
            current_price=current_price,
            price_history=price_history[:i+1],
            date_history=date_history[:i+1],
            parameters=strategy_params,
        )
        if investment_amount > 0:
            shares_bought = investment_amount / current_price
            shares_owned += shares_bought
            total_invested += investment_amount
        portfolio_value = shares_owned * current_price
        portfolio_history.append(portfolio_value)

    final_value = portfolio_history[-1] if portfolio_history else 0.0
    num_years = (date_history[-1] - date_history[0]).days / 365.25
    annual_return = ((final_value / total_invested)**(1/num_years) - 1) * 100 if total_invested > 0 and num_years > 0 else 0.0

    return {
        "Strategy": strategy.get_metadata().name,
        "Final Value": final_value,
        "Total Invested": total_invested,
        "Ann. Return": annual_return,
        "Final Multiplier": (final_value / total_invested) if total_invested > 0 else 0.0,
        "Portfolio History": portfolio_history,
    }

def plot_scenario_results(date_history, price_history, results, scenario_name, ticker):
    """Plots and saves a chart comparing strategy performance."""
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Plot S&P 500 price on primary y-axis
    ax1.plot(date_history, price_history, color='gray', linestyle='--', alpha=0.7, label=f'{ticker} Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel(f'{ticker} Price (USD)', color='gray')
    ax1.tick_params(axis='y', labelcolor='gray')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Create secondary y-axis for portfolio values
    ax2 = ax1.twinx()
    
    # Plot each strategy's portfolio value
    for result in results:
        ax2.plot(date_history, result['Portfolio History'], label=result['Strategy'])
    
    ax2.set_ylabel('Portfolio Value (USD)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

    # Final touches
    plt.title(f'Investment Strategy Performance: {scenario_name}')
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
    plt.tight_layout()
    
    # Save chart
    chart_dir = 'charts'
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    
    filename = f"{scenario_name.replace(' ', '_').lower()}.png"
    filepath = os.path.join(chart_dir, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"Chart saved to: {filepath}")

def run_historical_scenario(ticker: str, start_date: str, end_date: str, scenario_name: str):
    """Fetches data, runs simulations, and generates plots for a scenario."""
    print(f"\n--- Scenario: {scenario_name} ({ticker}: {start_date} to {end_date}) ---")
    
    try:
        price_history, date_str_history = fetch_price_history_by_date(ticker, start_date, end_date)
        if not price_history:
            print("No data loaded.")
            return
        date_history = [datetime.strptime(d, "%Y-%m-%d").date() for d in date_str_history]
    except Exception as e:
        print(f"Failed to load data for {ticker}: {e}")
        return

    ref_price = price_history[0]
    base_investment = 1000.0

    strategies_to_test = [
        (AAVCStaticStrategy(), {"ref_price": ref_price, "base_amount": base_investment, "investment_frequency": "monthly"}),
        (DCAStrategy(), {"base_amount": base_investment, "investment_frequency": "monthly"}),
        (BuyAndHoldStrategy(), {"dca_base_amount": base_investment, "investment_frequency": "monthly"}),
    ]

    results = []
    for strategy_instance, params in strategies_to_test:
        result = run_strategy_simulation(strategy=strategy_instance, strategy_params=params, price_history=price_history, date_history=date_history)
        results.append(result)

    # Print Results Table
    print("| Strategy      | Final Value   | Total Invested | Ann. Return | Final Multiplier |")
    print("|:--------------|:--------------|:---------------|:------------|:-----------------|")
    for row in results:
        print(f"| {row['Strategy']:<13} | ${row['Final Value']:<12,.0f} | ${row['Total Invested']:<13,.0f} | {row['Ann. Return']:<10.2f}% | {row['Final Multiplier']:<16.2f}x |")
    print("--------------------------------------------------------------------------------")

    # Plot results
    plot_scenario_results(date_history, price_history, results, scenario_name, ticker)

if __name__ == "__main__":
    TICKER = "^GSPC"
    scenarios = {
        "Uptrend Market": ("2016-01-01", "2019-12-31"),
        "Sideways Market": ("2015-01-01", "2016-06-30"),
        "Downtrend Market": ("2007-10-01", "2009-03-31"),
    }
    for name, (start, end) in scenarios.items():
        run_historical_scenario(TICKER, start, end, name)