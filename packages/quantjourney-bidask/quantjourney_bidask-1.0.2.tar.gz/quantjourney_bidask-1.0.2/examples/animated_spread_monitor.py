#!/usr/bin/env python3
"""
Animated Spread Monitor.

Creates animated visualizations of bid-ask spread evolution over time with
real-time websocket data streaming capabilities.

Author: Jakub Polec
Date: 2025-06-28

Part of the QuantJourney framework - The framework with advanced quantitative 
finance tools and insights.
"""

import os
import sys

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add parent directory to path for both installed and development mode
try:
    from quantjourney_bidask import edge_rolling
except ImportError:
    # Development mode - add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from quantjourney_bidask import edge_rolling

from data.fetch import DataFetcher, get_stock_data


def create_animated_spread_plot(df, window=20, save_gif=True):
    """Create animated plot showing spread evolution over time.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with OHLC data and timestamp
    window : int
        Rolling window for spread calculation
    save_gif : bool
        Whether to save as animated GIF

    """
    # Calculate spreads
    df = df.copy()
    df["spread"] = edge_rolling(df, window=window)

    # Set up the figure and axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Initialize empty plots
    (line1,) = ax1.plot([], [], "b-", label="Price", linewidth=2)
    (line2,) = ax2.plot([], [], "r-", label="Spread (%)", linewidth=2)

    # Set axis properties
    ax1.set_xlim(df["timestamp"].min(), df["timestamp"].max())
    ax1.set_ylim(df["close"].min() * 0.95, df["close"].max() * 1.05)
    ax1.set_ylabel("Price")
    ax1.set_title("Real-Time Price and Spread Monitor")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.set_xlim(df["timestamp"].min(), df["timestamp"].max())
    spread_max = df["spread"].max() * 100 * 1.2
    ax2.set_ylim(0, max(spread_max, 0.1))
    ax2.set_ylabel("Spread (%)")
    ax2.set_xlabel("Time")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # Animation function
    def animate(frame):
        # Get data up to current frame
        current_data = df.iloc[: frame + 20]  # Show at least 20 points

        if len(current_data) > 0:
            # Update price line
            line1.set_data(current_data["timestamp"], current_data["close"])

            # Update spread line
            valid_spread = current_data.dropna(subset=["spread"])
            if len(valid_spread) > 0:
                line2.set_data(valid_spread["timestamp"], valid_spread["spread"] * 100)

                # Update fill (for visual appeal)
                ax2.collections.clear()  # Clear previous fill
                ax2.fill_between(
                    valid_spread["timestamp"],
                    0,
                    valid_spread["spread"] * 100,
                    alpha=0.3,
                    color="red",
                )

        # Update title with current values
        if frame < len(df):
            current_price = df.iloc[frame]["close"]
            current_spread = df.iloc[frame]["spread"]
            if not pd.isna(current_spread):
                ax1.set_title(
                    f"Price: ${current_price:.2f} | "
                    f"Spread: {current_spread*100:.3f}% | "
                    f"Frame: {frame+1}/{len(df)}"
                )

        return line1, line2

    # Create animation
    frames = min(len(df), 200)  # Limit frames for performance
    ani = animation.FuncAnimation(
        fig, animate, frames=frames, interval=100, blit=False, repeat=True
    )

    if save_gif:
        print("Saving animated GIF (this may take a moment)...")
        ani.save("animated_spread_monitor.gif", writer="pillow", fps=10)
        print("Animation saved as 'animated_spread_monitor.gif'")

    plt.tight_layout()
    plt.show()

    return ani


def create_crypto_spread_comparison():
    """Create animated comparison of spreads across different crypto assets."""
    print("Creating Multi-Crypto Spread Comparison")
    print("=====================================")

    # Generate synthetic data for multiple "crypto" assets with
    # different characteristics
    np.random.seed(42)
    n = 150

    # Create different assets with varying spread characteristics
    assets = {
        "BTC-like": {
            "base_spread": 0.002,
            "volatility": 0.03,
            "price": 50000,
        },  # Low spread, high price
        "ETH-like": {
            "base_spread": 0.004,
            "volatility": 0.04,
            "price": 3000,
        },  # Medium spread
        "ALT-like": {
            "base_spread": 0.015,
            "volatility": 0.08,
            "price": 100,
        },  # High spread, volatile
        "STABLE-like": {
            "base_spread": 0.0005,
            "volatility": 0.001,
            "price": 1,
        },  # Very low spread, stable
    }

    all_data = []

    for asset_name, params in assets.items():
        # Generate price series
        returns = np.random.normal(0, params["volatility"], n)
        prices = params["price"] * np.exp(np.cumsum(returns))

        # Generate spreads that vary with volatility
        volatility_factor = np.abs(returns) / params["volatility"]
        spread_multiplier = (
            1 + 2 * volatility_factor
        )  # Higher spreads during volatile periods
        spread_pct = params["base_spread"] * spread_multiplier

        # Create OHLC data
        open_prices = prices
        high_prices = prices * (1 + np.random.uniform(0, spread_pct / 2, n))
        low_prices = prices * (1 - np.random.uniform(0, spread_pct / 2, n))
        close_prices = prices + np.random.normal(0, params["price"] * 0.0001, n)

        df = pd.DataFrame(
            {
                "open": open_prices,
                "high": high_prices,
                "low": low_prices,
                "close": close_prices,
                "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min"),
                "symbol": asset_name,
            }
        )

        # Calculate spreads
        df["spread"] = edge_rolling(df, window=20)
        all_data.append(df)

    # Combine data
    combined_df = pd.concat(all_data, ignore_index=True)

    # Create comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()

    colors = ["blue", "green", "red", "orange"]

    for i, (asset_name, color) in enumerate(zip(assets.keys(), colors)):
        asset_data = combined_df[combined_df["symbol"] == asset_name]

        # Normalize prices for comparison (plot as percentage change)
        price_pct = (asset_data["close"] / asset_data["close"].iloc[0] - 1) * 100

        # Price plot
        axes[i].plot(
            asset_data["timestamp"],
            price_pct,
            color=color,
            alpha=0.7,
            label="Price Change (%)",
        )
        ax2_twin = axes[i].twinx()
        ax2_twin.plot(
            asset_data["timestamp"],
            asset_data["spread"] * 100,
            color="red",
            linewidth=2,
            label="Spread (%)",
        )

        axes[i].set_title(f"{asset_name} Price vs Spread")
        axes[i].set_ylabel("Price Change (%)", color=color)
        ax2_twin.set_ylabel("Spread (%)", color="red")
        axes[i].grid(True, alpha=0.3)

        # Add statistics
        mean_spread = asset_data["spread"].mean() * 100
        std_spread = asset_data["spread"].std() * 100
        axes[i].text(
            0.02,
            0.98,
            f"Avg: {mean_spread:.3f}%\nStd: {std_spread:.3f}%",
            transform=axes[i].transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

    plt.suptitle("Crypto Asset Spread Comparison (Synthetic Data)", fontsize=16)
    plt.tight_layout()
    plt.savefig("_output/crypto_spread_comparison.png", dpi=150, bbox_inches="tight")
    print("Comparison plot saved as 'crypto_spread_comparison.png'")
    plt.show()

    # Summary statistics
    print("\nSpread Statistics Summary:")
    print("-" * 50)
    for asset_name in assets:
        asset_data = combined_df[combined_df["symbol"] == asset_name]
        mean_spread = asset_data["spread"].mean() * 10000  # in basis points
        std_spread = asset_data["spread"].std() * 10000
        min_spread = asset_data["spread"].min() * 10000
        max_spread = asset_data["spread"].max() * 10000

        print(
            f"{asset_name:12}: Mean={mean_spread:6.1f}bps, "
            f"Std={std_spread:6.1f}bps, "
            f"Range=[{min_spread:5.1f}, {max_spread:5.1f}]bps"
        )

    return combined_df


if __name__ == "__main__":
    print("Animated Spread Monitor Examples")
    print("===============================")

    # Example 1: Synthetic data animation
    print("\n1. Creating synthetic animated spread monitor...")
    np.random.seed(42)
    n = 100

    # Generate synthetic data with time-varying spreads
    base_price = 100
    volatility = 0.02 * (
        1 + 0.3 * np.sin(np.linspace(0, 4 * np.pi, n))
    )  # Varying volatility
    returns = np.random.normal(0, volatility)
    prices = base_price * np.exp(np.cumsum(returns))

    # Spreads correlate with volatility
    spread_base = 0.003
    spread_multiplier = 1 + 2 * (volatility / 0.02 - 1)
    spread_pct = spread_base * spread_multiplier

    synthetic_df = pd.DataFrame(
        {
            "open": prices,
            "high": prices * (1 + np.random.uniform(0, spread_pct / 2, n)),
            "low": prices * (1 - np.random.uniform(0, spread_pct / 2, n)),
            "close": prices + np.random.normal(0, 0.01, n),
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="15min"),
        }
    )

    # Create static version (animation requires display)
    synthetic_df["spread"] = edge_rolling(synthetic_df, window=20)

    # Create static plots showing the concept
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(
        synthetic_df["timestamp"],
        synthetic_df["close"],
        "b-",
        linewidth=2,
        label="Price",
    )
    ax1.set_ylabel("Price")
    ax1.set_title("Simulated Real-Time Price and Spread Evolution")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.plot(
        synthetic_df["timestamp"],
        synthetic_df["spread"] * 100,
        "r-",
        linewidth=2,
        label="Spread (%)",
    )
    ax2.fill_between(
        synthetic_df["timestamp"],
        0,
        synthetic_df["spread"] * 100,
        alpha=0.3,
        color="red",
    )
    ax2.set_ylabel("Spread (%)")
    ax2.set_xlabel("Time")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig("_output/simulated_realtime_monitor.png", dpi=150, bbox_inches="tight")
    print("Static version saved as 'simulated_realtime_monitor.png'")
    plt.show()

    # Example 2: Multi-crypto comparison
    print("\n2. Creating multi-crypto spread comparison...")
    crypto_data = create_crypto_spread_comparison()

    # Example 3: Real data (if available)
    print("\n3. Testing with real market data...")
    try:
        real_df = get_stock_data("SPY", period="5d", interval="1h")

        real_df["spread"] = edge_rolling(real_df, window=12)  # 12-hour window

        # Create real data visualization
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))

        ax1.plot(real_df["timestamp"], real_df["close"], "b-", linewidth=1.5)
        ax1.set_ylabel("SPY Price ($)")
        ax1.set_title("SPY Real-Time Spread Monitor (Last 5 Days, Hourly)")
        ax1.grid(True, alpha=0.3)

        valid_spreads = real_df.dropna(subset=["spread"])
        ax2.plot(
            valid_spreads["timestamp"],
            valid_spreads["spread"] * 10000,
            "r-",
            linewidth=1.5,
        )
        ax2.set_ylabel("Spread (basis points)")
        ax2.set_xlabel("Date/Time")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("_output/spy_realtime_monitor.png", dpi=150, bbox_inches="tight")
        print("SPY real-time monitor saved as 'spy_realtime_monitor.png'")
        plt.show()

        print(
            f"SPY spread stats: Mean={valid_spreads['spread'].mean()*10000:.2f}bps, "
            f"Std={valid_spreads['spread'].std()*10000:.2f}bps"
        )

    except Exception as e:
        print(f"Could not fetch real data: {e}")

    # Example 4: Real-time websocket data (demonstration)
    print("\n4. Testing websocket data stream...")
    try:
        import asyncio

        async def demo_websocket_stream():
            fetcher = DataFetcher()
            print("\nStarting EXTENDED BTC real-time data stream for 30 seconds...")
            print(
                "This will show actual price movements and "
                "spread changes over time"
            )
            btc_stream = await fetcher.get_btc_1m_websocket(duration_seconds=30)

            if not btc_stream.empty:
                print(
                    f"Received {len(btc_stream)} data points from real-time stream"
                )

                # Calculate price statistics
                start_price = btc_stream["price"].iloc[0]
                end_price = btc_stream["price"].iloc[-1]
                price_change = end_price - start_price
                price_change_pct = (price_change / start_price) * 100
                min_price = btc_stream["price"].min()
                max_price = btc_stream["price"].max()

                print("\nPRICE ANALYSIS:")
                print(f"   Start: ${start_price:.2f}")
                print(f"   End:   ${end_price:.2f}")
                print(f"   Change: ${price_change:+.2f} ({price_change_pct:+.3f}%)")
                print(f"   Range: ${min_price:.2f} - ${max_price:.2f}")

                # Create enhanced visualization
                fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))

                # Price plot with trend line
                ax1.plot(
                    btc_stream["timestamp"],
                    btc_stream["price"],
                    "b-",
                    linewidth=2,
                    label="BTC Price",
                )
                ax1.axhline(
                    y=start_price,
                    color="gray",
                    linestyle="--",
                    alpha=0.5,
                    label=f"Start: ${start_price:.2f}",
                )
                ax1.set_title(
                    f"BTC Real-Time Price Movement (30s) - Change: {price_change_pct:+.3f}%"
                )
                ax1.set_ylabel("Price (USDT)")
                ax1.grid(True, alpha=0.3)
                ax1.legend()

                # Spread plot
                ax2.plot(
                    btc_stream["timestamp"],
                    btc_stream["spread"] * 10000,
                    "r-",
                    linewidth=2,
                )
                ax2.fill_between(
                    btc_stream["timestamp"],
                    0,
                    btc_stream["spread"] * 10000,
                    alpha=0.3,
                    color="red",
                )
                avg_spread = btc_stream["spread"].mean() * 10000
                ax2.axhline(
                    y=avg_spread,
                    color="darkred",
                    linestyle="--",
                    label=f"Avg: {avg_spread:.2f}bps",
                )
                ax2.set_title("BTC Spread Evolution (Real-time)")
                ax2.set_ylabel("Spread (basis points)")
                ax2.grid(True, alpha=0.3)
                ax2.legend()

                # Price change over time
                price_changes = (btc_stream["price"] / start_price - 1) * 100
                ax3.plot(btc_stream["timestamp"], price_changes, "g-", linewidth=2)
                ax3.fill_between(
                    btc_stream["timestamp"],
                    0,
                    price_changes,
                    alpha=0.3,
                    color="green" if price_change_pct > 0 else "red",
                )
                ax3.axhline(y=0, color="black", linestyle="-", alpha=0.3)
                ax3.set_title("Cumulative Price Change (%)")
                ax3.set_ylabel("Change (%)")
                ax3.set_xlabel("Time")
                ax3.grid(True, alpha=0.3)

                plt.tight_layout()
                plt.savefig(
                    "_output/btc_extended_realtime_demo.png",
                    dpi=150,
                    bbox_inches="tight",
                )
                print(
                    "\nEnhanced real-time demo saved as "
                    "'btc_extended_realtime_demo.png'"
                )
                plt.show()

                # Spread statistics
                min_spread = btc_stream["spread"].min() * 10000
                max_spread = btc_stream["spread"].max() * 10000

                print("\nSPREAD ANALYSIS:")
                print(f"   Average: {avg_spread:.2f} bps")
                print(f"   Range: {min_spread:.2f} - {max_spread:.2f} bps")
                print(f"   Volatility: {btc_stream['spread'].std() * 10000:.2f} bps")

                # Check if it's real or synthetic data
                # Check if data is synthetic (unused variable removed)
                data_source = (
                    "synthetic (fallback)"
                    if "synthetic" in str(btc_stream.iloc[0].get("source", ""))
                    else "real exchange data"
                )
                print(f"\n🔍 Data source: {data_source}")

            else:
                print(
                    "No data received - check network connection or "
                    "CCXT installation"
                )

        # Run the async websocket demo
        asyncio.run(demo_websocket_stream())

    except Exception as e:
        print(f"Websocket demo error: {e}")
