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
        self._algorithm_classes: Dict[str, type[InvestmentAlgorithm]] = {}
        self._metadata: Dict[str, AlgorithmMetadata] = {}

    def register(self, algorithm_class: type[InvestmentAlgorithm]) -> None:
        """アルゴリズムクラスを登録"""
        # メタデータ取得のために一時的にインスタンス化
        temp_instance = algorithm_class()
        metadata = temp_instance.get_metadata()
        self._algorithm_classes[metadata.name] = algorithm_class
        self._metadata[metadata.name] = metadata

    def get_algorithm(self, name: str) -> Optional[InvestmentAlgorithm]:
        """アルゴリズムの新しいインスタンスを取得"""
        algorithm_class = self._algorithm_classes.get(name)
        if algorithm_class:
            return algorithm_class()  # 毎回新しいインスタンスを返す
        return None

    def list_algorithms(self) -> List[str]:
        """登録済みアルゴリズムの一覧を取得"""
        return list(self._algorithm_classes.keys())

    def get_metadata(self, name: str) -> Optional[AlgorithmMetadata]:
        """アルゴリズムのメタデータを取得"""
        return self._metadata.get(name)
