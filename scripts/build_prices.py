import pandas as pd
import yfinance as yf
import time
import os

DATA_PATH = "data"

universe = pd.read_csv(os.path.join(DATA_PATH, "jse_universe.csv"))

tickers = universe["Ticker"].dropna().unique()

records = []

print("Downloading historical prices...")

for ticker in tickers:

    print("Fetching:", ticker)

    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)

        if df.empty:
            continue

        df = df.reset_index()

        for _, row in df.iterrows():

            records.append({
                "Ticker": ticker,
                "Date": row["Date"],
                "Close": row["Close"],
                "Volume": row["Volume"]
            })

    except Exception as e:
        print("Error:", ticker, e)

    time.sleep(0.3)


prices = pd.DataFrame(records)

prices.to_csv(os.path.join(DATA_PATH, "jse_prices.csv"), index=False)

print("\nPrice dataset saved:")
print("data/jse_prices.csv")

print("\nDataset summary:")
print("Rows:", len(prices))
print("Stocks:", prices["Ticker"].nunique())