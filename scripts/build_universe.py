import sys
import os
import yfinance as yf
import pandas as pd
import time

# Allow script to see project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from jse_project.universe import JSE_UNIVERSE

print("Building JSE universe dataset...")

records = []

for ticker_symbol in JSE_UNIVERSE:

    print("Fetching:", ticker_symbol)

    ticker = yf.Ticker(ticker_symbol)

    try:
        info = ticker.info
        hist = ticker.history(period="1d")

        if hist.empty:
            continue

        latest_close = hist["Close"].iloc[-1]
        latest_volume = hist["Volume"].iloc[-1]
        latest_date = hist.index[-1]

    except Exception as e:
        print("Skipping:", ticker_symbol)
        continue

    records.append({
        "Ticker": ticker_symbol,
        "Company": info.get("shortName", ""),
        "Sector": info.get("sector", ""),
        "Industry": info.get("industry", ""),
        "MarketCap": info.get("marketCap", ""),
        "Close": latest_close,
        "Volume": latest_volume,
        "Date": latest_date
    })

    # Prevent Yahoo blocking requests
    time.sleep(0.5)

df = pd.DataFrame(records)

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

df.to_csv("data/jse_universe.csv", index=False)

print("\nUniverse dataset saved:")
print("data/jse_universe.csv")

print("\nDataset summary:")
print("Stocks collected:", len(df))
print("Sectors:", df["Sector"].nunique())