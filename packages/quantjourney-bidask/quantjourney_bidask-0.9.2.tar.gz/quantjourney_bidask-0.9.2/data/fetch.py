"""
Simplified data fetcher for quantjourney_bidask examples and tests.
"""

import asyncio
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, timezone
import time
from typing import List, Optional, Dict
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import ccxt.async_support as ccxt_async
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    logger.warning("CCXT not available - crypto features will use synthetic data")

class DataFetcher:
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"DataFetcher initialized: data_dir={data_dir}")
    
    async def get_btc_1m_websocket(self, exchange_name: str = "binance", duration_seconds: int = 60):
        """Get 1m BTC data via websocket - simplified for examples."""
        if not CCXT_AVAILABLE:
            logger.info("Using synthetic BTC data")
            return self._generate_synthetic_btc_stream(duration_seconds)
        
        try:
            exchange_class = getattr(ccxt_async, exchange_name.lower())
            exchange = exchange_class({'enableRateLimit': True, 'timeout': 30000})
            await exchange.load_markets()
            
            data_points = []
            symbol = 'BTC/USDT'
            
            logger.info(f"Starting BTC websocket stream for {duration_seconds}s")
            for i in range(duration_seconds):
                try:
                    ticker = await exchange.watch_ticker(symbol)
                    data_points.append({
                        'timestamp': pd.to_datetime(ticker['timestamp'], unit='ms', utc=True),
                        'symbol': 'BTCUSDT',
                        'price': float(ticker['close']),
                        'volume': float(ticker['baseVolume']) if ticker.get('baseVolume') else 0,
                        'bid': float(ticker['bid']) if ticker.get('bid') else None,
                        'ask': float(ticker['ask']) if ticker.get('ask') else None,
                        'spread': float(ticker['ask'] - ticker['bid']) if ticker.get('ask') and ticker.get('bid') else None
                    })
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Ticker error: {e}")
                    break
            
            await exchange.close()
            
            # If no data collected, use synthetic data
            if not data_points:
                logger.info("No real data collected, falling back to synthetic")
                return self._generate_synthetic_btc_stream(duration_seconds)
            
            logger.info(f"Collected {len(data_points)} data points")
            return pd.DataFrame(data_points)
            
        except Exception as e:
            logger.error(f"Websocket error: {e}")
            return self._generate_synthetic_btc_stream(duration_seconds)
    
    async def get_historical_crypto_data(self, symbol: str = "BTC/USDT", exchange: str = "binance", 
                                       timeframe: str = "1m", limit: int = 100):
        """Get historical crypto data."""
        if not CCXT_AVAILABLE:
            return self._generate_synthetic_historical_data(symbol, limit)
        
        try:
            exchange_class = getattr(ccxt_async, exchange.lower())
            exchange_instance = exchange_class({'enableRateLimit': True, 'timeout': 30000})
            await exchange_instance.load_markets()
            
            ohlcv = await exchange_instance.fetch_ohlcv(symbol, timeframe, limit=limit)
            await exchange_instance.close()
            
            if not ohlcv:
                logger.warning(f"No historical data for {symbol}")
                return self._generate_synthetic_historical_data(symbol, limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            df['symbol'] = symbol.replace('/', '')
            
            logger.info(f"Fetched {len(df)} historical data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Historical data error: {e}")
            return self._generate_synthetic_historical_data(symbol, limit)
    
    def get_stock_data(self, ticker: str, period: str = "1mo", interval: str = "1d"):
        """Get stock data via yfinance."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No stock data for {ticker}")
                return pd.DataFrame()
            
            df = df.reset_index()
            df['timestamp'] = pd.to_datetime(df['Date'], utc=True) if 'Date' in df.columns else pd.to_datetime(df['Datetime'], utc=True)
            df['symbol'] = ticker
            df.columns = [col.lower() for col in df.columns]
            
            cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in cols if col in df.columns]]
            
            logger.info(f"Fetched {len(df)} stock data points for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Stock data error for {ticker}: {e}")
            return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, filename: str):
        """Save data to CSV."""
        if not filename.endswith('.csv'):
            filename += '.csv'
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            df.to_csv(filepath, index=False)
            logger.info(f"Data saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Save error: {e}")
            raise
    
    def load_data(self, filename: str):
        """Load data from CSV."""
        if not filename.endswith('.csv'):
            filename += '.csv'
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            df = pd.read_csv(filepath)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            logger.info(f"Data loaded from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Load error: {e}")
            raise
    
    def _generate_synthetic_btc_stream(self, duration_seconds: int):
        """Generate synthetic BTC stream data for testing."""
        base_price = 45000
        data_points = []
        current_time = datetime.now(timezone.utc)
        
        for i in range(duration_seconds):
            # Add some realistic price movement
            price_change = np.random.normal(0, base_price * 0.0001)
            price = max(base_price + price_change, 1000)  # Ensure price doesn't go negative
            spread = price * 0.0001  # 0.01% spread
            
            data_points.append({
                'timestamp': current_time + timedelta(seconds=i),
                'symbol': 'BTCUSDT',
                'price': price,
                'volume': np.random.uniform(100, 1000),
                'bid': price - spread/2,
                'ask': price + spread/2,
                'spread': spread
            })
            base_price = price  # Use current price as base for next
        
        logger.info(f"Generated {len(data_points)} synthetic BTC data points")
        return pd.DataFrame(data_points)
    
    def _generate_synthetic_historical_data(self, symbol: str, limit: int):
        """Generate synthetic historical OHLCV data."""
        base_price = 45000 if 'BTC' in symbol.upper() else 2500
        data_points = []
        current_time = datetime.now(timezone.utc) - timedelta(minutes=limit)
        
        for i in range(limit):
            # Generate realistic OHLCV data
            price_change = np.random.normal(0, base_price * 0.005)
            close_price = max(base_price + price_change, 1)
            
            open_price = base_price
            high_price = max(open_price, close_price) * (1 + np.random.uniform(0, 0.002))
            low_price = min(open_price, close_price) * (1 - np.random.uniform(0, 0.002))
            volume = np.random.uniform(1000, 10000)
            
            data_points.append({
                'timestamp': current_time + timedelta(minutes=i),
                'symbol': symbol.replace('/', ''),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
            base_price = close_price
        
        logger.info(f"Generated {len(data_points)} synthetic historical data points")
        return pd.DataFrame(data_points)

# Convenience functions for backward compatibility
async def get_crypto_data(symbol: str = "BTC/USDT", exchange: str = "binance", timeframe: str = "1m", limit: int = 100):
    """Quick function to get crypto data."""
    fetcher = DataFetcher()
    return await fetcher.get_historical_crypto_data(symbol, exchange, timeframe, limit)

def get_stock_data(ticker: str, period: str = "1mo", interval: str = "1d"):
    """Quick function to get stock data."""
    fetcher = DataFetcher()
    return fetcher.get_stock_data(ticker, period, interval)

async def stream_btc_data(duration_seconds: int = 60):
    """Quick function to stream BTC data."""
    fetcher = DataFetcher()
    return await fetcher.get_btc_1m_websocket(duration_seconds=duration_seconds)

async def main():
    """Example usage."""
    fetcher = DataFetcher()
    
    print("Testing BTC websocket stream...")
    btc_stream = await fetcher.get_btc_1m_websocket(duration_seconds=10)
    print(f"BTC stream: {len(btc_stream)} rows")
    if not btc_stream.empty:
        print(btc_stream.head())
    
    print("\nTesting historical crypto data...")
    hist_data = await fetcher.get_historical_crypto_data('BTC/USDT', limit=20)
    print(f"Historical data: {len(hist_data)} rows")
    if not hist_data.empty:
        print(hist_data.head())
    
    print("\nTesting stock data...")
    stock_data = fetcher.get_stock_data('AAPL', period='5d')
    print(f"Stock data: {len(stock_data)} rows")
    if not stock_data.empty:
        print(stock_data.head())

if __name__ == "__main__":
    asyncio.run(main())