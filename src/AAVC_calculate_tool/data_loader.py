from typing import List, Tuple

import yfinance as yf


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""
    pass


class TickerNotFoundError(DataFetchError):
    """Custom exception for ticker not found errors."""
    pass


# Cache for fetched price history
_price_history_cache = {}


def fetch_price_history(ticker: str) -> List[float]:
    """Fetch historical closing prices for a given ticker from Yahoo Finance."""
    if ticker in _price_history_cache:
        return _price_history_cache[ticker]

    try:
        # Fetch data for a long period to ensure enough history
        # yfinance automatically handles start/end dates if period is given
        data = yf.Ticker(ticker)
        hist = data.history(period="max")

        if hist.empty:
            raise TickerNotFoundError(f"No data found for ticker '{ticker}'.")

        # Extract 'Close' column and convert to list
        # Ensure the list is sorted by date (yfinance history is usually
        # sorted oldest to newest)
        prices = hist['Close'].tolist()
        _price_history_cache[ticker] = prices
        return prices
    except TickerNotFoundError as e:
        raise e  # Re-raise custom exception
    except Exception as e:
        # Catch any other exceptions from yfinance or network issues
        raise DataFetchError(f"Failed to fetch data for '{ticker}': {e}") from e


def fetch_price_history_by_date(
    ticker: str,
    start_date: str,
    end_date: str
) -> Tuple[List[float], List[str]]:
    """指定された期間のティッカーの終値履歴を取得する。

    Args:
        ticker (str): Yahoo Financeのティッカーシンボル。
        start_date (str): 取得開始日 (YYYY-MM-DD)。
        end_date (str): 取得終了日 (YYYY-MM-DD)。

    Returns:
        Tuple[List[float], List[str]]: 終値のリストと対応する日付文字列のリスト。

    Raises:
        TickerNotFoundError: 指定された期間でティッカーのデータが見つからない場合。
        DataFetchError: データ取得中に問題が発生した場合。
    """
    try:
        data = yf.Ticker(ticker)
        # Fetch data for the specified date range
        hist = data.history(start=start_date, end=end_date)

        if hist.empty:
            raise TickerNotFoundError(f"No data found for ticker '{ticker}' "
                                      f"from {start_date} to {end_date}.")

        # Extract 'Close' column and dates, convert to lists
        prices = hist['Close'].tolist()
        dates = hist.index.to_series().dt.strftime('%Y-%m-%d').tolist()

        return prices, dates
    except TickerNotFoundError as e:
        raise e  # Re-raise custom exception
    except Exception as e:
        # Catch any other exceptions from yfinance or network issues
        raise DataFetchError(f"Failed to fetch data for '{ticker}' "
                             f"from {start_date} to {end_date}: {e}") from e
