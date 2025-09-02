import numpy as np
from datetime import date, datetime
import sys
import io
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

from src.AAVC_calculate_tool.data_loader import fetch_price_history_by_date
from src.AAVC_calculate_tool.calculator import (
    AAVCStaticStrategy,
    AAVCDynamicStrategy,
    AAVCMovingAverageStrategy,
    AAVCHighestPriceResetStrategy,
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
    """Runs a simulation for a single strategy and returns results."""
    shares_owned = 0.0
    total_invested = 0.0
    portfolio_history = []
    
    if isinstance(strategy, BuyAndHoldStrategy):
        dca_base_amount = strategy_params.get("dca_base_amount", 1000.0)
        num_months = (date_history[-1].year - date_history[0].year) * 12 + date_history[-1].month - date_history[0].month + 1
        strategy_params["initial_amount"] = dca_base_amount * num_months

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
    
    if total_invested > 0 and num_years > 0:
        annual_return = ((final_value / total_invested)**(1/num_years) - 1) * 100
    else:
        annual_return = 0.0

    return {
        "Strategy": strategy.get_metadata().name,
        "Final Value": final_value,
        "Total Invested": total_invested,
        "Ann. Return": annual_return,
    }

def plot_results_boxplot(results_df: pd.DataFrame, metric: str, title: str, filename: str, ylabel: str, y_formatter):
    """Plots and saves a generic boxplot chart comparing strategy performance."""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))

    strategy_groups = results_df.groupby('Strategy')[metric]
    # Sort strategies by median value of the metric
    sorted_strategies = strategy_groups.median().sort_values(ascending=False).index
    
    data = [strategy_groups.get_group(name).values for name in sorted_strategies]
    labels = sorted_strategies

    boxplot = ax.boxplot(data, vert=True, patch_artist=True, tick_labels=labels)

    cmap = plt.colormaps.get_cmap('viridis')
    colors = cmap(np.linspace(0, 1, len(data)))
    for patch, color in zip(boxplot['boxes'], colors):
        patch.set_facecolor(color)

    ax.set_title(title, fontsize=16)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(y_formatter)
    plt.xticks(rotation=45, ha="right")
    
    chart_dir = 'charts'
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    
    filepath = os.path.join(chart_dir, filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    print(f"Chart saved to: {filepath}")

def plot_dataframe_as_table(df: pd.DataFrame, title: str, filename: str, float_format_func):
    """Saves a pandas DataFrame as a table image using matplotlib with custom formatting."""
    plt.style.use('seaborn-v0_8-whitegrid')
    formatted_df = df.copy()
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            formatted_df[col] = df[col].apply(float_format_func)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis('off')

    table = ax.table(
        cellText=formatted_df.values,
        colLabels=formatted_df.columns,
        rowLabels=formatted_df.index,
        cellLoc='center',
        loc='center',
        colWidths=[0.15 for x in formatted_df.columns]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    ax.set_title(title, fontsize=16, pad=20)

    chart_dir = 'charts'
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)

    filepath = os.path.join(chart_dir, filename)
    plt.savefig(filepath, bbox_inches='tight', pad_inches=0.2)
    plt.close()
    print(f"Table chart saved to: {filepath}")

def run_rolling_simulation():
    TICKER = "^GSPC"
    SIMULATION_YEARS = 10
    START_YEAR = 2000
    END_YEAR = 2025 # Current year

    all_results = []
    
    last_start_year = END_YEAR - SIMULATION_YEARS
    
    # Generate quarterly start dates
    start_dates = pd.date_range(start=f'{START_YEAR}-01-01', end=f'{last_start_year}-12-31', freq='3MS')

    print(f"Running {len(start_dates)} rolling 10-year simulations with a 3-month step...")

    for start_date_dt in start_dates:
        start_date_str = start_date_dt.strftime('%Y-%m-%d')
        end_date_dt = start_date_dt + pd.DateOffset(years=10) - pd.DateOffset(days=1)
        end_date_str = end_date_dt.strftime('%Y-%m-%d')
        
        print(f"\n--- Running Simulation for: {start_date_str} to {end_date_str} ---")
        
        try:
            price_history, date_str_history = fetch_price_history_by_date(TICKER, start_date_str, end_date_str)
            if not price_history:
                print(f"No data for period. Skipping.")
                continue
            date_history = [datetime.strptime(d, "%Y-%m-%d").date() for d in date_str_history]
        except Exception as e:
            print(f"Failed to load data for period: {e}. Skipping.")
            continue

        ref_price = price_history[0]
        base_investment = 1000.0

        strategies_to_test = [
            (AAVCStaticStrategy(), {"ref_price": ref_price, "base_amount": base_investment, "investment_frequency": "monthly"}),
            (AAVCDynamicStrategy(), {"ref_price": ref_price, "base_amount": base_investment, "investment_frequency": "monthly"}),
            (AAVCMovingAverageStrategy(), {"base_amount": base_investment, "investment_frequency": "monthly"}),
            (AAVCHighestPriceResetStrategy(), {"base_amount": base_investment, "investment_frequency": "monthly"}),
            (DCAStrategy(), {"base_amount": base_investment, "investment_frequency": "monthly"}),
            (BuyAndHoldStrategy(), {"dca_base_amount": base_investment, "investment_frequency": "monthly"}),
        ]

        for strategy_instance, params in strategies_to_test:
            result = run_strategy_simulation(
                strategy=strategy_instance, 
                strategy_params=params, 
                price_history=price_history, 
                date_history=date_history
            )
            period_str = f"{start_date_dt.year}Q{start_date_dt.quarter}"
            result['Period'] = period_str
            all_results.append(result)

    if not all_results:
        print("No simulations were successfully run. Exiting.")
        return

    results_df = pd.DataFrame(all_results)
    print("\n--- Analysis Complete ---")
    print("Analysis charts and CSV files have been saved in the 'charts' directory.")

    # --- Analysis & Plotting for Final Value ---
    stats_value_df = results_df.groupby('Strategy')['Final Value'].agg(['mean', 'median', 'min', 'max', 'std']).sort_values(by='median', ascending=False)
    stats_value_df.to_csv('charts/rolling_simulation_stats_value.csv')
    plot_dataframe_as_table(
        stats_value_df,
        title=f'Statistical Analysis of Final Portfolio Value\n(10-Year Rolling Simulations, Quarterly, {START_YEAR}-{last_start_year})',
        filename='rolling_simulation_stats_value_table.png',
        float_format_func=lambda x: f'${x:,.0f}'
    )
    plot_results_boxplot(
        results_df,
        metric='Final Value',
        title=f'Distribution of Final Portfolio Value\n(10-Year Rolling Simulations, Quarterly, {START_YEAR}-{last_start_year})',
        filename='rolling_simulation_final_value_boxplot.png',
        ylabel='Final Value (USD)',
        y_formatter=mticker.StrMethodFormatter('${x:,.0f}')
    )

    # --- Analysis & Plotting for Annual Return ---
    stats_return_df = results_df.groupby('Strategy')['Ann. Return'].agg(['mean', 'median', 'min', 'max', 'std']).sort_values(by='median', ascending=False)
    stats_return_df.to_csv('charts/rolling_simulation_stats_return.csv')
    plot_dataframe_as_table(
        stats_return_df,
        title=f'Statistical Analysis of Annual Return\n(10-Year Rolling Simulations, Quarterly, {START_YEAR}-{last_start_year})',
        filename='rolling_simulation_stats_return_table.png',
        float_format_func=lambda x: f'{x:.2f}%'
    )
    plot_results_boxplot(
        results_df,
        metric='Ann. Return',
        title=f'Distribution of Annual Return\n(10-Year Rolling Simulations, Quarterly, {START_YEAR}-{last_start_year})',
        filename='rolling_simulation_return_boxplot.png',
        ylabel='Annual Return (%)',
        y_formatter=mticker.PercentFormatter(xmax=100, decimals=1)
    )


if __name__ == "__main__":
    run_rolling_simulation()

