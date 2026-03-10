import sys
import os

# Allow access to project modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import yfinance as yf
import pandas as pd
import time
from datetime import datetime

from jse_project.universe import JSE_UNIVERSE

print("Building JSE dataset with daily prices...")

records = []

for ticker_symbol in JSE_UNIVERSE:

    print("Fetching history:", ticker_symbol)

    ticker = yf.Ticker(ticker_symbol)

    try:
        hist = ticker.history(period="max")
    except:
        print("Failed:", ticker_symbol)
        continue

    if hist.empty:
        print("No data:", ticker_symbol)
        continue

    hist.reset_index(inplace=True)

    try:
        info = ticker.info
        company = info.get("shortName", "")
        sector = info.get("sector", "")
        industry = info.get("industry", "")
        shares = info.get("sharesOutstanding", None)
    except:
        company = ""
        sector = ""
        industry = ""
        shares = None

    for _, row in hist.iterrows():

        market_cap = None

        if shares:
            market_cap = row["Close"] * shares

        records.append({
            "Date": row["Date"],
            "Ticker": ticker_symbol,
            "Company": company,
            "Sector": sector,
            "Industry": industry,
            "Open": row["Open"],
            "High": row["High"],
            "Low": row["Low"],
            "Close": row["Close"],
            "Volume": row["Volume"],
            "Split": row.get("Stock Splits", 0),
            "MarketCap": market_cap
        })

    # Prevent Yahoo API throttling
    time.sleep(0.5)

print("Creating DataFrame...")

df = pd.DataFrame(records)

# Ensure Date column is formatted correctly
df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

# Split datasets for deployment efficiency
prices_df = df[[
    "Date",
    "Ticker",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Split"
]]

companies_df = df[[
    "Ticker",
    "Company",
    "Sector",
    "Industry",
    "MarketCap"
]].drop_duplicates(subset="Ticker")

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Save datasets
prices_df.to_csv("data/jse_prices.csv", index=False)
companies_df.to_csv("data/jse_companies.csv", index=False)

print("Dataset build complete.")
print("Saved files:")
print("data/jse_prices.csv")
print("data/jse_companies.csv")