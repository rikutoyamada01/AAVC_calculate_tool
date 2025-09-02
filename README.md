# AAVC Calculate Tool

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python version">
</p>

A tool to calculate daily investment amounts based on the **Asymmetric Volatility-Adjusted Cost Average (AAVC)** algorithm.

## Features

- **Core Calculation Engine**: Implements the AAVC algorithm and supports multiple investment algorithms.
- **Command-Line Interface (CLI)**: Provides a 'calc' subcommand to calculate daily investment amounts.
- **Algorithm Comparison Mode**: Allows comparison of results from multiple algorithms side-by-side.
- **Automatic Data Acquisition**: Fetches the latest stock/fund data automatically using yfinance.
- **Configuration Management**: Manages your portfolio and parameters via a simple YAML configuration file.
- **Monthly Email Notifications**: Automatically calculates the investment amount for a pre-configured stock and sends a summary report to your email once a month. Requires setup.
- **Backtesting (Planned)**: Simulate and evaluate the strategy's performance on historical data.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone <repository_url>
cd AAVC_calculate_tool
```

### Step 2: Set Up Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install in development mode (recommended for development)
pip install -e .

# Or install with development tools
pip install .[dev]

# Alternative: Install from requirements.txt
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Check if the tool is working
python -m AAVC_calculate_tool --help
```

## Usage

### Basic Commands

The tool provides a command-line interface with the following subcommands:

```bash
python -m AAVC_calculate_tool [subcommand] [options]
```

Available subcommands:
- `calc`: Calculate investment amounts
- `backtest`: Run backtesting (planned feature)

### Run Backtesting

Run a backtest comparison for AAVC, DCA, and Buy & Hold strategies.

```bash
python -m AAVC_calculate_tool backtest \
  --ticker <TICKER_SYMBOL> \
  --start-date <YYYY-MM-DD> \
  --end-date <YYYY-MM-DD> \
  --amount <BASE_AMOUNT> \
  [--algorithms <ALGO1,ALGO2,...>] \
  [--algorithm-params <ALGO:PARAM=VAL,...>] \
  [--compare-mode <simple|detailed>] \
  [--plot] \
  [--investment-frequency <daily|monthly>]
```

**Options:**
- `--ticker, -t`: Required. Ticker symbol for backtest.
- `--start-date`: Required. Start date for backtest (YYYY-MM-DD).
- `--end-date`: Required. End date for backtest (YYYY-MM-DD).
- `--amount, -a`: Required. Base investment amount.
- `--algorithms`: Optional. Comma-separated list of algorithms to compare (e.g., `aavc,dca,buy_and_hold`). Defaults to all registered algorithms.
- `--algorithm-params`: Optional. Algorithm-specific parameters (e.g., `aavc:ref_price=100,dca:base_amount=200`).
- `--compare-mode`: Optional. Comparison display mode (`simple` or `detailed`). Default is `simple`.
- `--plot`: Optional. Generate and save comparison chart.
- `--investment-frequency`: Optional. Investment frequency (`daily` or `monthly`). Default is `monthly`.

**Examples:**
```bash
# Basic backtest for AAPL
python -m AAVC_calculate_tool backtest --ticker "AAPL" --start-date "2020-01-01" --end-date "2023-12-31" --amount 10000

# Backtest with specific algorithms and detailed comparison
python -m AAVC_calculate_tool backtest --ticker "MSFT" --start-date "2021-01-01" --end-date "2024-01-01" --amount 5000 --algorithms aavc,dca --compare-mode detailed

# Backtest with plotting and daily investment frequency
python -m AAVC_calculate_tool backtest --ticker "GOOGL" --start-date "2022-01-01" --end-date "2023-06-30" --amount 20000 --plot --investment-frequency daily
```

### Calculate Investment Amounts

#### Single Stock Calculation

Calculate the investment amount for a single stock:

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000
```

**Options:**
- `--ticker, -t`: Stock ticker symbol (e.g., AAPL, SPY, 7203.T)
- `--amount, -a`: Base investment amount (required)
- `--ref-price, -r`: Reference price (optional, uses oldest historical price if not specified)
- `--log-file`: Custom log file path (optional, defaults to `investment_log.csv`)
- `--ref-ma-period`: Period for moving average reference price (optional, defaults to 200)

**Examples:**
```bash
# Basic calculation
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000

# With custom reference price
python -m AAVC_calculate_tool calc --ticker "SPY" --amount 5000 --ref-price 400.0

# With custom log file
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000 --log-file my_portfolio.csv
```

#### Multiple Algorithm Calculation and Comparison

Calculate and compare investment amounts using multiple algorithms:

```bash
python -m AAVC_calculate_tool calc --ticker "SPY" --amount 10000 --algorithms AAVC,SMA --algorithm-params '{"SMA": {"period": 50}}' --compare-mode
```

**Options:**
- `--algorithms`: Comma-separated list of algorithm names to use (e.g., `AAVC,SMA`)
- `--algorithm-params`: JSON string of parameters for each algorithm (e.g., `'{"SMA": {"period": 50}}'`)
- `--compare-mode`: Enable comparison output for multiple algorithms

**Example:**
```bash
# Compare AAVC and SMA for SPY with custom SMA period
python -m AAVC_calculate_tool calc --ticker "SPY" --amount 10000 --algorithms AAVC,SMA --algorithm-params '{"SMA": {"period": 50}}' --compare-mode
```

#### Batch Calculation from Configuration File

Calculate investment amounts for multiple stocks defined in a configuration file:

```bash
python -m AAVC_calculate_tool calc --config config.yaml
```

**Options:**
- `--config, -c`: Path to YAML configuration file (required)
- `--log-file`: Custom log file path (optional, defaults to `investment_log.csv`)

**Example:**
```bash
python -m AAVC_calculate_tool calc --config my_portfolio.yaml --log-file portfolio_log.csv
```

### Configuration File (config.yaml)

The tool can process multiple investment jobs defined in a YAML configuration file (e.g., `config.yaml`). This file allows you to define global settings and specific parameters for each ticker.

**Example `config.yaml` structure:**

```yaml
# 全体に適用するデフォルト設定
default_settings:
  base_amount: 10000
  asymmetric_coefficient: 2.0 # Optional: Defaults to 2.0 if not specified.

# 銘柄ごとの設定
stocks:
  - ticker: "SPY" # Ticker symbol (required)
    base_amount: 2000 # Optional: Overrides default_settings.base_amount for this ticker.
    # reference_price: (Optional: If omitted, uses the oldest price from history)
    # asymmetric_coefficient: (Optional: Overrides default_settings.asymmetric_coefficient for this ticker)
```

**Key parameters:**

-   `default_settings`:
    -   `base_amount`: (Required) The default base investment amount for all stocks.
    -   `asymmetric_coefficient`: (Optional) The asymmetric coefficient used in the AAVC calculation. **Defaults to `2.0` if not specified.**
-   `stocks`: A list of individual stock configurations. Each item can have:
    -   `ticker`: (Required) The ticker symbol for the asset.
    -   `base_amount`: (Optional) Overrides the `default_settings.base_amount` for this specific ticker.
    -   `reference_price`: (Optional) The reference price for the calculation. If omitted, the oldest price from the fetched history will be used.
    -   `asymmetric_coefficient`: (Optional) Overrides the `default_settings.asymmetric_coefficient` for this specific ticker.

### Investment Logging

The tool can automatically log each investment calculation to a CSV file. By default, the log is saved to `investment_log.csv` in the current directory.

You can specify a different log file path using the `--log-file` argument:

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000 --log-file my_custom_log.csv
```

The log file will contain the following columns: `date`, `ticker`, `base_amount`, `reference_price`, and `calculated_investment`. If the file does not exist, a header row will be added automatically.

<details>
<summary><b>AAVCアルゴリズムの詳細 (Click to expand)</b></summary>

### AAVCアルゴリズムとは？

AAVCは、**非対称ボラティリティ調整型ドルコスト平均法(Asymmetric Volatility-Adjusted Cost Average)** の略称です。これは、従来のドルコスト平均平均法をさらに進化させた投資アルゴリズムです。

従来のドルコスト平均法は、株価の変動に関わらず**常に一定額**を投資します。これにより、株価が高いときには少ない株数を、低いときには多い株数を購入し、平均購入価格を平準化する効果があります。

一方、AAVCアルゴリズムは、この「常に一定額」というルールを、**市場の状況に応じて変化させる**のが大きな特徴です。

### 仕組み

AAVCは、以下の3つの要素を組み合わせて投資額を調整します。

1.  **基準価格からの乖離率**:
    *   現在の株価が、事前に設定した**基準価格**からどれだけ離れているかを計算します。
    *   株価が基準価格より下落していれば、**投資額を増やします**。逆に、基準価格より上昇していれば、**投資額を減らします**。

2.  **非対称性係数**:
    *   株価が下落したときだけ、投資額を増やす効果を**さらに加速**させます。例えば、株価が10%下落した場合、ただ投資額を増やすだけでなく、その効果を2倍にするなど、下落局面に積極的に対応します。これが「非対称（Asymmetric）」と呼ばれる理由です。

3.  **ボラティリティ（変動幅）**:
    *   株価の変動が大きい（ボラティリティが高い）市場では、投資額の調整幅を大きくします。これにより、変動の激しい相場でも効果的に株価下落時の買い増しや上昇時の買い控えを行うことができます。

### まとめ

AAVCアルゴリズムは、ただ機械的に買い続けるのではなく、**株価の下落時に強く、上昇時には控えめに投資額を調整する**ことで、より効率的な資産形成を目指すための戦略です。特に、長期的な下落局面で効果を発揮するように設計されています。

</details>

## Documentation

The AAVC Calculate Tool provides comprehensive documentation to help users and developers get the most out of the tool.

### 📚 Documentation Structure

#### 🚀 Getting Started
- **[Quick Start Guide](Doc/Quick_Start_Guide.md)** - Get up and running in minutes
- **[AAVC Deep Dive Manual](Doc/AAVC_Deep_Dive_Manual.md)** - Comprehensive guide to the AAVC algorithm
- **[README](README.md)** - Main project overview and user guide (this file)

#### 📋 Specifications
- **[CLI Specification](Doc/01_CLI_Specification.md)** - Command-line interface overview
- **[Data Acquisition](Doc/02_Data_Acquisition.md)** - Data fetching and validation
- **[Configuration and Logging](Doc/03_Configuration_and_Logging.md)** - Settings and logging
- **[Backtesting](Doc/04_Backtesting.md)** - Strategy testing (planned feature)
- **[Backtest Comparison](Doc/05_Backtest_Comparison.md)** - Performance analysis (planned feature)

#### 🔧 Technical Details
- **[CLI Detailed Design](Doc/01_CLI_Detailed_Design.md)** - CLI implementation details
- **[Data Acquisition Detailed Design](Doc/02_Data_Acquisition_Detailed_Design.md)** - Data handling architecture
- **[Configuration and Logging Detailed Design](Doc/03_Configuration_and_Logging_Detailed_Design.md)** - Configuration system design
- **[Backtesting Detailed Design](Doc/04_Backtesting_Detailed_Design.md)** - Backtesting implementation (planned)
- **[Backtest Comparison Detailed Design](Doc/05_Backtest_Comparison_Detailed_Design.md)** - Comparison system design (planned)

#### 👨‍💻 Developer Resources
- **[Developer Guide](Doc/Developer_Guide.md)** - Comprehensive development information
- **[API Reference](Doc/API_Reference.md)** - Complete API documentation

### 🎯 Choose Your Path

#### For New Users
1. Start with the **[Quick Start Guide](Doc/Quick_Start_Guide.md)**
2. Read this **[README](README.md)** for comprehensive information
3. Refer to **[Configuration and Logging](Doc/03_Configuration_and_Logging.md)** for setup details

#### For Regular Users
1. Use **[CLI Specification](Doc/01_CLI_Specification.md)** for command reference
2. Check **[Data Acquisition](Doc/02_Data_Acquisition.md)** for supported tickers
3. Review **[Configuration and Logging](Doc/03_Configuration_and_Logging.md)** for advanced features

#### For Developers
1. Begin with **[Developer Guide](Doc/Developer_Guide.md)** for setup and architecture
2. Use **[API Reference](Doc/API_Reference.md)** for detailed function documentation
3. Review detailed design documents for implementation insights

### 📖 Complete Documentation Index

For a complete overview of all available documentation, see the **[Documentation Index](Doc/Documentation_Index.md)**.

## Troubleshooting

## Feature: Monthly Email Notifications

This tool includes a feature to automatically run a calculation once a month and send the results to you via email. This is powered by GitHub Actions and is useful for receiving timely investment information without needing to run the tool manually.

### How to Enable and Configure

To use this feature, you must configure several "Secrets" in your GitHub repository. This ensures that your sensitive information (like email passwords) is kept secure.

**Step 1: Navigate to GitHub Secrets**

1.  Go to your repository on GitHub.
2.  Click on the **Settings** tab.
3.  In the left sidebar, click **Secrets and variables** > **Actions**.
4.  Click the **New repository secret** button for each of the secrets listed below.

**Step 2: Add the Following Secrets**

| Secret Name     | Description                                                                                                | Example                     |
| :-------------- | :--------------------------------------------------------------------------------------------------------- | :-------------------------- |
| `MAIL_SERVER`   | The address of your email provider's SMTP server.                                                          | `smtp.gmail.com`            |
| `MAIL_PORT`     | The port for the SMTP server. TLS is recommended.                                                          | `587`                       |
| `MAIL_USERNAME` | Your full email address, used to log in to the SMTP server.                                                | `your.email@gmail.com`      |
| `MAIL_PASSWORD` | The password for your email account. **For Gmail, you must use an [App Password](https://support.google.com/accounts/answer/185833).** | `abdc efgh ijkl mnop`       |
| `MAIL_TO`       | The email address where the notification should be sent.                                                   | `recipient.email@example.com` |

**Note:** Without these secrets, the monthly action will fail.

### Customization

-   **Ticker and Amount**: The stock ticker and base investment amount can be changed by editing the configuration variables at the top of the `src/AAVC_calculate_tool/notification_sender.py` file. The defaults are `QQQ` and `$10,000`.
-   **Schedule**: The schedule is defined in `.github/workflows/monthly_notification.yml` using a cron expression. The default is the 1st of every month.

### Manual Testing

After setting up the secrets, you can test the feature without waiting for the schedule:
1. Go to the **Actions** tab in your GitHub repository.
2. In the left sidebar, click on the **Monthly Investment Notification** workflow.
3. Click the **Run workflow** dropdown, and then the **Run workflow** button. This will trigger the process manually.

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'AAVC_calculate_tool.recorder'
```

**Solution:**
Install the package in development mode:
```bash
pip install -e .
```

#### 2. Unrecognized Arguments Error

**Error:**
```
__main__.py: error: unrecognized arguments: --log-file my_custom_log.csv
```

**Solution:**
Ensure the package is properly installed and you're using the correct command syntax.

#### 3. Data Fetching Issues

**Error:**
```
Error: No historical data found for [TICKER]
```

**Solution:**
- Verify the ticker symbol is correct
- Check your internet connection
- Some tickers may not be available on Yahoo Finance

#### 4. Configuration File Errors

**Error:**
```
Error: Could not parse configuration file
```

**Solution:**
- Verify YAML syntax is correct
- Check that required fields are present
- Ensure file encoding is UTF-8

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/your-repo/AAVC_calculate_tool/issues) page
2. Create a new issue with:
   - Error message
   - Command used
   - Python version
   - Operating system

## Dependencies

This project relies on the following Python libraries:

### Core Dependencies

These are required to run the main functionalities of the tool:

-   `numpy`: For numerical operations, especially in the AAVC calculation.
-   `yfinance`: To fetch historical stock and fund data from Yahoo Finance.
-   `PyYAML`: To parse and load configuration files in YAML format.

### Development Dependencies

These are required for development, testing, and maintaining code quality:

-   `black`: Code formatter.
-   `ruff`: Linter for code style and quality checks.
-   `mypy`: Static type checker.
-   `isort`: For sorting import statements.
-   `pytest`: Testing framework.
-   `matplotlib`: For generating plots and charts in backtesting results.

You can install all core dependencies using `pip install -r requirements.txt`.
To install all development dependencies (including core dependencies), use `pip install .[dev]` from the project root.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our coding standards and how to get started.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.
