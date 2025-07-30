#!/usr/bin/env python3
"""
Basic Spread Estimation Examples.

Demonstrates core spread estimation functionality using the EDGE estimator
with various data sources and window configurations.

Author: Jakub Polec
Date: 2025-06-28

Part of the QuantJourney framework - The framework with advanced quantitative 
finance tools and insights.
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add parent directory to path to access data module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetch import get_stock_data
from quantjourney_bidask import edge, edge_expanding, edge_rolling

print("Spread Estimator Examples")
print("========================")

# Test data download from the original paper
print("\n1. Testing with sample OHLC data...")
# Create sample OHLC data for testing
sample_data = {
    "Open": [100.0, 101.5, 99.8, 102.1, 100.9, 103.2, 101.7, 104.5, 102.3, 105.1],
    "High": [102.3, 103.0, 101.2, 103.5, 102.0, 104.8, 103.1, 106.2, 104.0, 106.5],
    "Low": [99.5, 100.8, 98.9, 101.0, 100.1, 102.5, 101.0, 103.8, 101.5, 104.2],
    "Close": [101.2, 102.5, 100.3, 102.8, 101.5, 104.1, 102.4, 105.7, 103.2, 105.8],
}
df = pd.DataFrame(sample_data)
spread = edge(df.Open, df.High, df.Low, df.Close)
print(f"Sample data spread: {spread:.6f}")

# Generate synthetic data for testing
print("\n2. Testing with synthetic data...")
np.random.seed(42)
n = 100
base_price = 100
returns = np.random.normal(0, 0.02, n)
prices = base_price * np.exp(np.cumsum(returns))
spread_pct = 0.01  # 1% bid-ask spread

# Simulate OHLC with embedded bid-ask spread
open_prices = prices
high_prices = prices * (1 + np.random.uniform(0, spread_pct / 2, n))
low_prices = prices * (1 - np.random.uniform(0, spread_pct / 2, n))
close_prices = prices + np.random.normal(0, 0.001, n)

synthetic_df = pd.DataFrame(
    {
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="h"),
    }
)

# Test single estimate
spread_single = edge(
    synthetic_df.open, synthetic_df.high, synthetic_df.low, synthetic_df.close
)
print(f"Synthetic data single spread: {spread_single:.6f}")

# Test rolling estimates
print("\n3. Testing rolling and expanding windows...")
synthetic_df["spread_rolling_21"] = edge_rolling(synthetic_df, window=21)
synthetic_df["spread_expanding"] = edge_expanding(synthetic_df, min_periods=21)

# Plot results
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Price plot
axes[0, 0].plot(synthetic_df["timestamp"], synthetic_df["close"], label="Close Price")
axes[0, 0].set_title("Synthetic Price Series")
axes[0, 0].set_ylabel("Price")
axes[0, 0].legend()

# Rolling spread
axes[0, 1].plot(
    synthetic_df["timestamp"],
    synthetic_df["spread_rolling_21"] * 100,
    label="Rolling Spread (21)",
    color="blue",
)
axes[0, 1].set_title("Rolling Spread Estimates")
axes[0, 1].set_ylabel("Spread (%)")
axes[0, 1].legend()

# Expanding spread
axes[1, 0].plot(
    synthetic_df["timestamp"],
    synthetic_df["spread_expanding"] * 100,
    label="Expanding Spread",
    color="green",
)
axes[1, 0].set_title("Expanding Spread Estimates")
axes[1, 0].set_ylabel("Spread (%)")
axes[1, 0].legend()

# Comparison
axes[1, 1].plot(
    synthetic_df["timestamp"],
    synthetic_df["spread_rolling_21"] * 100,
    label="Rolling (21)",
    alpha=0.7,
)
axes[1, 1].plot(
    synthetic_df["timestamp"],
    synthetic_df["spread_expanding"] * 100,
    label="Expanding",
    alpha=0.7,
)
axes[1, 1].axhline(
    y=spread_pct * 100, color="red", linestyle="--", label="True Spread (1%)"
)
axes[1, 1].set_title("Spread Comparison")
axes[1, 1].set_ylabel("Spread (%)")
axes[1, 1].legend()

plt.tight_layout()
plt.savefig("_output/spread_estimator_results.png", dpi=150, bbox_inches="tight")
print("Plot saved as 'spread_estimator_results.png'")
plt.show()

# Summary statistics
print("\n4. Summary Statistics:")
print(f"Rolling 21-period mean: {synthetic_df['spread_rolling_21'].mean()*100:.4f}%")
print(f"Expanding window mean: {synthetic_df['spread_expanding'].mean()*100:.4f}%")
print(f"True embedded spread: {spread_pct*100:.4f}%")

# Real data example (Yahoo Finance)
print("\n5. Real data examples (Yahoo Finance)...")
try:
    # Fetch SPY data
    spy_df = get_stock_data(ticker="SPY", period="1mo", interval="1d")

    # Compute rolling spreads
    spy_df["spread"] = edge_rolling(spy_df, window=20)

    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Spread in basis points
    ax1.plot(
        spy_df["timestamp"],
        spy_df["spread"] * 10000,
        label="Spread (bps)",
        color="blue",
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Spread (basis points)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.legend(loc="upper left")

    # Volume
    ax2 = ax1.twinx()
    ax2.bar(
        spy_df["timestamp"],
        spy_df["volume"] / 1e6,
        label="Volume (M)",
        color="gray",
        alpha=0.3,
    )
    ax2.set_ylabel("Volume (Millions)", color="gray")
    ax2.tick_params(axis="y", labelcolor="gray")
    ax2.legend(loc="upper right")

    plt.title("SPY Bid-Ask Spread and Volume (Daily, 20d Window)")
    plt.tight_layout()
    plt.savefig("_output/spy_spread_analysis.png", dpi=150, bbox_inches="tight")
    print("SPY analysis plot saved as 'spy_spread_analysis.png'")
    plt.show()

    # Summary statistics
    print("\nSPY Spread Statistics:")
    print(f"Mean spread: {spy_df['spread'].mean()*10000:.2f} bps")
    print(f"Std spread: {spy_df['spread'].std()*10000:.2f} bps")

except Exception as e:
    print(f"Could not fetch Yahoo Finance data: {e}")

print("\nExample completed successfully!")
