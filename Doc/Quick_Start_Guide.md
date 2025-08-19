# Quick Start Guide

## はじめに

このガイドでは、AAVC Calculate Tool の使用方法を短時間で習得できます。複数の投資アルゴリズムを比較し、お気に入りの銘柄に対する投資額を計算する方法を学びます。

## What You'll Learn

- How to install the tool
- How to calculate investment amounts for a single stock
- How to set up a portfolio configuration
- How to log your investment calculations

## Prerequisites

Before you begin, make sure you have:

- Python 3.8 or higher installed
- Internet connection (for fetching stock data)
- Basic familiarity with command line tools

## Step 1: Installation

### Option A: Quick Install (Recommended)

```bash
# Clone the repository
git clone <repository_url>
cd AAVC_calculate_tool

# Install in development mode
pip install -e .
```

### Option B: From Requirements

```bash
# Clone the repository
git clone <repository_url>
cd AAVC_calculate_tool

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
python -m AAVC_calculate_tool --help
```

You should see the help message with available commands.

## 基本的な使い方

Let's start with a simple example - calculating the investment amount for Apple (AAPL).

### Basic Command

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000
```

**What this does:**
- `calc`: Tells the tool to calculate investment amounts
- `--ticker "AAPL"`: Specifies Apple's stock symbol
- `--amount 10000`: Sets your base investment amount to 10,000 JPY

### 複数のアルゴリズムを比較する

複数の投資アルゴリズムを比較して、最適な戦略を見つけることができます。

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000 --algorithms AAVC,SMA --algorithm-params '{"SMA": {"period": 20}}' --compare-mode
```

**What this does:**
- `--algorithms AAVC,SMA`: AAVCとSMAの2つのアルゴリズムを比較します。
- `--algorithm-params '{"SMA": {"period": 20}}'`: SMAアルゴリズムに`period=20`というパラメータを渡します。
- `--compare-mode`: 比較モードを有効にし、各アルゴリズムの結果を並べて表示します。

### アルゴリズムのパラメータを指定する

各アルゴリズムに固有のパラメータを渡すことができます。

```bash
python -m AAVC_calculate_tool calc --ticker "GOOG" --amount 5000 --asymmetric-coefficient 2.5 --max-multiplier 4.0
```

**What this does:**
- `--ticker "GOOG"`: Googleのティッカーシンボルを指定します。
- `--amount 5000`: 基準投資額を5000 JPYに設定します。
- `--asymmetric-coefficient 2.5`: AAVCアルゴリズムの非対称係数を2.5に設定します。
- `--max-multiplier 4.0`: AAVCアルゴリズムの最大投資額の基準額に対する倍率を4.0に設定します。
- `--ref-ma-period 50`: 基準価格として50日移動平均を使用します。

### S&P 500指数を用いた現実的な例

S&P 500指数に連動するETFであるSPYを対象に、AAVCアルゴリズムとSMA（単純移動平均）アルゴリズムを比較しながら投資額を計算する例です。基準投資額を10,000 JPYとし、SMAアルゴリズムの期間を50日としています。

```bash
python -m AAVC_calculate_tool calc --ticker "SPY" --amount 10000 --algorithms AAVC,SMA --algorithm-params '{"SMA": {"period": 50}}' --compare-mode
```

**What this does:**
- `--ticker "SPY"`: S&P 500指数に連動するETFであるSPYを対象とします。
- `--amount 10000`: 基準投資額を10,000 JPYに設定します。
- `--algorithms AAVC,SMA`: AAVCアルゴリズムとSMAアルゴリズムの両方を使用して投資額を計算します。
- `--algorithm-params '{"SMA": {"period": 50}}'`: SMAアルゴリズムに`period=50`というパラメータ（50日移動平均）を渡します。
- `--compare-mode`: 各アルゴリズムの計算結果を並べて表示し、比較しやすくします。


### 出力結果

After running the command, you'll see something like:

```
--- Calculation Result ---
Ticker: AAPL
Date: 2025-08-16
Algorithm: AAVC
Investment Amount: JPY 4052
--------------------------

--- Comparison Result ---
Ticker: AAPL
Date: 2025-08-16
AAVC Investment Amount: JPY 4052
SMA Investment Amount: JPY 5000
--------------------------
```

**What this means:**
- 単一アルゴリズムの場合、指定されたアルゴリズムが計算した投資額が表示されます。
- 比較モードの場合、各アルゴリズムが計算した投資額が並べて表示され、異なる戦略の結果を簡単に比較できます。
- アルゴリズムは、市場の状況に基づいて投資額を自動的に調整します。

## Step 3: Customize Your Calculation

### Set a Custom Reference Price

If you want to use a specific price as your reference point:

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000 --ref-price 150.0
```

**When to use this:**
- You want to compare against a specific historical price
- You're tracking performance from a particular date
- You want to set your own baseline

### Use a Custom Log File

Save your calculations to a specific file:

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000 --log-file my_apple_investments.csv
```

**Benefits:**
- Keep track of all your AAPL investments
- Separate logs for different stocks or strategies
- Easy to analyze your investment history

## Step 4: Create a Portfolio Configuration

Instead of calculating one stock at a time, you can set up a configuration file to manage multiple stocks.

### Create a Configuration File

Create a file named `my_portfolio.yaml`:

```yaml
# Default settings for all stocks
default_settings:
  base_amount: 10000
  asymmetric_coefficient: 2.0

# Individual stock configurations
stocks:
  - ticker: "AAPL"
    base_amount: 8000
  
  - ticker: "SPY"
    base_amount: 12000
    reference_price: 400.0
  
  - ticker: "7203.T"  # Toyota (Japanese stock)
    base_amount: 6000
```

### Run Portfolio Calculation

```bash
python -m AAVC_calculate_tool calc --config my_portfolio.yaml
```

**What happens:**
- The tool processes all stocks in your configuration
- Each calculation uses the specified parameters
- Results are logged to the default log file (`investment_log.csv`)

## Step 5: Understanding the AAVC Algorithm

### How It Works

The AAVC algorithm automatically adjusts your investment amount based on:

1. **Price Movement**: If the stock price goes down, you invest more. If it goes up, you invest less.

2. **Volatility**: More volatile stocks get larger adjustments.

3. **Asymmetric Response**: The algorithm is more aggressive when prices fall than when they rise.

### Example Scenarios

#### Scenario 1: Stock Price Drops
- **Base Amount**: 10,000 JPY
- **Current Price**: 20% below reference price
- **Result**: Investment amount increases to ~14,000 JPY
- **Why**: You're buying more when the stock is "on sale"

#### Scenario 2: Stock Price Rises
- **Base Amount**: 10,000 JPY
- **Current Price**: 20% above reference price
- **Result**: Investment amount decreases to ~6,000 JPY
- **Why**: You're buying less when the stock is expensive

## Step 6: Logging and Tracking

### View Your Investment Log

After running calculations, check your log file:

```bash
# View the log file
cat investment_log.csv
```

**Log File Contents:**
```csv
date,ticker,base_amount,reference_price,calculated_investment
2025-08-16,AAPL,10000.0,201.86,4051.57
2025-08-16,SPY,12000.0,400.0,1358.42
2025-08-16,7203.T,6000.0,2500.0,4800.0
```

### Custom Log Files

Use different log files for different purposes:

```bash
# Monthly logs
python -m AAVC_calculate_tool calc --config portfolio.yaml --log-file august_2025.csv

# Stock-specific logs
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000 --log-file apple_log.csv
```

## Step 7: Advanced Features

### Adjust Asymmetric Coefficient

The asymmetric coefficient controls how aggressively the algorithm responds to price changes:

```yaml
default_settings:
  base_amount: 10000
  asymmetric_coefficient: 3.0  # More aggressive (default is 2.0)
```

**Coefficient Values:**
- **1.0**: No asymmetric adjustment (like regular dollar-cost averaging)
- **2.0**: Standard asymmetric adjustment (default)
- **3.0**: More aggressive adjustment
- **Higher values**: More aggressive response to price drops

### Multiple Reference Prices

Set different reference prices for different stocks:

```yaml
stocks:
  - ticker: "AAPL"
    base_amount: 8000
    reference_price: 150.0  # Custom reference price
  
  - ticker: "SPY"
    base_amount: 12000
    # No reference_price - uses oldest historical price
```

## Common Use Cases

### Daily Investment Planning

```bash
# Run this every morning to plan your investments
python -m AAVC_calculate_tool calc --config daily_portfolio.yaml --log-file daily_log.csv
```

### Portfolio Rebalancing

```bash
# Check if you need to adjust your portfolio
python -m AAVC_calculate_tool calc --config rebalance_portfolio.yaml
```

### Research and Analysis

```bash
# Test different parameters
python -m AAVC_calculate_tool calc --ticker "SPY" --amount 10000 --ref-price 350.0
```

## Troubleshooting

### Common Issues

#### "Ticker not found" Error
- Check the ticker symbol spelling
- Some international stocks need country suffixes (e.g., 7203.T for Toyota)
- Verify the stock is available on Yahoo Finance

#### "No historical data found" Error
- Check your internet connection
- Some stocks may have limited data availability
- Try a different ticker symbol

#### Configuration File Errors
- Ensure YAML syntax is correct
- Check that required fields are present
- Verify file encoding is UTF-8

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting section](../README.md#troubleshooting) in the main README
2. Review the [API Reference](07_API_Reference.md) for detailed information
3. Check the [GitHub Issues](https://github.com/your-repo/AAVC_calculate_tool/issues) page

## Next Steps

Now that you're comfortable with the basics:

1. **Explore More Stocks**: Try different ticker symbols and see how the algorithm responds
2. **Customize Your Portfolio**: Create a configuration file that matches your investment strategy
3. **Track Performance**: Use log files to monitor your investment decisions over time
4. **Learn Advanced Features**: Read the [Developer Guide](06_Developer_Guide.md) for more technical details

## Example Workflow

Here's a complete example of a typical investment session:

```bash
# 1. Check your portfolio
python -m AAVC_calculate_tool calc --config my_portfolio.yaml --log-file today_investments.csv

# 2. Review the results
cat today_investments.csv

# 3. Make investment decisions based on the calculated amounts
# 4. Repeat tomorrow with updated data
```

## Summary

You've successfully:
- ✅ Installed the AAVC Calculate Tool
- ✅ Calculated your first investment amount
- ✅ Created a portfolio configuration
- ✅ Learned how the AAVC algorithm works
- ✅ Set up logging and tracking

The tool is now ready to help you make informed investment decisions using the AAVC algorithm. Happy investing!

---

**Need more help?** Check out the [full documentation](../README.md) or [API reference](07_API_Reference.md) for detailed information. 
