import pandas as pd
from datetime import (datetime, timedelta)
from Holding import Holding
import json

from collections import defaultdict

from simulator import run_simulator
from price_lookup import (Fake_Price_Lookup, Yahoo_Price_Lookup, Alpaca_Price_Lookup)
from combine_insider_trades import combine_insider_trades
from graph_pl import graph_pl

# start_date = datetime(2022, 1, 1)
# end_date = datetime(2022, 12, 31)
# quarters = ["./data/2008q2", "./data/2008q4", "./data/2008q3", "./data/2008q1"]
# quarters = ["./data/2022Q1/", "./data/2022Q2/", "./data/2022Q3/", "./data/2022Q4/"]



params = {}
with open("./params.json", "r") as param_file:
    params = json.loads(param_file.read())

print(params)

input("Press enter to continue")

start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")


all_insider_trades = combine_insider_trades(start_date, end_date, params["transaction_files"], combined=params["already_computed"], combined_file=params["filtered_transactions_output_file"], threshold=params["minimum_transaction_value"])


input("All insider trades computed. Press enter to continue")


# price_lookup = Yahoo_Price_Lookup(params["cached_ticker_data_dir"], params["prev_cached_ticker_data_dirs"])
price_lookup = Alpaca_Price_Lookup(params["cached_ticker_data_dir"], params["prev_cached_ticker_data_dirs"])
price_lookup.lookup("SPY", start_date)




finished_portfolio, sim_stats = run_simulator(start_date, end_date, all_insider_trades, price_lookup, params["simlation_output_file"], valid_trade_days_ticker="SPY", fragment_size=params["fragment_size"], loss_stop=params["loss_stop"], profit_target=params["profit_target"], jump_sell=params["jump_sell"],  expiration=params["expiration"], starting_cash=params["starting_cash"])

with open(params["stats_output_file"], "w") as stats_file:
    full_stat_report = {
        "params": params,
        "stat": sim_stats
    }
    
    stats_file.write(json.dumps(full_stat_report))

input("Finished simulation. Press enter to continue")


graph_pl(params["simlation_output_file"], params["simlation_output_graph"], params["liquidity_graph"])

        
input("Done! Press enter to exit")



