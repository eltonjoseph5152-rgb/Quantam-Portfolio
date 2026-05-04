import yfinance as yf
import pandas as pd
import datetime
import sys

def fetch_data(tickers, start_date=None, end_date=None):
    """
    Fetches adjusted close prices for given tickers over the last 1 year.
    Exits gracefully if the network is down or tickers are invalid.
    """
    if end_date is None:
        end_date = datetime.date.today()
    if start_date is None:
        start_date = end_date - datetime.timedelta(days=365)
        
    print(f"Fetching data for {tickers} from {start_date} to {end_date}...")
    
    try:
        data = yf.download(tickers, start=start_date, end=end_date)['Close']
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)
    
    if data.empty or data.shape[0] < 30:
        print("[ERROR] Insufficient data returned. Check ticker symbols and date range.")
        sys.exit(1)
    
    # Clean data: fill missing values using forward fill, then drop any remaining
    data = data.ffill().dropna()
    print("Data successfully fetched!")
    return data
