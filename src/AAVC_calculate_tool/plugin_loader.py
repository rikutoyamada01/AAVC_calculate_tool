from AAVC_calculate_tool.algorithm_registry import AlgorithmRegistry
from AAVC_calculate_tool.calculator import AAVCStrategy, BuyAndHoldStrategy, DCAStrategy


def initialize_registry() -> AlgorithmRegistry:
    """アルゴリズムレジストリを初期化し、デフォルトのアルゴリズムを登録する"""
    registry = AlgorithmRegistry()
    registry.register(AAVCStrategy())
    registry.register(DCAStrategy())
    registry.register(BuyAndHoldStrategy())
    return registry


# グローバルなレジストリインスタンス
ALGORITHM_REGISTRY = initialize_registry()
