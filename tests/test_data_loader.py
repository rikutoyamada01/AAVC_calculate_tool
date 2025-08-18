from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.AAVC_calculate_tool.data_loader import (
    DataFetchError,
    TickerNotFoundError,
    fetch_price_history,
    fetch_price_history_by_date,
)


class TestDataLoader:
    """Test cases for the data_loader module."""

    @pytest.fixture(autouse=True)
    def setup(self):
        # Clear cache before each test
        from src.AAVC_calculate_tool.data_loader import _price_history_cache
        _price_history_cache.clear()

    def test_fetch_price_history_success(self):
        with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
            # Mock yfinance Ticker and history method
            mock_yf.Ticker.return_value.history.return_value = pd.DataFrame({
                'Close': [100.0, 101.0, 102.0],
                'Volume': [1000, 1000, 1000]
            }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))

            prices = fetch_price_history("AAPL")
            assert prices == [100.0, 101.0, 102.0]
            mock_yf.Ticker.assert_called_with("AAPL")
            mock_yf.Ticker.return_value.history.assert_called_with(period="max")

    def test_fetch_price_history_invalid_ticker(self):
        with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
            mock_yf.Ticker.return_value.history.return_value = pd.DataFrame()  # Empty DataFrame
            with pytest.raises(TickerNotFoundError) as excinfo:
                fetch_price_history("INVALID")
            assert "No data found for ticker 'INVALID'" in str(excinfo.value)

    def test_fetch_price_history_data_fetch_error(self):
        with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
            # Mock the Ticker instance's history method to raise an exception
            mock_ticker_instance = MagicMock()
            mock_yf.Ticker.return_value = mock_ticker_instance
            mock_ticker_instance.history.side_effect = Exception("Network Error")

            with pytest.raises(DataFetchError) as excinfo:
                fetch_price_history("AAPL")
            assert "Failed to fetch data for 'AAPL': Network Error" in str(excinfo.value)

    def test_fetch_price_history_cache(self):
        with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
            mock_yf.Ticker.return_value.history.return_value = pd.DataFrame({
                'Close': [100.0, 101.0, 102.0],
                'Volume': [1000, 1000, 1000]
            }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))

            prices1 = fetch_price_history("CACHED_TICKER")
            prices2 = fetch_price_history("CACHED_TICKER")
            # yfinance should only be called once due to caching
            mock_yf.Ticker.return_value.history.assert_called_once()

            assert prices1 == prices2

    def test_fetch_price_history_by_date_success(self):
        with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
            mock_yf.Ticker.return_value.history.return_value = pd.DataFrame({
                'Close': [100.0, 101.0, 102.0],
                'Volume': [1000, 1000, 1000]
            }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))

            prices, dates = fetch_price_history_by_date("AAPL", "2023-01-01", "2023-01-03")
            assert prices == [100.0, 101.0, 102.0]
            assert dates == ['2023-01-01', '2023-01-02', '2023-01-03']
            mock_yf.Ticker.assert_called_with("AAPL")
            mock_yf.Ticker.return_value.history.assert_called_with(
                start="2023-01-01", end="2023-01-03")

    def test_fetch_price_history_by_date_no_data(self):
        with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
            mock_yf.Ticker.return_value.history.return_value = pd.DataFrame()  # Empty DataFrame
            with pytest.raises(TickerNotFoundError) as excinfo:
                fetch_price_history_by_date("AAPL", "2023-01-01", "2023-01-03")
            assert "No data found for ticker 'AAPL' from 2023-01-01 to 2023-01-03." in str(excinfo.value)

    def test_fetch_price_history_by_date_error(self):
        with patch('src.AAVC_calculate_tool.data_loader.yf') as mock_yf:
            mock_yf.Ticker.side_effect = Exception("API Limit")
            with pytest.raises(DataFetchError) as excinfo:
                fetch_price_history_by_date("AAPL", "2023-01-01", "2023-01-03")
            assert "Failed to fetch data for 'AAPL' from 2023-01-01 to 2023-01-03: API Limit" in str(excinfo.value)
