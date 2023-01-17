import pandas as pd

def combine_insider_trades(start_date, end_date, quarters, combined=False, combined_file=""):
    if combined:
        data = pd.read_csv(combined_file, index_col=0)
        return data

    # Load all insider trades into one DF
    all_insider_trades = pd.DataFrame()
    for quarter in quarters:
        transactions = filtered_transactions(quarter)

        print(f"{quarter} {len(transactions)}")

        insider_trades, tickers = find_insider_trades(start_date, end_date, transactions, threshold=1_000_000)
        insider_trades.to_csv(quarter + "filtered.csv")

        all_insider_trades = pd.concat([all_insider_trades, insider_trades]).reset_index(drop=True)

    all_insider_trades.to_csv("./data/all_trades.csv")
