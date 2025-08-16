import numpy as np

def calculate_aavc_investment(price_path: list, base_amount: float, reference_price: float, asymmetric_coefficient: float = 2.0) -> float:
    """
    AAVCアルゴリズムに基づいて、その日の投資額を計算する関数

    :param price_path: 過去N日間の株価推移のリスト（例: [1000, 1010, 990, ...])
    :param base_amount: 基準となる投資額
    :param reference_price: 基準価格
    :param asymmetric_coefficient: 非対称性係数（デフォルトは2.0）
    :return: その日に投資すべき金額
    """
    
    # --- 1. 株価の確認 ---
    if not price_path:
        return 0.0  # 株価データがない場合は0を返す
    
    current_price = price_path[-1]
    
    # --- 2. ボラティリティの計算 ---
    if len(price_path) < 2:
        volatility = 0.0
    else:
        # 価格の変動率を計算
        price_changes = np.abs(np.diff(price_path) / price_path[:-1])
        volatility = np.mean(price_changes)
        
    # --- 3. 乖離率の計算 ---
    if reference_price == 0:
        price_change_rate = 0.0
    else:
        price_change_rate = (reference_price - current_price) / reference_price
        
    # --- 4. 投資額調整率の計算 ---
    # ボラティリティ調整係数を計算
    volatility_adjustment_factor = 1.0 + (volatility / 0.01) # 基準ボラティリティは1%に設定
    
    adjusted_rate = asymmetric_coefficient * price_change_rate * volatility_adjustment_factor
    
    # --- 5. 最終投資額の計算 ---
    calculated_amount = base_amount * (1 + adjusted_rate)
    
    # --- 6. 投資額の制限 ---
    # 投資額がマイナスにならないように
    if calculated_amount < 0:
        return 0.0
    
    # 上限キャップ（例: 基準額の3倍）
    if calculated_amount > base_amount * 3:
        return base_amount * 3
        
    return float(calculated_amount)