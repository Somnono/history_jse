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

    try:
        companies = pd.read_csv(companies_path)
    except:
        companies = pd.DataFrame(columns=["Ticker","Company","Sector","MarketCap"])

    try:
        prices = pd.read_csv(prices_path)
    except:
        prices = pd.DataFrame(columns=["Ticker","Date","Close"])

    try:
        splits = pd.read_csv(splits_path)
    except:
        splits = pd.DataFrame(columns=["Ticker","Company","SplitDate","SplitRatio"])

    return prices, companies, splits


# ---------------------------------
# Market overview
# ---------------------------------
def market_overview(companies):

    try:
        total_stocks = companies["Ticker"].nunique()
        total_sectors = companies["Sector"].nunique()

        companies["MarketCap"] = pd.to_numeric(
            companies["MarketCap"], errors="coerce"
        ).fillna(0)

        total_marketcap = int(companies["MarketCap"].sum())

    except:
        total_stocks = 0
        total_sectors = 0
        total_marketcap = 0

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
# Latest daily prices
# ---------------------------------
def latest_prices_table(prices):

    html = "<h2>Latest Daily Prices</h2>"

    if prices.empty:
        return html + "<p>No price data available.</p>"

    try:

        prices["Date"] = pd.to_datetime(prices["Date"], errors="coerce")

        latest = (
            prices.sort_values("Date")
            .groupby("Ticker")
            .last()
            .reset_index()[["Ticker","Date","Close"]]
        )

        latest = latest.sort_values("Close", ascending=False).head(15)

        html += """
        <table>
        <tr>
        <th>Ticker</th>
        <th>Date</th>
        <th>Close (ZAR)</th>
        </tr>
        """

        for _, row in latest.iterrows():

            html += f"""
            <tr>
            <td>{row['Ticker']}</td>
            <td>{row['Date'].date()}</td>
            <td>{row['Close']:.2f}</td>
            </tr>
            """

        html += "</table>"

    except:
        html += "<p>Price data could not be processed.</p>"

    return html


# ---------------------------------
# Stock splits table
# ---------------------------------
def stock_splits_table(splits):

    html = "<h2>Historical Stock Splits</h2>"

    if splits.empty:
        return html + "<p>No stock split data available.</p>"

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

        html += f"""
        <tr>
        <td>{row.get('Ticker','')}</td>
        <td>{row.get('Company','')}</td>
        <td>{row.get('SplitDate','')}</td>
        <td>{row.get('SplitRatio','')}</td>
        </tr>
        """

    html += "</table>"

    return html


# ---------------------------------
# Top companies
# ---------------------------------
def top_companies(companies):

    df = companies.copy()

    df["MarketCap"] = pd.to_numeric(
        df.get("MarketCap",0), errors="coerce"
    ).fillna(0)

    top_market = df.sort_values("MarketCap", ascending=False).head(10)

    html = """
    <h2>Top 10 Companies by Market Capitalisation</h2>
    <table>
    <tr>
    <th>Ticker</th>
    <th>Company</th>
    <th>Sector</th>
    <th>Market Cap (ZAR)</th>
    </tr>
    """

    for _, row in top_market.iterrows():

        html += f"""
        <tr>
        <td>{row.get('Ticker','')}</td>
        <td>{row.get('Company','')}</td>
        <td>{row.get('Sector','')}</td>
        <td>{int(row.get('MarketCap',0)):,}</td>
        </tr>
        """

    html += "</table>"

    return html


# ---------------------------------
# Home route
# ---------------------------------
@app.route("/")
def home():

    prices, companies, splits = load_data()

    overview_html = market_overview(companies)
    prices_html = latest_prices_table(prices)
    companies_html = top_companies(companies)
    splits_html = stock_splits_table(splits)

    html = f"""
<!DOCTYPE html>
<html>

<head>
<title>JSE Market Research Dashboard</title>

<style>

body {{
font-family: Arial, sans-serif;
background:#f4f6f8;
margin:40px;
color:#333;
}}

.container {{
max-width:1100px;
margin:auto;
}}

h1 {{
text-align:center;
color:#1f2d3d;
}}

.subtitle {{
text-align:center;
color:#666;
margin-bottom:40px;
}}

.overview {{
display:flex;
justify-content:space-between;
margin-bottom:40px;
}}

.card {{
background:white;
padding:20px;
flex:1;
margin:10px;
border-radius:6px;
box-shadow:0 2px 8px rgba(0,0,0,0.1);
text-align:center;
}}

table {{
width:100%;
border-collapse:collapse;
background:white;
box-shadow:0 3px 10px rgba(0,0,0,0.1);
margin-bottom:40px;
}}

th, td {{
padding:10px;
border:1px solid #ddd;
text-align:center;
}}

th {{
background:#2c3e50;
color:white;
}}

tr:nth-child(even) {{
background:#f2f2f2;
}}

.footer {{
text-align:center;
margin-top:30px;
font-size:14px;
color:#666;
}}

</style>
</head>

<body>

<div class="container">

<h1>JSE Market Research Dashboard</h1>

<div class="subtitle">
Historical equity dataset built from Yahoo Finance for Johannesburg Stock Exchange companies
</div>

{overview_html}

{prices_html}

{companies_html}

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


if __name__ == "__main__":

    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)