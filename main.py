import pandas as pd
from datetime import (datetime, timedelta)
from Holding import Holding
import json

from collections import defaultdict

from filter_EDGAR_data import filtered_transactions
from find_insider_trades import find_insider_trades
from simulator import run_simulator
from price_lookup import (Fake_Price_Lookup, Yahoo_Price_Lookup)
from combine_insider_trades import combine_insider_trades

start_date = datetime(2022, 1, 1)
end_date = datetime(2022, 12, 31)
quarters = ["./data/2022Q1/", "./data/2022Q2/", "./data/2022Q3/", "./data/2022Q4/"]
all_insider_trades = combine_insider_trades(start_date, end_date, quarters, combined=True, combined_file="data/all_trades.csv")

# print(tickers)
# price_lookup = Yahoo_Price_Lookup('cached_ticker_data')
price_lookup = Fake_Price_Lookup('cached_ticker_data')
# price_lookup.load_tickers(tickers, start_date, end_date)
# price_lookup.load_tickers(["SPY"], start_date, end_date)

finished_portfolio = run_simulator(start_date, end_date, all_insider_trades, price_lookup)


        


