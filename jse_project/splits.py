import yfinance as yf

def get_splits(ticker_symbol):

    ticker = yf.Ticker(ticker_symbol)

    splits = ticker.splits

    if splits.empty:
        return []

    return splits.to_dict()