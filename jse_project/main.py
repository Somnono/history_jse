from flask import Flask
import pandas as pd
import os

app = Flask(__name__)
DATA_PATH = "data"

# -----------------------------
# Safe numeric formatting
# -----------------------------
def safe_float_format(value):
    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return "-"

# -----------------------------
# Load datasets safely
# -----------------------------
def load_data():
    companies_path = os.path.join(DATA_PATH, "jse_universe.csv")
    prices_path = os.path.join(DATA_PATH, "jse_prices.csv")
    splits_path = os.path.join(DATA_PATH, "jse_splits.csv")

    # Companies
    try:
        companies = pd.read_csv(companies_path)
    except Exception:
        companies = pd.DataFrame(columns=["Ticker", "Company", "Sector", "MarketCap"])

    # Prices
    try:
        prices = pd.read_csv(prices_path)
        if "Date" in prices.columns:
            prices["Date"] = pd.to_datetime(prices["Date"], errors="coerce")
    except Exception:
        prices = pd.DataFrame(columns=["Ticker", "Date", "Close"])

    # Splits
    try:
        splits = pd.read_csv(splits_path)
        if "Split Date" in splits.columns:
            splits["Split Date"] = pd.to_datetime(splits["Split Date"], errors="coerce")
    except Exception:
        splits = pd.DataFrame(columns=["Ticker", "Company", "Split Date", "Ratio"])

    return prices, companies, splits

# -----------------------------
# Market overview
# -----------------------------
def market_overview(companies):
    total_stocks = companies["Ticker"].nunique() if not companies.empty else 0
    total_sectors = companies["Sector"].nunique() if not companies.empty else 0
    companies["MarketCap"] = pd.to_numeric(companies.get("MarketCap", 0), errors="coerce").fillna(0)
    total_marketcap = int(companies["MarketCap"].sum()) if not companies.empty else 0

    html = f"""
    <div class="overview">
        <div class="card"><h3>Stocks Tracked</h3><p>{total_stocks}</p></div>
        <div class="card"><h3>Sectors</h3><p>{total_sectors}</p></div>
        <div class="card"><h3>Total Market Cap</h3><p>{total_marketcap:,} ZAR</p></div>
    </div>
    """
    return html

# -----------------------------
# Top 10 companies overall
# -----------------------------
def top_companies(prices, companies):
    df = companies.copy()
    df["MarketCap"] = pd.to_numeric(df.get("MarketCap", 0), errors="coerce").fillna(0)

    # Merge latest prices
    if not prices.empty and {"Ticker", "Date", "Close"}.issubset(prices.columns):
        latest_prices = prices.sort_values("Date").groupby("Ticker").last().reset_index()[["Ticker", "Close"]]
        df = df.merge(latest_prices, on="Ticker", how="left")
    else:
        df["Close"] = None

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
        html += f"""
        <tr>
            <td>{row.get('Ticker','')}</td>
            <td>{row.get('Company','')}</td>
            <td>{row.get('Sector','')}</td>
            <td>{safe_float_format(row.get('Close'))}</td>
            <td>{safe_float_format(row.get('MarketCap'))}</td>
        </tr>
        """
    html += "</table>"
    return html

# -----------------------------
# Top 10 per sector
# -----------------------------
def sector_leaders(prices, companies):

    df = companies.copy()
    df["MarketCap"] = pd.to_numeric(df.get("MarketCap", 0), errors="coerce").fillna(0)

    # Merge latest prices
    if not prices.empty and {"Ticker","Date","Close"}.issubset(prices.columns):
        latest_prices = (
            prices.sort_values("Date")
            .groupby("Ticker")
            .last()
            .reset_index()[["Ticker","Close"]]
        )

        df = df.merge(latest_prices, on="Ticker", how="left")
    else:
        df["Close"] = None

    html = "<h2>Top 10 Companies per Sector</h2>"

    sectors = sorted(df["Sector"].dropna().unique()) if not df.empty else []

    for sector in sectors:

        sector_df = df[df["Sector"] == sector]
        top_sector = sector_df.sort_values("MarketCap", ascending=False).head(10)

        html += f"<h3>{sector}</h3>"

        html += """
        <table>
        <tr>
        <th>Ticker</th>
        <th>Company</th>
        <th>Close</th>
        <th>Market Cap</th>
        </tr>
        """

        for _, row in top_sector.iterrows():

            html += f"""
            <tr>
            <td>{row.get('Ticker','')}</td>
            <td>{row.get('Company','')}</td>
            <td>{safe_float_format(row.get('Close'))}</td>
            <td>{safe_float_format(row.get('MarketCap'))}</td>
            </tr>
            """

        html += "</table>"

    return html
# -----------------------------
# Stock splits
# -----------------------------
def stock_splits(splits):
    html = "<h2>Historical Stock Splits</h2>"
    if splits.empty:
        html += "<p>No stock split data available.</p>"
        return html

    html += "<table><tr><th>Ticker</th><th>Company</th><th>Split Date</th><th>Ratio</th></tr>"
    for _, row in splits.iterrows():
        split_date = row.get("Split Date")
        date_str = split_date.strftime("%Y-%m-%d") if pd.notna(split_date) else "-"
        html += f"<tr><td>{row.get('Ticker','')}</td><td>{row.get('Company','')}</td><td>{date_str}</td><td>{row.get('Ratio','')}</td></tr>"
    html += "</table>"
    return html

# -----------------------------
# Home route
# -----------------------------
@app.route("/")
def home():
    try:
        prices, companies, splits = load_data()
        overview_html = market_overview(companies)
        top_html = top_companies(prices, companies)
        sector_html = sector_leaders(companies)
        splits_html = stock_splits(splits)
    except Exception as e:
        return f"<h1>Application Error</h1><p>{e}</p>"

    html = f"""
<!DOCTYPE html>
<html>
<head><title>JSE Market Research Dashboard</title>
<style>
body {{font-family: Arial; background:#f4f6f8; margin:40px; color:#333;}}
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
<div class="subtitle">Historical equity dataset built from Yahoo Finance for Johannesburg Stock Exchange companies</div>
{overview_html}
{top_html}
{sector_html}
{splits_html}
<div class="footer">Data Source: Yahoo Finance<br>Research Project: JSE Sector & Market Capitalisation Analysis</div>
</div>
</body>
</html>
"""
    return html

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)