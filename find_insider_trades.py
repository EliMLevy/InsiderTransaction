# Download from:
# https://www.sec.gov/dera/data/form-345

from datetime import (datetime, timedelta)
import pandas as pd


def find_insider_trades(start_date, end_date, transactions, threshold=1_000_000):
    current_day = start_date
    tickers = set()
    logs = pd.DataFrame(columns=["date", "accession_number", "ticker", "quantity", "price", "total_trans_cost", "total_shares_after_trans", "trans_code"])

    while current_day < end_date:
        # todays_filings = transactions[(transactions["month"] == current_day.month) & (transactions["day"] == current_day.day)]
        todays_filings = transactions[transactions["datetime"] == str(current_day)]
        ticker_action = {}
        for index, row in todays_filings.iterrows():
            total_cost = float(row["TRANS_SHARES"]) * float(row["TRANS_PRICEPERSHARE"])
            if total_cost >= threshold:
                tickers.add(row["ISSUERTRADINGSYMBOL"])
                try:
                    logs.loc[len(logs)] = [
                        str(current_day),
                        index,
                        row["ISSUERTRADINGSYMBOL"],
                        row["TRANS_SHARES"],
                        row["TRANS_PRICEPERSHARE"],
                        float(row["TRANS_SHARES"]) * float(row["TRANS_PRICEPERSHARE"]),
                        row["SHRS_OWND_FOLWNG_TRANS"],
                        row["TRANS_CODE"]
                    ]
                except ValueError:
                    print("FAILED TO SAVE: " + str(row))
        # print(json.dumps(ticker_action))
        # logs[current_day.timestamp()] = ticker_action
        current_day += timedelta(days=1)
    
    return logs, tickers