from .sectors import SECTORS
from .marketcap import calculate_market_cap

def rank_sectors(year):

    sector_results = {}

    for sector, tickers in SECTORS.items():

        companies = []

        for ticker in tickers:

            cap = calculate_market_cap(ticker, year)

            if cap:
                companies.append({
                    "ticker": ticker,
                    "market_cap": cap
                })

        companies.sort(key=lambda x: x["market_cap"], reverse=True)

        sector_results[sector] = companies[:10]

    return sector_results