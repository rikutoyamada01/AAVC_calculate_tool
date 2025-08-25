import numpy as np

def generate_deterministic_price_path(
    initial_price: float,
    annual_growth_rate: float,
    amplitude: float,
    frequency: float,
    num_trading_days: int,
    trading_days_per_year: int = 252,
) -> np.ndarray:
    """
    Generates a deterministic stock price path with inflationary growth and sinusoidal oscillation.

    Args:
        initial_price: The starting price of the stock.
        annual_growth_rate: The annual growth rate (e.g., due to inflation).
        amplitude: The amplitude of the sinusoidal oscillation (e.g., 0.1 for 10% fluctuation).
        frequency: The frequency of the oscillation (cycles per trading day, e.g., 1/20 for 1 cycle every 20 days).
        num_trading_days: The total number of trading days to simulate.
        trading_days_per_year: The number of trading days in a year.

    Returns:
        A numpy array representing the simulated deterministic price path.
    """
    price_path = np.zeros(num_trading_days)
    price_path[0] = initial_price

    for t in range(num_trading_days):
        # Growth component (compounding annually)
        growth_factor = (1 + annual_growth_rate)**(t / trading_days_per_year)
        
        # Sinusoidal oscillation component
        oscillation_factor = 1 + amplitude * np.sin(2 * np.pi * frequency * t)
        
        price_path[t] = initial_price * growth_factor * oscillation_factor

    return price_path

if __name__ == "__main__":
    # Example usage:
    initial_price = 100.0
    annual_growth_rate = 0.05 # 5% annual growth
    amplitude = 0.10 # 10% fluctuation around the trend
    frequency = 1/60 # 1 cycle every 60 trading days
    num_years = 5
    num_trading_days = num_years * 252
    
    print(f"Simulating deterministic price path for {num_years} years ({num_trading_days} days)...")
    price_path = generate_deterministic_price_path(
        initial_price,
        annual_growth_rate,
        amplitude,
        frequency,
        num_trading_days
    )
    
    print(f"Generated price path length: {len(price_path)}")
    print(f"First 5 prices: {price_path[:5]}")
    print(f"Last 5 prices: {price_path[-5:]}")
    print(f"Min price: {np.min(price_path):.2f}")
    print(f"Max price: {np.max(price_path):.2f}")
    print(f"Final price: {price_path[-1]:.2f}")
