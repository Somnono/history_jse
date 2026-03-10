import yfinance as yf

def calculate_market_cap(ticker_symbol, year):
    
    ticker = yf.Ticker(ticker_symbol)

    hist = ticker.history(
        start=f"{year}-01-01",
        end=f"{year}-12-31"
    )

    if hist.empty:
        return None

    close_price = hist["Close"].iloc[-1]

    try:
        shares = ticker.info.get("sharesOutstanding", None)
    except:
        shares = None

    if not shares:
        return None

    return close_price * shares