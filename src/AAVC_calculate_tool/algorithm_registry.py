from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class AlgorithmMetadata:
    """アルゴリズムのメタデータ"""
    name: str
    description: str
    version: str
    author: str
    parameters: Dict[str, Any]
    category: str

class InvestmentAlgorithm(Protocol):
    """投資アルゴリズムの統一インターフェース"""

    def get_metadata(self) -> AlgorithmMetadata:
        """アルゴリズムのメタデータを返す"""
        ...

    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        """投資額を計算する"""
        ...

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """パラメータの妥当性を検証する"""
        ...

class BaseAlgorithm(ABC):
    """アルゴリズムの基底クラス"""

    @abstractmethod
    def get_metadata(self) -> AlgorithmMetadata:
        pass

    @abstractmethod
    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """デフォルトのパラメータ検証"""
        return True

class AlgorithmRegistry:
    """アルゴリズムレジストリ"""

    def __init__(self):
        self._algorithms: Dict[str, InvestmentAlgorithm] = {}
        self._metadata: Dict[str, AlgorithmMetadata] = {}

    def register(self, algorithm: InvestmentAlgorithm) -> None:
        """アルゴリズムを登録"""
        metadata = algorithm.get_metadata()
        self._algorithms[metadata.name] = algorithm
        self._metadata[metadata.name] = metadata

    def get_algorithm(self, name: str) -> Optional[InvestmentAlgorithm]:
        """アルゴリズムを取得"""
        return self._algorithms.get(name)

    def list_algorithms(self) -> List[str]:
        """登録済みアルゴリズムの一覧を取得"""
        return list(self._algorithms.keys())

    def get_metadata(self, name: str) -> Optional[AlgorithmMetadata]:
        """アルゴリズムのメタデータを取得"""
        return self._metadata.get(name)
