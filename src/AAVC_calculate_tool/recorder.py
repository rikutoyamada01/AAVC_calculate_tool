import csv
from typing import TypedDict


class LogEntry(TypedDict):
    """Type definition for a log entry."""
    date: str
    ticker: str
    base_amount: float
    reference_price: float
    calculated_investment: float


class LogWriteError(Exception):
    """Custom exception for errors during log writing."""
    pass


def record_investment(log_entry: LogEntry, file_path: str = "investment_log.csv") -> None:
    """投資結果をCSVファイルに記録する。

    Args:
        log_entry (LogEntry): 記録するログエントリ。
        file_path (str): ログファイルのパス (デフォルト: investment_log.csv)。
    """
    file_exists = False
    try:
        with open(file_path, 'r') as f:
            file_exists = True
    except FileNotFoundError:
        pass  # File does not exist, will be created

    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(log_entry.keys()))

            if not file_exists:
                writer.writeheader()  # Write header only if file is new

            writer.writerow(log_entry)
    except IOError as e:
        raise LogWriteError(f"Failed to write log to {file_path}: {e}") from e
