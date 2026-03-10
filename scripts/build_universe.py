import sys
import os

# Allow script to see the project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import yfinance as yf
import pandas as pd
import time

from jse_project.universe import JSE_UNIVERSE

print("Building JSE universe dataset...")

records = []

for ticker_symbol in JSE_UNIVERSE:

    print("Fetching:", ticker_symbol)

    ticker = yf.Ticker(ticker_symbol)

    try:
        info = ticker.info
    except:
        continue

    records.append({
        "Ticker": ticker_symbol,
        "Company": info.get("shortName", ""),
        "Sector": info.get("sector", ""),
        "Industry": info.get("industry", ""),
        "MarketCap": info.get("marketCap", "")
    })

    # Prevent Yahoo blocking requests
    time.sleep(0.5)

df = pd.DataFrame(records)

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

df.to_csv("data/jse_universe.csv", index=False)

print("Universe dataset saved:")
print("data/jse_universe.csv")