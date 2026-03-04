import yfinance as yf
import pandas as pd

ticker_symbol = "NPN.JO"

ticker = yf.Ticker(ticker_symbol)

data = ticker.history(period="5y")

# Keep only Adjusted Close
data = data[["Close"]]

# Reset index so Date becomes a column
data.reset_index(inplace=True)

print(data.head())