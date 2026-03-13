import yfinance as yf
import pandas as pd

tickers = [
"NPN.JO","CPI.JO","SBK.JO","BTI.JO"
]

rows = []

for ticker_symbol in tickers:

    ticker = yf.Ticker(ticker_symbol)

    splits = ticker.splits

    if splits.empty:
        continue

    for date, ratio in splits.items():

        rows.append({
            "Ticker": ticker_symbol,
            "Company": ticker_symbol,
            "Split Date": date,
            "Ratio": ratio
        })

df = pd.DataFrame(rows)

df.to_csv("data/jse_splits.csv", index=False)

print("Splits file created")