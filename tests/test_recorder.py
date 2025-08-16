from unittest.mock import patch

import pytest

from src.AAVC_calculate_tool.recorder import LogEntry, LogWriteError, record_investment


@pytest.fixture
def temp_log_file(tmp_path):
    """一時的なログファイルパスを提供するフィクスチャ"""
    return tmp_path / "test_investment_log.csv"

def test_record_investment_new_file(temp_log_file):
    """新しいファイルにログが正しく書き込まれることをテスト"""
    log_entry: LogEntry = {
        "date": "2023-01-01",
        "ticker": "TEST",
        "base_amount": 10000.0,
        "reference_price": 150.0,
        "calculated_investment": 10500.0,
    }
    record_investment(log_entry, str(temp_log_file))

    assert temp_log_file.exists()
    with open(temp_log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2  # Header + 1 data row
        assert lines[0].strip() == "date,ticker,base_amount,reference_price,calculated_investment"
        assert lines[1].strip() == "2023-01-01,TEST,10000.0,150.0,10500.0"

def test_record_investment_append_to_existing_file(temp_log_file):
    """既存のファイルにログが正しく追記されることをテスト"""
    # 最初のログを書き込む
    log_entry1: LogEntry = {
        "date": "2023-01-01",
        "ticker": "TEST1",
        "base_amount": 10000.0,
        "reference_price": 150.0,
        "calculated_investment": 10500.0,
    }
    record_investment(log_entry1, str(temp_log_file))

    # 2番目のログを追記
    log_entry2: LogEntry = {
        "date": "2023-01-02",
        "ticker": "TEST2",
        "base_amount": 20000.0,
        "reference_price": 250.0,
        "calculated_investment": 21000.0,
    }
    record_investment(log_entry2, str(temp_log_file))

    assert temp_log_file.exists()
    with open(temp_log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 3  # Header + 2 data rows
        assert lines[0].strip() == "date,ticker,base_amount,reference_price,calculated_investment"
        assert lines[1].strip() == "2023-01-01,TEST1,10000.0,150.0,10500.0"
        assert lines[2].strip() == "2023-01-02,TEST2,20000.0,250.0,21000.0"

def test_record_investment_io_error(temp_log_file):
    """IOErrorが発生した場合にLogWriteErrorが送出されることをテスト"""
    log_entry: LogEntry = {
        "date": "2023-01-01",
        "ticker": "TEST",
        "base_amount": 10000.0,
        "reference_price": 150.0,
        "calculated_investment": 10500.0,
    }

    # 存在しないディレクトリを指定してIOErrorを発生させる
    invalid_path = str(temp_log_file / "non_existent_dir" / "log.csv")

    with pytest.raises(LogWriteError) as excinfo:
        record_investment(log_entry, invalid_path)
    assert "Failed to write log to" in str(excinfo.value)
    assert "non_existent_dir" in str(excinfo.value)

    # ファイル書き込み中にIOErrorが発生するようモックする
    with patch('builtins.open', side_effect=IOError("Mocked IOError")):
        with pytest.raises(LogWriteError) as excinfo:
            record_investment(log_entry, str(temp_log_file))
        assert "Failed to write log to" in str(excinfo.value)
        assert "Mocked IOError" in str(excinfo.value)
