from unittest.mock import patch

import pandas as pd
import pytest

from src.AAVC_calculate_tool.data_loader import (
    DataFetchError,
    TickerNotFoundError,
    fetch_price_history,
)


# Mock yfinance for consistent testing and to avoid network calls
@pytest.fixture
def mock_yfinance_success():
    # Clear the cache before each test to ensure fresh data fetching
    fetch_price_history.cache_clear()
    with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
        mock_yf.Ticker.return_value.history.return_value = \
            pd.DataFrame({'Close': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]})
        yield mock_yf


# Test fetch_price_history with valid ticker
def test_fetch_price_history_valid_ticker(mock_yfinance_success):
    prices = fetch_price_history("AAPL")
    assert isinstance(prices, list)
    assert len(prices) == 6
    assert prices[0] == 100.0
    assert prices[-1] == 105.0
    mock_yfinance_success.Ticker.assert_called_with("AAPL")
    mock_yfinance_success.Ticker.return_value.history.assert_called_with(period="60d")

# Test fetch_price_history with invalid ticker (empty DataFrame)
def test_fetch_price_history_invalid_ticker():
    with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
        mock_yf.Ticker.return_value.history.return_value = pd.DataFrame() # Empty DataFrame
        with pytest.raises(TickerNotFoundError) as excinfo:
            fetch_price_history("INVALID")
        assert "No data found for ticker 'INVALID'" in str(excinfo.value)

# Test fetch_price_history with general data fetch error
def test_fetch_price_history_general_error():
    with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
        mock_yf.Ticker.return_value.history.side_effect = Exception("Network error")
        with pytest.raises(DataFetchError) as excinfo:
            fetch_price_history("ERROR_TICKER")
        assert "Failed to fetch data for 'ERROR_TICKER'" in str(excinfo.value)
        assert "Network error" in str(excinfo.value)

# Test lru_cache
def test_fetch_price_history_caching():
    with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
        mock_yf.Ticker.return_value.history.return_value = \
            pd.DataFrame({'Close': [100.0, 101.0]})

        # First call, should hit yfinance
        prices1 = fetch_price_history("CACHED_TICKER")
        mock_yf.Ticker.return_value.history.assert_called_once()

        # Second call with same args, should use cache
        prices2 = fetch_price_history("CACHED_TICKER")
        mock_yf.Ticker.return_value.history.assert_called_once() # Still called once, as cache hit prevents second call

        assert prices1 == prices2
