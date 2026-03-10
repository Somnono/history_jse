from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = "data"

def load_data():

    prices = pd.read_csv(os.path.join(DATA_PATH,"jse_prices.csv"))
    companies = pd.read_csv(os.path.join(DATA_PATH,"jse_companies.csv"))

    prices["Date"] = pd.to_datetime(prices["Date"])

    return prices, companies


def build_sector_table(prices, companies):

    latest = prices.sort_values("Date").groupby("Ticker").last().reset_index()

    merged = latest.merge(companies, on="Ticker", how="left")

    merged = merged.sort_values("MarketCap", ascending=False)

    top = merged.head(20)

    table = "<table>"
    table += "<tr><th>Ticker</th><th>Company</th><th>Sector</th><th>Close</th><th>Market Cap</th></tr>"

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


@app.route("/")
def home():

    prices, companies = load_data()

    table_html = build_sector_table(prices, companies)

    html = f"""
<!DOCTYPE html>
<html>

<head>

<title>JSE Market Research Dashboard</title>

<style>

body {{
font-family: Arial;
background:#f4f6f8;
margin:40px;
color:#333;
}}

h1 {{
text-align:center;
color:#1f2d3d;
}}

h2 {{
text-align:center;
color:#3b4b5a;
}}

.container {{
max-width:1100px;
margin:auto;
}}

table {{
width:100%;
border-collapse:collapse;
background:white;
box-shadow:0 3px 10px rgba(0,0,0,0.1);
}}

th,td {{
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

<h2>Top Companies by Market Capitalisation</h2>

{table_html}

<div class="footer">

Data Source: Yahoo Finance  
Research Dataset: Johannesburg Stock Exchange equities

</div>

</div>

</body>

</html>
"""

    return html


if __name__ == "__main__":
    app.run()