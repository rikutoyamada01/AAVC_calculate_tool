import csv
import os
from unittest.mock import patch

import pytest

from src.AAVC_calculate_tool.recorder import LogEntry, LogWriteError, record_investment


class TestRecorder:
    """Test cases for the recorder module."""

    @pytest.fixture(autouse=True)
    def setup_method(self, tmp_path):
        self.log_file = tmp_path / "test_investment_log.csv"

    def test_record_investment_new_file(self):
        log_entry: LogEntry = {
            "date": "2023-01-01",
            "ticker": "TEST",
            "base_amount": 10000.0,
            "ref_price": 150.0,
            "calculated_investment": 10500.0
        }
        record_investment(log_entry, str(self.log_file))

        assert self.log_file.exists()
        with open(self.log_file, 'r', newline='') as f:
            reader = csv.reader(f)
            lines = list(reader)
            assert len(lines) == 2  # Header + 1 data row
            assert lines[0] == ["date", "ticker", "base_amount",
                                "ref_price", "calculated_investment"]
            assert lines[1] == ["2023-01-01", "TEST", "10000.0",
                                "150.0", "10500.0"]

    def test_record_investment_append_to_existing_file(self):
        # First entry
        log_entry1: LogEntry = {
            "date": "2023-01-01",
            "ticker": "TEST1",
            "base_amount": 10000.0,
            "ref_price": 150.0,
            "calculated_investment": 10500.0
        }
        record_investment(log_entry1, str(self.log_file))

        # Second entry
        log_entry2: LogEntry = {
            "date": "2023-01-02",
            "ticker": "TEST2",
            "base_amount": 20000.0,
            "ref_price": 250.0,
            "calculated_investment": 21000.0
        }
        record_investment(log_entry2, str(self.log_file))

        with open(self.log_file, 'r', newline='') as f:
            reader = csv.reader(f)
            lines = list(reader)
            assert len(lines) == 3  # Header + 2 data rows
            assert lines[0] == ["date", "ticker", "base_amount",
                                "ref_price", "calculated_investment"]
            assert lines[1] == ["2023-01-01", "TEST1", "10000.0",
                                "150.0", "10500.0"]
            assert lines[2] == ["2023-01-02", "TEST2", "20000.0",
                                "250.0", "21000.0"]

    def test_record_investment_io_error(self):
        # Simulate an IOError by patching csv.DictWriter.writerow
        with patch('csv.DictWriter.writerow', side_effect=IOError("Disk full")):
            with pytest.raises(LogWriteError) as excinfo:
                log_entry = {
                    "date": "2023-01-01",
                    "ticker": "TEST",
                    "base_amount": 10000.0,
                    "ref_price": 100.0,
                    "calculated_investment": 10000.0,
                }
                record_investment(log_entry, "test_log.csv") # Use a generic file name
            assert "Failed to write log to test_log.csv: Disk full" in str(excinfo.value)
