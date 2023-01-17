# https://query1.finance.yahoo.com/v8/finance/chart/HCCI?region=US&lang=en-US&includePrePost=false&interval=1mo&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance
# https://query1.finance.yahoo.com/v7/finance/download/HCCI?period1=1661990400&period2=1672358400&interval=1d&events=history&includeAdjustedClose=true
# 
import datetime

import requests
import json
import sys
import time
from os import path, listdir
from os.path import isfile, join
from collections import defaultdict
import math
import random
import pandas as pd

class Yahoo_Price_Lookup():
    def __init__(self, cache_dir):
        self.API_SLEEP_TIME = 3
        self.lookup_table = defaultdict(pd.DataFrame)
        self.last_request_time = None
        self.cache_dir = cache_dir
        for f in listdir(cache_dir):
            if isfile(join(cache_dir, f)):
                parsed_filename = f.split('.')[0]
                data = pd.read_csv(f"{cache_dir}/{f}", index_col=0)
                self.lookup_table[parsed_filename] = data

        self.blacklist = set()
        self.blacklist.add("NLSN")
        self.blacklist.add("NLOK")
        self.blacklist.add("Y")
        self.blacklist.add("Z AND ZG")

        

    def lookup(self, ticker, date):
        if date.weekday() >= 5:
            return None
        if ticker in self.lookup_table and self.lookup_table[ticker] is None:
            return None
        if ticker in self.blacklist:
            return None
        
        if ticker in self.lookup_table:
            result = self.lookup_table[ticker][self.lookup_table[ticker]["date"] == str(date)]
        else:
            result = []

        if ticker not in self.lookup_table or len(result) == 0:
            # print(f"Cache miss on {ticker} {str(date)}\n{self.lookup_table[ticker]}")
            new_data = self.get_thirty_days_prices(ticker, date, date + datetime.timedelta(days=30))
            self.lookup_table[ticker] = pd.concat([self.lookup_table[ticker], new_data]).reset_index(drop=True)
            self.lookup_table[ticker].to_csv(f"{self.cache_dir}/{ticker}.csv")
            result = self.lookup_table[ticker][self.lookup_table[ticker]["date"] == str(date)]
            if len(result) == 0:
                # print(f"Twas not in lookup table. {self.lookup_table.values()}")
                self.lookup_table[ticker].loc[len(self.lookup_table[ticker])] = [str(date), 0, 0, "0"]
                return None


        result = result.iloc[0]
        if result["timestamp"] == "0":
            return None

        price = (result["open"] + result["close"]) / 2
        return price

    def get_thirty_days_prices(self, ticker, start_date, end_date):
        if ticker in self.blacklist:
            return None

        url = f"https://query1.finance.yahoo.com/v7/finance/chart/{ticker}?period1={int(start_date.timestamp())}&period2={int(end_date.timestamp())}&interval=1d&events=history"
        # Send the request and get the response
        if self.last_request_time is not None and time.time() - self.last_request_time < 5:
            time.sleep(self.API_SLEEP_TIME)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        self.last_request_time = time.time()
        # Convert the response to a JSON object
        data = json.loads(response.text)

        try:
            price_data = data["chart"]["result"][0]["indicators"]["quote"][0]
            timestamps = data["chart"]["result"][0]["timestamp"]
        except Exception:
            print(f"Failed to extract data from resonse: {response.text}")
            return None

        result = pd.DataFrame(columns=["date", "open", "close", "timestamp"])
        for i in range(len(price_data["open"])):
            date = datetime.datetime.fromtimestamp(timestamps[i])
            price_open = price_data["open"][i],
            price_close = price_data["close"][i],
            timestamp = str(date.timestamp())
            result.loc[len(result)] = [str(datetime.datetime(date.year, date.month, date.day)), price_open, price_close, timestamp]

        # print(f"Price result: {result}")
        return result

    def load_tickers(self, tickers, start_date, end_date):
        for ticker in tickers:
            print(f"fetching ticker {ticker}")
            new_data = self.get_thirty_days_prices(ticker, start_date, end_date)
            self.lookup_table[ticker] = pd.concat([self.lookup_table[ticker], new_data]).reset_index(drop=True)
            self.lookup_table[ticker].to_csv(f"{self.cache_dir}/{ticker}.csv")


class Fake_Price_Lookup(Yahoo_Price_Lookup):

    def __init__(self, cache_dir):
        super().__init__(cache_dir)

    def get_thirty_days_prices(self, ticker, start_date, end_date):
        result = pd.DataFrame(columns=["date", "open", "close", "timestamp"])

        curr_day = start_date
        while curr_day < end_date:
            open_price = random.random() * 500 + 100
            result.loc[len(result)] = [str(curr_day), open_price, open_price + random.random() * 10 - 5, str(curr_day.timestamp())]
            curr_day += datetime.timedelta(days=1)
        return result


def main():
    price_lookup = Fake_Price_Lookup("cached_ticker_data")
    date = datetime.datetime(2023, 1, 18)
    print(f"GOOG: {price_lookup.lookup('GOOG', date)}")
    print(f"AAPL: {price_lookup.lookup('AAPL', date)}")
    print(f"OJAD: {price_lookup.lookup('OJAD', date)}")
    print(f"ADAW: {price_lookup.lookup('ADAW', date)}")

    print(f"GOOG: {price_lookup.lookup('GOOG', datetime.datetime(2022, 1, 18))}")


if __name__ == "__main__":
    main()


