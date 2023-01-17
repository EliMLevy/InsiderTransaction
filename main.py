import pandas as pd
from datetime import (datetime, timedelta)
from Holding import Holding
import json

from collections import defaultdict

from filter_EDGAR_data import filtered_transactions
from find_insider_trades import find_insider_trades
from simulator import run_simulator
from price_lookup import (Fake_Price_Lookup, Yahoo_Price_Lookup)


quarters = ["./data/2022Q1/", "./data/2022Q2/", "./data/2022Q3/", "./data/2022Q4/"]

# Load all insider trades into one DF
all_insider_trades = pd.DataFrame()
for quarter in quarters:
    transactions = filtered_transactions(quarter)

    print(f"{quarter} {len(transactions)}")
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)

    insider_trades, tickers = find_insider_trades(start_date, end_date, transactions, threshold=1_000_000)
    insider_trades.to_csv(quarter + "filtered.csv")

    all_insider_trades = pd.concat([all_insider_trades, insider_trades]).reset_index(drop=True)

all_insider_trades.to_csv("./data/all_trades.csv")


# print(tickers)
price_lookup = Yahoo_Price_Lookup('cached_ticker_data')
# price_lookup.load_tickers(tickers, start_date, end_date)
# price_lookup.load_tickers(["SPY"], start_date, end_date)

finished_portfolio = run_simulator(start_date, end_date, all_insider_trades, price_lookup)


        


