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

class Yahoo_Price_Lookup():
    def __init__(self, cache_dir):
        self.lookup_table = defaultdict(dict)
        self.last_request_time = None
        self.cached_files = {}
        for f in listdir(cache_dir):
            if isfile(join(cache_dir, f)):
                parsed_filename = f.split('-')
                parsed_start = parsed_filename[1][5:].split("_")
                parsed_end = parsed_filename[2][3:-5].split("_")
                self.cached_files[parsed_filename[0]] = {
                    "start": datetime.datetime(int(parsed_start[0]),int(parsed_start[1]),int(parsed_start[2])),
                    "end": datetime.datetime(int(parsed_end[0]),int(parsed_end[1]),int(parsed_end[2]))
                }
        print(self.cached_files)

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
        if ticker in self.lookup_table and date in self.lookup_table[ticker] and self.lookup_table[ticker][date] == None:
            return None
        if ticker in self.blacklist:
            return None
        
        if ticker not in self.lookup_table or str(date) not in self.lookup_table[ticker]:
            if ticker in self.cached_files and date >= self.cached_files[ticker]["start"] and date <= self.cached_files[ticker]["end"]:
                cached_file_start = self.cached_files[ticker]["start"]
                cached_file_end = self.cached_files[ticker]["end"]
                with open(f"cached_ticker_data/{ticker}-START{cached_file_start.year}_{cached_file_start.month}_{cached_file_start.day}-END{cached_file_end.year}_{cached_file_end.month}_{cached_file_end.day}.json", "r") as input_file:
                    data = json.loads(input_file.read())
                    self.lookup_table[ticker] = {**self.lookup_table[ticker], **data}
            else:
                # print(f"Cache miss on {ticker} {str(date)}\n{self.lookup_table[ticker]}")
                new_data = self.get_thirty_days_prices(ticker, date, date + datetime.timedelta(days=30))
                self.lookup_table[ticker] = {**self.lookup_table[ticker], **new_data}

        if str(date) not in self.lookup_table[ticker]:
            # print(f"Twas not in lookup table. {self.lookup_table.values()}")
            return None

        data = self.lookup_table[ticker][str(date)]
        price = (data["open"] + data["close"]) / 2

        return price

    def get_thirty_days_prices(self, ticker, start_date, end_date):
        if ticker in self.blacklist:
            return None
        if ticker in self.cached_files and start_date >= self.cached_files[ticker]["start"] and end_date <= self.cached_files[ticker]["end"]:
            cached_file_start = self.cached_files[ticker]["start"]
            cached_file_end = self.cached_files[ticker]["end"]
            with open(f"cached_ticker_data/{ticker}-START{cached_file_start.year}_{cached_file_start.month}_{cached_file_start.day}-END{cached_file_end.year}_{cached_file_end.month}_{cached_file_end.day}.json", "r") as input_file:
                data = json.loads(input_file.read())
            return data


        url = f"https://query1.finance.yahoo.com/v7/finance/chart/{ticker}?period1={int(start_date.timestamp())}&period2={int(end_date.timestamp())}&interval=1d&events=history"
        # Send the request and get the response
        if self.last_request_time is not None and time.time() - self.last_request_time < 5:
            time.sleep(5)
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

        result = {}
        for i in range(len(price_data["open"])):
            date = datetime.datetime.fromtimestamp(timestamps[i])
            result[str(datetime.datetime(date.year, date.month, date.day))] = {
                "open": price_data["open"][i],
                "close": price_data["close"][i],
                "timestamp": date.timestamp()
            }
        
        with open(f"cached_ticker_data/{ticker}-START{start_date.year}_{start_date.month}_{start_date.day}-END{end_date.year}_{end_date.month}_{end_date.day}.json", "w") as output_file:
            output_file.write(json.dumps(result))

        # print(f"Price result: {result}")
        return result

    def load_tickers(self, tickers, start_date, end_date):
        for ticker in tickers:
            print(f"fetching ticker {ticker}")
            self.lookup_table[ticker] = self.get_thirty_days_prices(ticker, start_date, end_date=end_date)


class Fake_Price_Lookup():
    def lookup(self, ticker, date):
        return 10