import pandas as pd
from datetime import (datetime, timedelta)
from Holding import Holding
import json

from collections import defaultdict

from simulator import run_simulator
from price_lookup import (Fake_Price_Lookup, Yahoo_Price_Lookup, Alpaca_Price_Lookup)
from combine_insider_trades import combine_insider_trades
from graph_pl import graph_pl

import threading
import time

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


def execute_simulation(strategy):
    finished_portfolio, sim_stats = run_simulator(start_date, end_date, all_insider_trades, price_lookup, strategy["simlation_output_file"], valid_trade_days_ticker="SPY", fragment_size=strategy["fragment_size"], loss_stop=strategy["loss_stop"], profit_target=strategy["profit_target"],  expiration=strategy["expiration"], starting_cash=strategy["starting_cash"])

    with open(strategy["stats_output_file"], "w") as stats_file:
        full_stat_report = {
            "params": strategy,
            "stat": sim_stats
        }
        
        stats_file.write(json.dumps(full_stat_report))

    # input("Finished simulation. Press enter to continue")



threads = []
# Only start n-1 threads because we'll use this thread for the last one
for i in range(len(params['strategies']) - 1):
    curr_strat = params['strategies'][i]
    print(curr_strat)
    new_thread = threading.Thread(target=execute_simulation, args=(curr_strat,))
    new_thread.daemon = True
    threads.append(new_thread)
    new_thread.start()
    print("One thread started")

execute_simulation(params['strategies'][len(params['strategies']) - 1])
print("Main thread finished")


# for executing_thread in threads:
#     executing_thread.join()
while threading.active_count() > 1:
    time.sleep(0.1)

for i in range(len(params['strategies'])):
    curr_strat = params['strategies'][i]
    graph_pl(curr_strat["simlation_output_file"], curr_strat["simlation_output_graph"], curr_strat["liquidity_graph"])

        
input("Done! Press enter to exit")



