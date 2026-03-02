import yfinance as yf

ticker_symbol = "NPN.JO"  # Naspers on JSE

ticker = yf.Ticker(ticker_symbol)

data = ticker.history(period="1y")

print(data.head())