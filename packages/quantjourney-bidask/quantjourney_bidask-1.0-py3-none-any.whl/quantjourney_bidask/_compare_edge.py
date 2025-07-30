# compare_edge_v2.py
"""
Comprehensive comparison script for EDGE estimator implementations.

This script benchmarks three versions of the EDGE bid-ask spread estimator:
1.  `edge_original`: The baseline, pure NumPy implementation.
2.  `edge_improved_v1`: Optimized with a modular structure and a Numba kernel
    for the core calculation.
3.  `edge_improved_v2`: Hyper-optimized with a single, monolithic Numba kernel
    to minimize Python overhead and maximize compiler optimizations.

The script validates that the optimized versions are numerically identical to the
original (within floating-point tolerances) and quantifies the performance gains
across a variety of test datasets.

To Run:
1. Ensure `edge.py`, `edge_improved.py`, and `edge_improved_v2.py` are in the same directory.
2. Execute from the terminal: `python compare_edge_v2.py`
"""
import time
import numpy as np

# Import the three versions of the edge function for comparison
from edge import edge as edge_original
from quantjourney_bidask.edge_improved_v1 import edge as edge_improved_v1
from quantjourney_bidask.edge_improved_v2 import edge as edge_improved_v2


def generate_complex_ohlc_data(num_points, initial_price=100.0, annual_vol=0.20, annual_drift=0.05, daily_spread_pct=0.005, overnight_vol=0.001, seed=42):
    """Generates synthetic OHLC data with overnight gaps for robust testing."""
    np.random.seed(seed)
    dt = 1 / 252.0
    daily_vol = annual_vol * np.sqrt(dt)
    daily_drift = annual_drift * dt
    log_returns = daily_drift + daily_vol * np.random.normal(size=num_points)
    mid_prices_series = initial_price * np.exp(np.cumsum(log_returns))
    
    mid_prices_series = np.maximum(mid_prices_series, 1e-6)
    overnight_returns = np.random.normal(loc=0, scale=overnight_vol, size=num_points)
    open_prices = mid_prices_series * np.exp(overnight_returns)
    open_prices = np.roll(open_prices, 1)
    open_prices[0] = initial_price
    close_prices = mid_prices_series
    
    intraday_range_factor = np.random.uniform(daily_vol, daily_vol * 2.5, size=num_points)
    intraday_range = intraday_range_factor * mid_prices_series
    high_prices = mid_prices_series + intraday_range / 2.0
    low_prices = mid_prices_series - intraday_range / 2.0
    
    spread_component = daily_spread_pct * mid_prices_series
    high_prices += spread_component / 2.0
    low_prices -= spread_component / 2.0
    
    high_prices = np.maximum.reduce([high_prices, open_prices, close_prices])
    low_prices = np.minimum.reduce([low_prices, open_prices, close_prices])
    
    high_prices = np.maximum(high_prices, 1e-6)
    low_prices = np.maximum(low_prices, 1e-6)
    open_prices = np.maximum(open_prices, 1e-6)
    close_prices = np.maximum(close_prices, 1e-6)
    
    return open_prices, high_prices, low_prices, close_prices

# --- Test Case Definitions ---
NUM_POINTS_10_YEARS = 10 * 252
open_10y, high_10y, low_10y, close_10y = generate_complex_ohlc_data(NUM_POINTS_10_YEARS, initial_price=500.0, daily_spread_pct=0.005)
open_small, high_small, low_small, close_small = [100.0, 101.5, 99.8, 102.1, 100.9], [102.3, 103.0, 101.2, 103.5, 102.0], [99.5, 100.8, 98.9, 101.0, 100.1], [101.2, 102.5, 100.3, 102.8, 101.5]
open_invalid, high_invalid, low_invalid, close_invalid = [100.0, 101.5, 99.8], [99.0, 103.0, 101.2], [99.5, 100.8, 98.9], [101.2, 102.5, 100.3]
open_nan, high_nan, low_nan, close_nan = [np.nan] * 5, [np.nan] * 5, [np.nan] * 5, [np.nan] * 5
open_non_positive, high_non_positive, low_non_positive, close_non_positive = [100.0, 0.0, 99.8], [102.0, 103.0, 101.2], [99.5, 100.8, 98.9], [101.2, 102.5, 100.3]
open_near_zero_diff, high_near_zero_diff, low_near_zero_diff, close_near_zero_diff = [100.0, 100.00000001, 100.00000002, 100.0, 100.00000001], [100.00000002, 100.00000003, 100.00000004, 100.00000002, 100.00000003], [99.99999998, 99.99999997, 99.99999996, 99.99999998, 99.99999997], [100.00000001, 100.00000002, 100.00000001, 100.00000001, 100.00000002]
open_partial_nan, high_partial_nan, low_partial_nan, close_partial_nan = [100.0, np.nan, 99.8, 102.1, np.nan], [102.3, 103.0, 101.2, 103.5, 102.0], [99.5, 100.8, 98.9, 101.0, 100.1], [101.2, 102.5, 100.3, 102.8, 101.5]
open_low_variability, high_low_variability, low_low_variability, close_low_variability = [100.0, 100.01, 100.02, 100.01, 100.0], [100.03, 100.04, 100.05, 100.04, 100.03], [99.97, 99.96, 99.95, 99.96, 99.97], [100.01, 100.02, 100.01, 100.02, 100.01]

test_cases = [
    {"name": f"Large Dataset ({NUM_POINTS_10_YEARS} points)", "open": open_10y, "high": high_10y, "low": low_10y, "close": close_10y},
    {"name": "Small Dataset (5 points)", "open": open_small, "high": high_small, "low": low_small, "close": close_small},
    {"name": "Invalid OHLC (high < low)", "open": open_invalid, "high": high_invalid, "low": low_invalid, "close": close_invalid},
    {"name": "All NaN", "open": open_nan, "high": high_nan, "low": low_nan, "close": close_nan},
    {"name": "Non-positive Prices", "open": open_non_positive, "high": high_non_positive, "low": low_non_positive, "close": close_non_positive},
    {"name": "Near-zero Differences", "open": open_near_zero_diff, "high": high_near_zero_diff, "low": low_near_zero_diff, "close": close_near_zero_diff},
    {"name": "Partial NaN", "open": open_partial_nan, "high": high_partial_nan, "low": low_partial_nan, "close": close_partial_nan},
    {"name": "Low Variability", "open": open_low_variability, "high": high_low_variability, "low": low_low_variability, "close": close_low_variability},
]

# --- Numba Warm-up ---
# First call to a Numba function includes compilation time.
# We run it once on a small dataset to ensure subsequent timings are for execution only.
print("Warming up Numba JIT compilers (this may take a moment)...")
try:
    edge_improved_v1(open_small, high_small, low_small, close_small)
    edge_improved_v2(open_small, high_small, low_small, close_small)
except Exception as e:
    print(f"An error occurred during warm-up: {e}")
print("Warm-up complete.\n")


# --- Main Comparison ---
print("="*80)
print("Comparing edge_original vs. edge_improved_v1 vs. edge_improved_v2")
print("="*80 + "\n")

for test in test_cases:
    name = test["name"]
    open_p, high_p, low_p, close_p = test["open"], test["high"], test["low"], test["close"]

    # --- Run original function and time it ---
    try:
        start_time = time.perf_counter()
        result_original = edge_original(open_p, high_p, low_p, close_p)
        time_original = time.perf_counter() - start_time
    except Exception as e:
        result_original, time_original = f"Error: {type(e).__name__}", -1

    # --- Run improved_v1 function and time it ---
    try:
        start_time = time.perf_counter()
        result_v1 = edge_improved_v1(open_p, high_p, low_p, close_p)
        time_v1 = time.perf_counter() - start_time
    except Exception as e:
        result_v1, time_v1 = f"Error: {type(e).__name__}", -1

    # --- Run improved_v2 (hyper-optimized) function and time it ---
    try:
        start_time = time.perf_counter()
        result_v2 = edge_improved_v2(open_p, high_p, low_p, close_p)
        time_v2 = time.perf_counter() - start_time
    except Exception as e:
        result_v2, time_v2 = f"Error: {type(e).__name__}", -1
    
    # --- Reporting ---
    print(f"--- Test Case: {name} ---")
    print(f"  Original:      {result_original:<25} (Time: {time_original*1000:.4f} ms)")
    print(f"  Improved v1:   {result_v1:<25} (Time: {time_v1*1000:.4f} ms)")
    print(f"  Improved v2:   {result_v2:<25} (Time: {time_v2*1000:.4f} ms)")
    
    # Check numerical equivalence against the original baseline
    is_v1_ok = np.isclose(result_original, result_v1, rtol=1e-9, atol=1e-12, equal_nan=True) if isinstance(result_original, float) and isinstance(result_v1, float) else str(result_original) == str(result_v1)
    is_v2_ok = np.isclose(result_original, result_v2, rtol=1e-9, atol=1e-12, equal_nan=True) if isinstance(result_original, float) and isinstance(result_v2, float) else str(result_original) == str(result_v2)
    
    status_v1 = "\033[92mPASS\033[0m" if is_v1_ok else "\033[91mFAIL\033[0m"
    status_v2 = "\033[92mPASS\033[0m" if is_v2_ok else "\033[91mFAIL\033[0m"
    print(f"  Equivalence (v1/v2 vs Original): {status_v1} / {status_v2}")
    
    # Performance reporting
    perf_string_v1, perf_string_v2 = "N/A", "N/A"
    if time_original > 0 and time_v1 > 0:
        perf_string_v1 = f"{time_original / time_v1:.2f}x"
    if time_original > 0 and time_v2 > 0:
        perf_string_v2 = f"{time_original / time_v2:.2f}x"
        
    print(f"  Speedup (v1/v2 vs Original):     {perf_string_v1} / {perf_string_v2}\n")