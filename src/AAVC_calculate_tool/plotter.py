"""
Plotting module for backtest comparison charts.

This module handles the creation of comparison charts showing the performance
of different investment strategies over time.
"""

import os
from typing import Dict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from .backtester import BacktestResult


def plot_comparison_chart(
    results: Dict[str, BacktestResult],
    ticker: str,
    start_date: str,
    end_date: str,
    output_path: str = None
) -> str:
    """
    Create a comparison chart showing portfolio values over time for all strategies.
    
    Args:
        results: Dictionary containing results for all strategies
        ticker: Stock ticker symbol
        start_date: Start date of backtest
        end_date: End date of backtest
        output_path: Output file path (optional)
        
    Returns:
        Path to the saved chart file
    """
    # Set up the plot
    plt.figure(figsize=(12, 8))
    
    # Define colors for each strategy
    colors = {
        "AAVC": "#1f77b4",      # Blue
        "DCA": "#ff7f0e",       # Orange
        "Buy & Hold": "#2ca02c"  # Green
    }
    
    # Plot each strategy
    for strategy_name, result in results.items():
        # Convert dates to datetime objects for plotting
        dates = [datetime.combine(date, datetime.min.time()) for date in result['dates']]
        
        plt.plot(
            dates,
            result['portfolio_history'],
            label=strategy_name,
            color=colors[strategy_name],
            linewidth=2
        )
    
    # Customize the plot
    plt.title(
        f'Portfolio Comparison: {ticker} ({start_date} to {end_date})',
        fontsize=16,
        fontweight='bold'
    )
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Portfolio Value (JPY)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11)
    
    # Format x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    # Format y-axis as currency
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x/1000:.0f}k'))
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Generate output filename if not provided
    if output_path is None:
        output_path = f"backtest_chart_{ticker}_{start_date}_to_{end_date}.png"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Save the chart
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path
