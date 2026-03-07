import yfinance as yf
import pandas as pd


def run_analysis():

    ticker_symbol = "NPN.JO"

    ticker = yf.Ticker(ticker_symbol)

    data = ticker.history(period="5y")

    if data.empty:
        return "<h2>No data returned from Yahoo Finance</h2>"

    # Keep only Close price
    data = data[["Close"]]

    # Reset index so Date becomes a column
    data.reset_index(inplace=True)

    # Format date nicely
    data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")

    # Get latest price
    latest_price = round(data["Close"].iloc[-1], 2)

    # Show only last 10 rows for cleaner display
    recent_data = data.tail(10)

    html_table = recent_data.to_html(index=False)

    html_output = f"""
    <h1>JSE Market Cap App</h1>
    <h2>Naspers (NPN.JO) - Last 5 Years</h2>
    <h3>Latest Price: {latest_price} ZAR</h3>
    <p>Data provided via Yahoo Finance</p>
    {html_table}
    """

    return html_output