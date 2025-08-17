from functools import lru_cache
from typing import List

import yfinance as yf


# Custom exceptions (as per detailed design)
class DataFetchError(Exception):
    """データ取得に関する汎用的なエラー"""
    pass

class TickerNotFoundError(DataFetchError):
    """ティッカーが見つからない、またはデータが存在しないエラー"""
    pass

@lru_cache(maxsize=32)
def fetch_price_history(ticker: str, period: str = "1y") -> List[float]:
    """
    指定されたティッカーの時系列価格データを取得する。
    yfinanceライブラリを使用する。

    Args:
        ticker (str): Yahoo Financeのティッカーシンボル。
        period (str): データを取得する期間 (例: "60d", "3mo", "1y")。

    Returns:
        List[float]: 終値のリスト。日付の昇順（古い→新しい）でソートされている。

    Raises:
        TickerNotFoundError: ティッカーが見つからない、またはデータが存在しない場合。
        DataFetchError: データ取得に関するその他のエラー。
    """
    try:
        stock = yf.Ticker(ticker)
        # history() returns a pandas DataFrame
        hist = stock.history(period=period)

        if hist.empty:
            raise TickerNotFoundError(f"No data found for ticker '{ticker}' for period '{period}'.")

        # Extract 'Close' column and convert to list
        # Ensure the list is sorted by date (yfinance history is usually sorted oldest to newest)
        return hist['Close'].tolist()

    except TickerNotFoundError: # Re-raise custom exception
        raise
    except Exception as e:
        # Catch any other exceptions from yfinance or network issues
        raise DataFetchError(f"Failed to fetch data for '{ticker}': {e}")


def fetch_price_history_by_date(
    ticker: str, 
    start_date: str, 
    end_date: str
) -> tuple[List[float], List[str]]:
    """
    指定されたティッカーの指定期間の時系列価格データを取得する。
    
    Args:
        ticker (str): Yahoo Financeのティッカーシンボル。
        start_date (str): 開始日 (YYYY-MM-DD形式)。
        end_date (str): 終了日 (YYYY-MM-DD形式)。

    Returns:
        tuple[List[float], List[str]]: (価格リスト, 日付リスト)のタプル。
                                      価格は日付の昇順（古い→新しい）でソートされている。

    Raises:
        TickerNotFoundError: ティッカーが見つからない、またはデータが存在しない場合。
        DataFetchError: データ取得に関するその他のエラー。
    """
    try:
        stock = yf.Ticker(ticker)
        # history() returns a pandas DataFrame with start and end dates
        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            raise TickerNotFoundError(f"No data found for ticker '{ticker}' from {start_date} to {end_date}.")

        # Extract 'Close' column and dates, convert to lists
        prices = hist['Close'].tolist()
        dates = hist.index.to_series().dt.strftime('%Y-%m-%d').tolist()
        
        return prices, dates

    except TickerNotFoundError: # Re-raise custom exception
        raise
    except Exception as e:
        # Catch any other exceptions from yfinance or network issues
        raise DataFetchError(f"Failed to fetch data for '{ticker}' from {start_date} to {end_date}: {e}")
