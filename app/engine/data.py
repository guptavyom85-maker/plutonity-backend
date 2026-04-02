# app/engine/data.py
import yfinance as yf
import pandas as pd

# These are the tickers we support
# yfinance uses .NS suffix for NSE stocks
# .BO suffix for BSE stocks
SUPPORTED_TICKERS = {
    # Large cap NSE stocks
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "WIPRO": "WIPRO.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "SBIN": "SBIN.NS",
    "ICICIBANK": "ICICIBANK.NS",
    # Indices
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANKNIFTY": "^NSEBANK"
}

def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Downloads historical OHLCV data for an NSE stock.
    
    Returns a DataFrame with columns:
    Open, High, Low, Close, Volume
    Index is the date.
    
    OHLCV = Open, High, Low, Close, Volume
    These are the 5 standard price points for each trading day.
    """

    # Get the yfinance symbol
    symbol = SUPPORTED_TICKERS.get(ticker.upper())

    if not symbol:
        raise ValueError(f"Ticker '{ticker}' not supported. Supported: {list(SUPPORTED_TICKERS.keys())}")

    # Download from Yahoo Finance
    df = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        progress=False    # don't print download progress bar
    )

    if df.empty:
        raise ValueError(f"No data found for {ticker} between {start_date} and {end_date}")

    # Clean up
    # yfinance sometimes returns multi-level columns, flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Keep only what we need
    
    df.dropna(inplace=True)

    # Validate minimum data
    if len(df) < 60:
        raise ValueError(f"Not enough data. Got {len(df)} days, need at least 60.")

    return df


def validate_dates(start_date: str, end_date: str):
    """Basic date validation before we even download data."""
    from datetime import datetime

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    if start >= end:
        raise ValueError("start_date must be before end_date")

    if (end - start).days < 60:
        raise ValueError("Date range must be at least 60 days")

    # Don't allow future dates
    if end > datetime.now():
        raise ValueError("end_date cannot be in the future")