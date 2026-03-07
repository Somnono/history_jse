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

    # Show only last 10 rows for cleaner display
    recent_data = data.tail(10)

    # Add change column for coloring
    recent_data["Change"] = recent_data["Close"].diff()

    # Function to color gains/losses
    def colorize(val):
        if val > 0:
            return 'background-color: #d4f8d4;'  # light green for gains
        elif val < 0:
            return 'background-color: #f8d4d4;'  # light red for losses
        else:
            return ''

    # Apply styling to Close column
    styled_table = recent_data.style.applymap(colorize, subset=["Close"]).hide_index().render()

    # Get latest price
    latest_price = round(data["Close"].iloc[-1], 2)

    # Build full HTML page
    html_output = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JSE Market Cap App</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            margin: 40px;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
        }}
        h2 {{
            color: #34495e;
            text-align: center;
        }}
        h3 {{
            color: #16a085;
            text-align: center;
        }}
        table {{
            margin: 20px auto;
            border-collapse: collapse;
            width: 60%;
            background-color: #fff;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #ccc;
            text-align: center;
        }}
        th {{
            background-color: #2c3e50;
            color: #fff;
        }}
        p {{
            text-align: center;
            font-size: 0.9em;
            color: #555;
        }}
    </style>
</head>
<body>
    <h1>JSE Market Cap App</h1>
    <h2>Naspers (NPN.JO) - Last 5 Years</h2>
    <h3>Latest Price: {latest_price} ZAR</h3>
    <p>Data provided via Yahoo Finance</p>
    {styled_table}
</body>
</html>
"""
    return html_output