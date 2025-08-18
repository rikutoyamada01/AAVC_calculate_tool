import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from .backtester import ComparisonResult


def plot_multi_algorithm_chart(
    comparison_result: ComparisonResult,
    output_filename: str = "multi_algorithm_comparison_chart.png"
) -> str:
    """複数アルゴリズムの比較チャートを生成"""

    results = comparison_result.results
    algorithm_names = list(results.keys())

    # Set up the plot
    plt.figure(figsize=(12, 8))

    # Define colors for each strategy dynamically
    colors = plt.cm.get_cmap('tab10', len(algorithm_names))

    # Plot each strategy
    for i, (strategy_name, result) in enumerate(results.items()):
        # Convert dates to datetime objects for plotting
        dates = [datetime.combine(d, datetime.min.time()) for d in result.dates]

        plt.plot(
            mdates.date2num(dates),
            result.portfolio_history,
            label=strategy_name,
            color=colors(i),
            linewidth=2
        )

    # Customize the plot
    plt.title(
        'Multi-Algorithm Backtest Comparison',
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
    plt.gca().yaxis.set_major_formatter(FuncFormatter(
        lambda x, _: f'¥{int(x):,}'  # Format as Japanese Yen
    ))

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the chart
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

    return output_filename
