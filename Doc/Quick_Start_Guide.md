# Quick Start Guide

## Welcome to AAVC Calculate Tool!

This guide will help you get started with the AAVC Calculate Tool in just a few minutes. You'll learn how to calculate investment amounts using the AAVC algorithm for your favorite stocks.

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

## Step 2: Your First Calculation

Let's start with a simple example - calculating the investment amount for Apple (AAPL).

### Basic Command

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000
```

**What this does:**
- `calc`: Tells the tool to calculate investment amounts
- `--ticker "AAPL"`: Specifies Apple's stock symbol
- `--amount 10000`: Sets your base investment amount to 10,000 JPY

### Understanding the Output

After running the command, you'll see something like:

```
--- Calculation Result ---
Ticker: AAPL
Date: 2025-08-16
Investment Amount: JPY 4052
--------------------------
```

**What this means:**
- The AAVC algorithm calculated that you should invest **4,052 JPY** today
- This is less than your base amount (10,000 JPY) because Apple's stock price is currently above the reference price
- The algorithm automatically adjusts your investment based on market conditions

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
