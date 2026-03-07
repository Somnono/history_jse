import yfinance as yf
import pandas as pd
from datetime import datetime

def run_analysis():
    """
    Retrieves historical JSE top 10 companies by market cap for each of the last 5 years,
    fetches their historical daily adjusted close prices (max), and exports to CSV.
    Returns a simplified HTML table for Flask deployment (demo purposes).
    """
    # Years to analyze
    current_year = datetime.now().year
    years = [current_year - i for i in range(5)]

    # Top 40 JSE tickers as a starting pool
    top40_tickers = [
        "NPN.JO", "SOL.JO", "BHP.JO", "AGL.JO", "MTN.JO", "SBK.JO", "FMB.JO",
        "GRT.JO", "REM.JO", "IMP.JO", "WHL.JO", "SHP.JO", "VOD.JO", "AGL.JO"
        # ... extend as needed
    ]

    all_records = []

    # Loop through each year to find top 10 by market cap
    for year in years:
        year_end_date = f"{year}-12-31"
        ticker_caps = []

        for ticker_symbol in top40_tickers:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(end=year_end_date, period="1y")
            if hist.empty:
                continue

            close_price = hist["Close"].iloc[-1]  # last price of the year

            try:
                shares_out = ticker.info.get("sharesOutstanding", None)
            except:
                shares_out = None

            if shares_out:
                market_cap = close_price * shares_out
                ticker_caps.append({
                    "Ticker": ticker_symbol,
                    "MarketCap": market_cap,
                    "Company": ticker.info.get("shortName", ""),
                    "Industry": ticker.info.get("industry", ""),
                    "Sector": ticker.info.get("sector", "")
                })

        # Sort descending by market cap, take top 10
        top10 = sorted(ticker_caps, key=lambda x: x["MarketCap"], reverse=True)[:10]

        for t in top10:
            # Fetch max historical adjusted close
            hist_full = yf.Ticker(t["Ticker"]).history(period="max")[["Close"]]
            hist_full.reset_index(inplace=True)
            hist_full["Date"] = hist_full["Date"].dt.strftime("%Y-%m-%d")
            hist_full["Ticker"] = t["Ticker"]
            hist_full["Company"] = t["Company"]
            hist_full["Industry"] = t["Industry"]
            hist_full["Sector"] = t["Sector"]
            hist_full["MarketCapYearEnd"] = round(t["MarketCap"], 2)

            all_records.append(hist_full)

    # Combine all into a single DataFrame
    if not all_records:
        return "<h2>No data available</h2>"

    df = pd.concat(all_records, ignore_index=True)

    # Export to CSV
    df.to_csv("jse_top10_5y.csv", index=False)

    # For Flask demo: show latest prices of last year’s top 10 in table
    latest_year_top10 = df[df["Date"] >= f"{current_year-1}-01-01"].groupby("Ticker").last().reset_index()
    table_html = "<table><tr><th>Ticker</th><th>Company</th><th>Close</th><th>Market Cap</th></tr>"
    for _, row in latest_year_top10.iterrows():
        table_html += f"<tr><td>{row['Ticker']}</td><td>{row['Company']}</td><td>{round(row['Close'],2)}</td><td>{row['MarketCapYearEnd']}</td></tr>"
    table_html += "</table>"

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
            table {{
                margin: 20px auto;
                border-collapse: collapse;
                width: 80%;
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
        <h2>Top 10 Companies by Market Cap - Last Year ({current_year-1})</h2>
        {table_html}
        <p>Data provided via Yahoo Finance | Full CSV exported as jse_top10_5y.csv</p>
    </body>
    </html>
    """
    return html_output