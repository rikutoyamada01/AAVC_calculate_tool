# API Reference

## Overview

This document provides detailed API documentation for all public functions, classes, and modules in the AAVC Calculate Tool.

## Module: calculator

Core AAVC calculation logic implementation.

### Functions

#### `calculate_aavc_investment`

```python
def calculate_aavc_investment(
    price_path: List[float],
    base_amount: float,
    reference_price: float,
    asymmetric_coefficient: float = 2.0
) -> float
```

**Description**: Calculates the investment amount using the AAVC algorithm.

**Parameters**:
- `price_path` (List[float]): Historical price data as a list of floats
- `base_amount` (float): Base investment amount in JPY
- `reference_price` (float): Reference price for comparison
- `asymmetric_coefficient` (float, optional): Asymmetric coefficient. Defaults to 2.0

**Returns**:
- `float`: Calculated investment amount in JPY

**Raises**:
- `ValueError`: If price_path is empty or contains invalid values
- `ValueError`: If base_amount or reference_price is negative

**Example**:
```python
from AAVC_calculate_tool.calculator import calculate_aavc_investment

prices = [100.0, 95.0, 90.0, 85.0]
base_amount = 10000
reference_price = 100.0

investment = calculate_aavc_investment(
    price_path=prices,
    base_amount=base_amount,
    reference_price=reference_price
)
print(f"Investment amount: JPY {investment:.0f}")
```

**Algorithm Details**:
1. Calculates price deviation from reference price
2. Applies volatility adjustment based on price movements
3. Applies asymmetric coefficient for downward price movements
4. Returns adjusted investment amount

---

## Module: data_loader

Data acquisition and validation functionality.

### Functions

#### `fetch_price_history`

```python
def fetch_price_history(ticker: str) -> List[float]
```

**Description**: Fetches historical price data for a given ticker symbol.

**Parameters**:
- `ticker` (str): Stock ticker symbol (e.g., "AAPL", "SPY", "7203.T")

**Returns**:
- `List[float]`: List of historical closing prices in chronological order (oldest first)

**Raises**:
- `TickerNotFoundError`: If the ticker symbol is not found
- `DataFetchError`: If there's an error fetching data from Yahoo Finance

**Example**:
```python
from AAVC_calculate_tool.data_loader import fetch_price_history

try:
    prices = fetch_price_history("AAPL")
    print(f"Retrieved {len(prices)} price points for AAPL")
    print(f"Oldest price: {prices[0]}")
    print(f"Latest price: {prices[-1]}")
except TickerNotFoundError:
    print("Ticker not found")
except DataFetchError as e:
    print(f"Error fetching data: {e}")
```

**Data Source**: Yahoo Finance via yfinance library
**Data Period**: 1 year of daily closing prices
**Currency**: USD (converted to JPY if needed)

---

## Module: config_loader

Configuration file parsing and management.

### Functions

#### `load_config`

```python
def load_config(config_path: str) -> Dict[str, Any]
```

**Description**: Loads and parses a YAML configuration file.

**Parameters**:
- `config_path` (str): Path to the YAML configuration file

**Returns**:
- `Dict[str, Any]`: Parsed configuration dictionary

**Raises**:
- `ConfigNotFoundError`: If the configuration file doesn't exist
- `ConfigParseError`: If the YAML file has syntax errors
- `ConfigError`: If the configuration is invalid

**Configuration Schema**:
```yaml
default_settings:
  base_amount: 10000
  asymmetric_coefficient: 2.0

stocks:
  - ticker: "SPY"
    base_amount: 2000
    reference_price: 400.0
    asymmetric_coefficient: 1.5
  - ticker: "AAPL"
    base_amount: 3000
```

**Example**:
```python
from AAVC_calculate_tool.config_loader import load_config

try:
    config = load_config("portfolio.yaml")
    default_amount = config["default_settings"]["base_amount"]
    stocks = config["stocks"]
    
    for stock in stocks:
        print(f"Ticker: {stock['ticker']}")
        print(f"Amount: {stock.get('base_amount', default_amount)}")
        
except ConfigError as e:
    print(f"Configuration error: {e}")
```

#### `prepare_calculation_jobs`

```python
def prepare_calculation_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]
```

**Description**: Prepares calculation jobs from configuration data.

**Parameters**:
- `config` (Dict[str, Any]): Configuration dictionary from `load_config`

**Returns**:
- `List[Dict[str, Any]]`: List of calculation job dictionaries

**Job Structure**:
```python
{
    "ticker": "SPY",
    "base_amount": 2000,
    "reference_price": 400.0,
    "asymmetric_coefficient": 1.5
}
```

---

## Module: recorder

Investment logging and data persistence.

### Types

#### `LogEntry`

```python
LogEntry = TypedDict('LogEntry', {
    'date': str,
    'ticker': str,
    'base_amount': float,
    'reference_price': float,
    'calculated_investment': float
})
```

**Description**: Type definition for investment log entries.

**Fields**:
- `date`: Investment date in YYYY-MM-DD format
- `ticker`: Stock ticker symbol
- `base_amount`: Base investment amount
- `reference_price`: Reference price used in calculation
- `calculated_investment`: Final calculated investment amount

### Functions

#### `record_investment`

```python
def record_investment(log_entry: LogEntry, log_file: str = "investment_log.csv") -> None
```

**Description**: Records an investment calculation to a CSV log file.

**Parameters**:
- `log_entry` (LogEntry): Investment log entry to record
- `log_file` (str, optional): Path to the log file. Defaults to "investment_log.csv"

**Raises**:
- `LogWriteError`: If there's an error writing to the log file

**Example**:
```python
from AAVC_calculate_tool.recorder import record_investment, LogEntry
from datetime import datetime

log_entry: LogEntry = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "ticker": "AAPL",
    "base_amount": 10000.0,
    "reference_price": 150.0,
    "calculated_investment": 8500.0
}

try:
    record_investment(log_entry, "my_portfolio.csv")
    print("Investment logged successfully")
except LogWriteError as e:
    print(f"Error logging investment: {e}")
```

**File Format**: CSV with headers: `date,ticker,base_amount,reference_price,calculated_investment`
**File Creation**: Automatically creates file with headers if it doesn't exist
**Append Mode**: New entries are appended to existing files

---

## Module: __main__

Command-line interface entry point.

### Functions

#### `main`

```python
def main() -> None
```

**Description**: Main entry point for the CLI application.

**CLI Structure**:
```bash
python -m AAVC_calculate_tool [subcommand] [options]
```

**Subcommands**:
- `calc`: Calculate investment amounts
- `backtest`: Run backtesting (planned)

**Calc Command Options**:
- `--ticker, -t`: Stock ticker symbol
- `--config, -c`: Configuration file path
- `--amount, -a`: Base investment amount
- `--ref-price, -r`: Reference price
- `--log-file`: Custom log file path

**Example Usage**:
```bash
# Single stock calculation
python -m AAVC_calculate_tool calc --ticker AAPL --amount 10000

# Configuration file calculation
python -m AAVC_calculate_tool calc --config portfolio.yaml

# With custom log file
python -m AAVC_calculate_tool calc --ticker SPY --amount 5000 --log-file custom_log.csv
```

---

## Exception Classes

### `TickerNotFoundError`

```python
class TickerNotFoundError(Exception):
    """Raised when a ticker symbol is not found."""
    pass
```

### `DataFetchError`

```python
class DataFetchError(Exception):
    """Raised when there's an error fetching data."""
    pass
```

### `ConfigNotFoundError`

```python
class ConfigNotFoundError(Exception):
    """Raised when a configuration file is not found."""
    pass
```

### `ConfigParseError`

```python
class ConfigParseError(Exception):
    """Raised when there's an error parsing configuration."""
    pass
```

### `ConfigError`

```python
class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass
```

### `LogWriteError`

```python
class LogWriteError(Exception):
    """Raised when there's an error writing to log files."""
    pass
```

---

## Data Types and Constants

### Supported Ticker Formats

- **US Stocks**: AAPL, SPY, QQQ
- **Japanese Stocks**: 7203.T (Toyota), 6758.T (Sony)
- **ETFs**: SPY, QQQ, VTI
- **International**: ^GSPC (S&P 500), ^DJI (Dow Jones)

### Price Data Format

- **Frequency**: Daily closing prices
- **Period**: 1 year (252 trading days)
- **Currency**: USD (primary), JPY (converted)
- **Data Source**: Yahoo Finance

### Configuration File Format

- **Format**: YAML
- **Encoding**: UTF-8
- **Required Fields**: `default_settings.base_amount`, `stocks[].ticker`
- **Optional Fields**: `asymmetric_coefficient`, `reference_price`

---

## Performance Characteristics

### Time Complexity

- **Data Fetching**: O(1) for single ticker, O(n) for n tickers
- **AAVC Calculation**: O(m) where m is the number of price points
- **Configuration Loading**: O(n) where n is the number of stocks
- **Logging**: O(1) per log entry

### Memory Usage

- **Price Data**: ~2KB per ticker (252 float values)
- **Configuration**: ~1KB per stock entry
- **Log Files**: Grows linearly with number of calculations

### Network Operations

- **Data Fetching**: 1 HTTP request per ticker
- **Rate Limiting**: Respects Yahoo Finance rate limits
- **Caching**: No built-in caching (implemented by yfinance)

---

## Best Practices

### Error Handling

```python
try:
    prices = fetch_price_history(ticker)
    investment = calculate_aavc_investment(prices, amount, ref_price)
    record_investment(log_entry, log_file)
except TickerNotFoundError:
    print(f"Ticker {ticker} not found")
except DataFetchError as e:
    print(f"Data fetch error: {e}")
except ValueError as e:
    print(f"Calculation error: {e}")
except LogWriteError as e:
    print(f"Logging error: {e}")
```

### Configuration Management

```python
# Load configuration once
config = load_config("config.yaml")

# Process multiple stocks
jobs = prepare_calculation_jobs(config)
for job in jobs:
    try:
        # Process each job
        prices = fetch_price_history(job["ticker"])
        investment = calculate_aavc_investment(**job)
        # Log result
    except Exception as e:
        print(f"Error processing {job['ticker']}: {e}")
        continue
```

### Logging Strategy

```python
# Use descriptive log file names
log_file = f"portfolio_{datetime.now().strftime('%Y%m')}.csv"

# Log all calculations for audit trail
record_investment(log_entry, log_file)

# Consider log rotation for long-term use
``` 