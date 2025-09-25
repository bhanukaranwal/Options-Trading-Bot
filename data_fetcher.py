import pandas as pd
import numpy as np
import argparse
import logging
from datetime import datetime, timedelta

from financial_math import black_scholes_greeks

def generate_sample_options_data(days=365, symbol="NIFTY", initial_price=25000):
    """
    Generates a realistic but simulated 1-minute options data CSV for backtesting.
    """
    logging.info(f"Generating {days} days of 1-minute sample data for {symbol}...")
    
    start_date = datetime.now() - timedelta(days=days)
    minutes = days * 24 * 60
    timestamps = pd.to_datetime(pd.date_range(start=start_date, periods=minutes, freq='T'))
    
    # Simulate underlying price movement (Geometric Brownian Motion)
    drift = 0.05 / (365 * 24 * 60) # 5% annual drift
    volatility = 0.20 / np.sqrt(365 * 24 * 60) # 20% annual volatility
    returns = np.exp(drift + volatility * np.random.randn(minutes))
    underlying_prices = initial_price * returns.cumprod()

    # Create a base DataFrame
    df = pd.DataFrame({'timestamp': timestamps, 'underlying_price': underlying_prices})
    df.set_index('timestamp', inplace=True)
    df.rename(columns={'underlying_price': 'close'}, inplace=True)
    
    # Simulate OHLC
    df['open'] = df['close'].shift(1)
    df['high'] = df[['open', 'close']].max(axis=1) + np.random.uniform(0, 5, size=len(df))
    df['low'] = df[['open', 'close']].min(axis=1) - np.random.uniform(0, 5, size=len(df))
    df.dropna(inplace=True)
    
    # For simplicity in this example, we won't generate a full options chain.
    # The backtester will use this underlying price data and a strategy
    # that dynamically calculates option prices. For a more advanced simulation,
    # you would generate data for multiple strikes and expiries.
    
    filepath = "nifty_options_data.csv"
    df.to_csv(filepath)
    logging.info(f"Sample data saved to {filepath}")
    return df

def load_historical_data(filepath):
    """Loads historical data from a CSV file into a pandas DataFrame."""
    try:
        logging.info(f"Loading historical data from {filepath}...")
        df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)
        # Ensure standard column names for backtrader
        df.rename(columns={'close': 'close', 'open': 'open', 'high': 'high', 'low': 'low'}, inplace=True)
        df['volume'] = 0  # Add dummy volume if not present
        df['openinterest'] = 0 # Add dummy open interest
        return df
    except FileNotFoundError:
        logging.error(f"Data file not found at {filepath}. Please generate it first.")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data Fetcher Utility")
    parser.add_argument('--generate-sample-data', action='store_true',
                        help="Generate a sample CSV file with NIFTY options data.")
    args = parser.parse_args()
    
    if args.generate_sample_data:
        generate_sample_options_data()
