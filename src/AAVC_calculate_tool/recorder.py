import csv
from pathlib import Path
from typing import TypedDict


# Custom exception
class LogWriteError(Exception):
    """ログ書き込みに関するエラー"""
    pass

class LogEntry(TypedDict):
    date: str
    ticker: str
    base_amount: float
    reference_price: float
    calculated_investment: float

def record_investment(log_entry: LogEntry, file_path: str = "investment_log.csv") -> None:
    """
    計算結果のログをCSVファイルに追記する

    :param log_entry: 記録するログデータ（辞書形式）
    :param file_path: ログファイルのパス
    """
    file_exists = Path(file_path).exists()
    fieldnames = list(LogEntry.__annotations__.keys())

    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(log_entry)
    except IOError as e:
        raise LogWriteError(f"Failed to write log to {file_path}: {e}")
