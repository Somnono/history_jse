from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = "data"


def load_data():

    df = pd.read_csv(os.path.join(DATA_PATH, "jse_universe.csv"))

    prices = df
    companies = df[["Ticker","Company","Sector","MarketCap"]].drop_duplicates()

    

    return prices, companies


def market_overview(prices):

    total_stocks = prices["Ticker"].nunique()
    total_sectors = prices["Sector"].nunique()
    total_marketcap = int(prices["MarketCap"].sum())

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


def top_companies(prices, companies):

    df = companies.copy()

    # Sort entire market by market cap
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
            <td>{row['Ticker']}</td>
            <td>{row['Company']}</td>
            <td>{row['Sector']}</td>
            <td>{int(row['MarketCap']):,}</td>
        </tr>
        """

    html += "</table>"

    return html


def sector_leaders(companies):

    df = companies.copy()

    html = "<h2>Top 10 Companies per Sector</h2>"

    sectors = df["Sector"].dropna().unique()

    for sector in sectors:

        sector_df = df[df["Sector"] == sector]

        top_sector = sector_df.sort_values(
            "MarketCap", ascending=False
        ).head(10)

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
            html += f"""
            <tr>
                <td>{row['Ticker']}</td>
                <td>{row['Company']}</td>
                <td>{int(row['MarketCap']):,}</td>
            </tr>
            """

        html += "</table>"

    return html


@app.route("/")
def home():

    prices, companies = load_data()

    overview_html = market_overview(prices)
    companies_html = top_companies(prices, companies)
    sector_html = sector_leaders(companies)

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