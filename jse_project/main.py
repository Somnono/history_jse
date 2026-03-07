import yfinance as yf
import pandas as pd

def run_analysis():

    ticker_symbol = "NPN.JO"

    ticker = yf.Ticker(ticker_symbol)

    data = ticker.history(period="5y")

    data = data[["Close"]]

    data.reset_index(inplace=True)

    return data.to_html()