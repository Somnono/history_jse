from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = "data"


def load_data():

    prices = pd.read_csv(os.path.join(DATA_PATH, "jse_prices.csv"))
    companies = pd.read_csv(os.path.join(DATA_PATH, "jse_companies.csv"))

    prices["Date"] = pd.to_datetime(prices["Date"])

    return prices, companies


def market_overview(prices):

    latest_date = prices["Date"].max()

    latest = prices[prices["Date"] == latest_date]

    avg_close = round(latest["Close"].mean(), 2)
    total_volume = int(latest["Volume"].sum())
    total_stocks = latest["Ticker"].nunique()

    html = f"""
    <div class="overview">

        <div class="card">
            <h3>Trading Date</h3>
            <p>{latest_date.date()}</p>
        </div>

        <div class="card">
            <h3>Stocks Tracked</h3>
            <p>{total_stocks}</p>
        </div>

        <div class="card">
            <h3>Average Price</h3>
            <p>{avg_close} ZAR</p>
        </div>

        <div class="card">
            <h3>Total Volume</h3>
            <p>{total_volume:,}</p>
        </div>

    </div>
    """

    return html


def top_companies(prices, companies):

    latest = prices.sort_values("Date").groupby("Ticker").last().reset_index()

    merged = latest.merge(companies, on="Ticker", how="left")

    merged = merged.sort_values("MarketCap", ascending=False)

    top = merged.head(10)

    table = """
    <h2>Top Companies by Market Capitalisation</h2>
    <table>
    <tr>
    <th>Ticker</th>
    <th>Company</th>
    <th>Sector</th>
    <th>Close</th>
    <th>Market Cap (ZAR)</th>
    </tr>
    """

    for _, row in top.iterrows():

        mc = f"{int(row['MarketCap']):,}" if pd.notnull(row["MarketCap"]) else ""

        table += f"""
        <tr>
        <td>{row['Ticker']}</td>
        <td>{row['Company']}</td>
        <td>{row['Sector']}</td>
        <td>{round(row['Close'],2)}</td>
        <td>{mc}</td>
        </tr>
        """

    table += "</table>"

    return table


def sector_leaders(prices, companies):

    latest = prices.sort_values("Date").groupby("Ticker").last().reset_index()

    merged = latest.merge(companies, on="Ticker", how="left")

    sector_top = merged.sort_values("Close", ascending=False).groupby("Sector").head(1)

    table = """
    <h2>Top Stock per Sector</h2>
    <table>
    <tr>
    <th>Sector</th>
    <th>Ticker</th>
    <th>Company</th>
    <th>Price</th>
    </tr>
    """

    for _, row in sector_top.iterrows():

        table += f"""
        <tr>
        <td>{row['Sector']}</td>
        <td>{row['Ticker']}</td>
        <td>{row['Company']}</td>
        <td>{round(row['Close'],2)}</td>
        </tr>
        """

    table += "</table>"

    return table


@app.route("/")
def home():

    prices, companies = load_data()

    overview_html = market_overview(prices)
    companies_html = top_companies(prices, companies)
    sector_html = sector_leaders(prices, companies)

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
margin-bottom:10px;
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

{companies_html}

{sector_html}

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

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)