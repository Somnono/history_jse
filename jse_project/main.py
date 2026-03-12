from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = "data"

# ---------------------------------
# Load datasets safely
# ---------------------------------
def load_data():
    companies_path = os.path.join(DATA_PATH, "jse_universe.csv")
    prices_path = os.path.join(DATA_PATH, "jse_prices.csv")
    splits_path = os.path.join(DATA_PATH, "jse_splits.csv")

    # Load companies
    try:
        companies = pd.read_csv(companies_path)
    except Exception:
        companies = pd.DataFrame(columns=["Ticker", "Company", "Sector", "MarketCap"])

    # Load prices
    try:
        prices = pd.read_csv(prices_path)
        if "Date" in prices.columns:
            prices["Date"] = pd.to_datetime(prices["Date"], errors="coerce")
    except Exception:
        prices = pd.DataFrame(columns=["Ticker", "Date", "Close"])

    # Load splits
    try:
        splits = pd.read_csv(splits_path)
        if "Split Date" in splits.columns:
            splits["Split Date"] = pd.to_datetime(splits["Split Date"], errors="coerce")
    except Exception:
        splits = pd.DataFrame(columns=["Ticker", "Company", "Split Date", "Ratio"])

    return prices, companies, splits

# ---------------------------------
# Market Overview
# ---------------------------------
def market_overview(companies):
    try:
        total_stocks = companies["Ticker"].nunique()
        total_sectors = companies["Sector"].nunique()
        companies["MarketCap"] = pd.to_numeric(companies["MarketCap"], errors="coerce").fillna(0)
        total_marketcap = int(companies["MarketCap"].sum())
    except Exception:
        total_stocks = total_sectors = total_marketcap = 0

    html = f"""
    <div class="overview">
        <div class="card">
            <h3>Stocks Tracked</h3>
            <p>{total_stocks}</p>
        </div>
        <div class="card">
            <h3>Sectors</h3>
            <p>{total_sectors}</p>
        </div>
        <div class="card">
            <h3>Total Market Cap</h3>
            <p>{total_marketcap:,} ZAR</p>
        </div>
    </div>
    """
    return html

# ---------------------------------
# Top companies by market cap
# ---------------------------------
def top_companies(prices, companies):
    df = companies.copy()
    try:
        if not prices.empty:
            latest_prices = prices.sort_values("Date").groupby("Ticker").last().reset_index()[["Ticker", "Close"]]
            df = df.merge(latest_prices, on="Ticker", how="left")
        else:
            df["Close"] = None
    except Exception:
        df["Close"] = None

    df["MarketCap"] = pd.to_numeric(df.get("MarketCap", 0), errors="coerce").fillna(0)
    top_market = df.sort_values("MarketCap", ascending=False).head(10)

    html = """
    <h2>Top 10 Companies by Market Capitalisation</h2>
    <table>
        <tr>
            <th>Ticker</th>
            <th>Company</th>
            <th>Sector</th>
            <th>Close (ZAR)</th>
            <th>Market Cap (ZAR)</th>
        </tr>
    """

    for _, row in top_market.iterrows():
        close_price = f"{row['Close']:.2f}" if pd.notna(row.get("Close")) else "-"
        marketcap = int(row.get("MarketCap", 0))
        html += f"""
        <tr>
            <td>{row.get('Ticker','')}</td>
            <td>{row.get('Company','')}</td>
            <td>{row.get('Sector','')}</td>
            <td>{close_price}</td>
            <td>{marketcap:,}</td>
        </tr>
        """
    html += "</table>"
    return html

# ---------------------------------
# Sector leaders
# ---------------------------------
def sector_leaders(companies):
    df = companies.copy()
    df["MarketCap"] = pd.to_numeric(df.get("MarketCap", 0), errors="coerce").fillna(0)

    html = "<h2>Top 10 Companies per Sector</h2>"
    sectors = sorted(df["Sector"].dropna().unique())

    for sector in sectors:
        sector_df = df[df["Sector"] == sector]
        top_sector = sector_df.sort_values("MarketCap", ascending=False).head(10)
        html += f"<h3>{sector}</h3>"
        html += """
        <table>
            <tr>
                <th>Ticker</th>
                <th>Company</th>
                <th>Market Cap</th>
            </tr>
        """
        for _, row in top_sector.iterrows():
            marketcap = int(row.get("MarketCap", 0))
            html += f"""
            <tr>
                <td>{row.get('Ticker','')}</td>
                <td>{row.get('Company','')}</td>
                <td>{marketcap:,}</td>
            </tr>
            """
        html += "</table>"
    return html

# ---------------------------------
# Latest Daily Prices
# ---------------------------------
def daily_prices(prices):
    html = "<h2>Latest Daily Prices</h2>"
    if prices.empty or not {"Ticker", "Date", "Close"}.issubset(prices.columns):
        return html + "<p>Price data could not be processed.</p>"

    latest_prices = prices.sort_values("Date").groupby("Ticker").last().reset_index()
    html += """
    <table>
        <tr>
            <th>Ticker</th>
            <th>Date</th>
            <th>Close (ZAR)</th>
        </tr>
    """
    for _, row in latest_prices.iterrows():
        date_str = row["Date"].strftime("%Y-%m-%d") if pd.notna(row["Date"]) else "-"
        close_price = f"{row['Close']:.2f}" if pd.notna(row["Close"]) else "-"
        html += f"""
        <tr>
            <td>{row.get('Ticker','')}</td>
            <td>{date_str}</td>
            <td>{close_price}</td>
        </tr>
        """
    html += "</table>"
    return html

# ---------------------------------
# Stock splits
# ---------------------------------
def stock_splits(splits):
    html = "<h2>Historical Stock Splits</h2>"
    if splits.empty or not {"Ticker", "Company", "Split Date", "Ratio"}.issubset(splits.columns):
        return html + "<p>No stock splits data available.</p>"

    html += """
    <table>
        <tr>
            <th>Ticker</th>
            <th>Company</th>
            <th>Split Date</th>
            <th>Ratio</th>
        </tr>
    """
    for _, row in splits.iterrows():
        date_str = row["Split Date"].strftime("%Y-%m-%d") if pd.notna(row["Split Date"]) else "-"
        html += f"""
        <tr>
            <td>{row.get('Ticker','')}</td>
            <td>{row.get('Company','')}</td>
            <td>{date_str}</td>
            <td>{row.get('Ratio','')}</td>
        </tr>
        """
    html += "</table>"
    return html

# ---------------------------------
# Home route
# ---------------------------------
@app.route("/")
def home():
    try:
        prices, companies, splits = load_data()
        overview_html = market_overview(companies)
        companies_html = top_companies(prices, companies)
        sector_html = sector_leaders(companies)
        prices_html = daily_prices(prices)
        splits_html = stock_splits(splits)
    except Exception as e:
        return f"<h1>Application Error</h1><p>{e}</p>"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<title>JSE Market Research Dashboard</title>
<style>
body {{font-family: Arial, sans-serif; background:#f4f6f8; margin:40px; color:#333;}}
.container {{max-width:1100px; margin:auto;}}
h1 {{text-align:center; color:#1f2d3d;}}
.subtitle {{text-align:center; color:#666; margin-bottom:40px;}}
.overview {{display:flex; justify-content:space-between; margin-bottom:40px;}}
.card {{background:white; padding:20px; flex:1; margin:10px; border-radius:6px; box-shadow:0 2px 8px rgba(0,0,0,0.1); text-align:center;}}
table {{width:100%; border-collapse:collapse; background:white; box-shadow:0 3px 10px rgba(0,0,0,0.1); margin-bottom:40px;}}
th, td {{padding:10px; border:1px solid #ddd; text-align:center;}}
th {{background:#2c3e50; color:white;}}
tr:nth-child(even) {{background:#f2f2f2;}}
.footer {{text-align:center; margin-top:30px; font-size:14px; color:#666;}}
</style>
</head>
<body>
<div class="container">
<h1>JSE Market Research Dashboard</h1>
<div class="subtitle">
Historical equity dataset built from Yahoo Finance for Johannesburg Stock Exchange companies
</div>
{overview_html}
{companies_html}
{sector_html}
{prices_html}
{splits_html}
<div class="footer">
Data Source: Yahoo Finance<br>
Research Project: JSE Sector & Market Capitalisation Analysis
</div>
</div>
</body>
</html>
"""
    return html

# ---------------------------------
# Run server
# ---------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)