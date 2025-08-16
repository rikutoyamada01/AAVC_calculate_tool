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
def fetch_price_history(ticker: str, period: str = "60d") -> List[float]:
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
