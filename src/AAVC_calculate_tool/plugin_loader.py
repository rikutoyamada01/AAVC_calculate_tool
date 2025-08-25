from AAVC_calculate_tool.algorithm_registry import AlgorithmRegistry
from AAVC_calculate_tool.calculator import (
    AAVCDynamicStrategy,
    AAVCStaticStrategy,
    AAVCMovingAverageStrategy,
    AAVCHighestPriceResetStrategy,
    BuyAndHoldStrategy,
    DCAStrategy
)
from AAVC_calculate_tool.minus_five_percent_rule import MinusFivePercentRuleStrategy


def initialize_registry() -> AlgorithmRegistry:
    """アルゴリズムレジストリを初期化し、デフォルトのアルゴリズムを登録する"""
    registry = AlgorithmRegistry()
    
    # Register AAVC versions
    registry.register(AAVCStaticStrategy)
    registry.register(AAVCDynamicStrategy)
    registry.register(AAVCMovingAverageStrategy)
    registry.register(AAVCHighestPriceResetStrategy)

    # Register other strategies
    registry.register(DCAStrategy)
    registry.register(BuyAndHoldStrategy)
    registry.register(MinusFivePercentRuleStrategy)
    
    return registry


# グローバルなレジストリインスタンス
ALGORITHM_REGISTRY = initialize_registry()
