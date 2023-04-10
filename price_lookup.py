# https://query1.finance.yahoo.com/v8/finance/chart/HCCI?region=US&lang=en-US&includePrePost=false&interval=1mo&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance
# https://query1.finance.yahoo.com/v7/finance/download/HCCI?period1=1661990400&period2=1672358400&interval=1d&events=history&includeAdjustedClose=true
# 
import datetime

import requests
import json
import sys
import time
from os import path, listdir, mkdir
from os.path import isfile, join
from collections import defaultdict
import math
import random
import pandas as pd
import logging_utils

from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.common.exceptions import APIError

from alpaca.data.timeframe import TimeFrame


import sys

import os
from dotenv import load_dotenv
load_dotenv()








class Yahoo_Price_Lookup():
    def __init__(self, cache_dir, prev_caches):
        self.API_SLEEP_TIME = 1
        self.lookup_table = defaultdict(pd.DataFrame)
        self.last_request_time = None
        self.cache_dir = cache_dir
        if not path.exists(cache_dir):
            mkdir(cache_dir)
        else:
            for prev_cache_dir in prev_caches:
                if path.exists(prev_cache_dir):
                    for f in listdir(prev_cache_dir):
                        if isfile(join(prev_cache_dir, f)):
                            parsed_filename = f.split('.')[0]
                            print("loading ticker " + parsed_filename + " from " + str(prev_cache_dir))
                            data = pd.read_csv(f"{prev_cache_dir}/{f}", index_col=0)
                            self.lookup_table[parsed_filename] = pd.concat([self.lookup_table[parsed_filename], data]).reset_index(drop=True)



        self.blacklist = set()
        # old_blacklist = ["AMB", "ESV", "SOYL", "SUG", "WMG", "NLOK", "ATMI", "NSOL", "STR", "TRA", "Y", "MWE", "NLSN", "NITE", "UTX", "TSO", "BEAV", "LZ", "DELL", "Z AND ZG", "PGN", "CNB", "TEC"]
        # old_blacklist = ["AGII", "SUG", "ESV", "MWE", "BHI", "VCSY", "ARB", "FLOW", "SVNT", "(MRK)", "MWA, MWA.B", "BCR", "SCBT", "ASI", "ASEI", "LLEN", "QRE", "FPO", "URS", "VAL", "DELL", "COMV", "Z AND ZG", "ATPG", "CHTL", "ARP", "ICON", "IMN", "DNEX", "FCEA/FCEB", "HCF", "UPL", "NWMO", "GLG", "NSOL", "MDCA", "DWA", "WMG", "ROIA/ROIAK", "TRA", "INDM", "ISLE", "ORH", "NLSN", "TEC", "HEK", "COG", "NITE", "UBI", "TSO", "RGA", "APC", "EUGS", "LLTC", "IDSA", "AMSG", "WSCE", "VRTU", "METH", "NU", "CAST", "EK", "ONNN", "NONE", "SEPR", "XJT", "GEF,GEF.B", "PNY", "POLGA.OC", "MRH", "PGN", "EPCC", "LZ", "SOYL", "ETEV.OB", "AMB", "LGF", "LBTY", "SLE", "CNB", "WMI", "SIAL", "NCS", "RKT", "SFY", "POLGA.OB", "DSTI", "CBB", "cvit", "NLOK", "UTX", "STI", "MNRK", "HET", "MHP", "CYCL", "DLM", "GPOR", "Y", "POM", "CEPH", "BNE", "RA", "WIN", "IBKC", "BEAV", "NIHD", "ATMI", "HR", "STR", "CRN", "PL", "TXCO"]
        old_blacklist = ["MBTF", "BRSS", "GLXZ", "ABQQ", "TWOH", "UEEC", "BDCO", "Z AND ZG", "WDLF", "VCSY", "MOBQ", "PTVCA/B", "FMCB", "REAC"]
        for ticker in old_blacklist:
            self.blacklist.add(ticker)



        self.logger = logging_utils.get_logger(__name__, f"pricelookups.log")
        

        

    def lookup(self, ticker, date, validate=True):
        if validate:
            if date.weekday() >= 5:
                self.logger.info(f"[{str(date)}] Not a weekday")
                return None
            if ticker in self.lookup_table and self.lookup_table[ticker] is None:
                self.logger.info(f"[{str(date)}] Empty ticker")
                return None
            if ticker in self.blacklist:
                self.logger.info(f"[{str(date)}] Black listed ticker")
                return None
        

        if ticker in self.lookup_table and self.lookup_table[ticker] is not None and len(self.lookup_table[ticker]) > 0:
            result = self.lookup_table[ticker][self.lookup_table[ticker]["date"] == str(date)]
        else:
            result = []

        if ticker not in self.lookup_table or len(result) == 0:
            self.logger.info(f"[{str(date)}] Cache miss on {ticker} {str(date)}. {ticker not in self.lookup_table} {len(result)}")
            new_data = self.get_range_of_days_prices(ticker, date, date + datetime.timedelta(days=365))
            if new_data is None:
                self.blacklist.add(ticker)
                self.logger.info(f"[{str(date)}] Blacklisting {ticker}. Blacklist: {json.dumps(list(self.blacklist))}")
                return None
                
            self.lookup_table[ticker] = pd.concat([self.lookup_table[ticker], new_data]).reset_index(drop=True)
            print(f"{self.cache_dir}/{ticker}.csv")
            self.lookup_table[ticker].to_csv(f"{self.cache_dir}/{ticker}.csv")
            result = self.lookup_table[ticker][self.lookup_table[ticker]["date"] == str(date)]
            if len(result) == 0:
                self.lookup_table[ticker].loc[len(self.lookup_table[ticker])] = [str(date), 0, 0, 0]
                return None


        result = result.iloc[0]
        if result["timestamp"] == 0:
            return None

        price = result["close"]
        # price = (result["open"] + result["close"]) / 2

        if price == 0 or math.isnan(price):
            self.logger.error(f"Returning None for ticker {ticker} on date {str(date)}. Timestamp is {result['timestamp']}")
            return None

        return price

    def get_range_of_days_prices(self, ticker, start_date, end_date):
        if ticker in self.blacklist:
            return None

#               https://query1.finance.yahoo.com/v8/finance/chart/GGC?   includeAdjustedClose=false&period1=1201046400&                   period2=1235347200&                 interval=1d
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?includeAdjustedClose=false&period1={int(start_date.timestamp())}&period2={int(end_date.timestamp())}&interval=1d&events=history"
        # print(url)
        # Send the request and get the response
        if self.last_request_time is not None and time.time() - self.last_request_time < 5:
            time.sleep(self.API_SLEEP_TIME)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        self.last_request_time = time.time()
        # Convert the response to a JSON object
        try:
            data = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            self.logger.warn(f"Failed to parse JSON data for ticker {ticker} at url {url} from resonse: {response.text} ")
            return None
        
        try:
            price_data = data["chart"]["result"][0]["indicators"]["quote"][0]
            timestamps = data["chart"]["result"][0]["timestamp"]
        except Exception:
            self.logger.warn(f"Failed to extract data for ticker {ticker} at url {url} from resonse: {response.text} ")
            return None

        # print(price_data)
        result = pd.DataFrame(columns=["date", "open", "close", "timestamp"])
        for i in range(len(price_data["open"])):
            date = datetime.datetime.fromtimestamp(timestamps[i])
            price_open = price_data["open"][i]
            price_close = price_data["close"][i]
            timestamp = str(date.timestamp())
            result.loc[len(result)] = [str(datetime.datetime(date.year, date.month, date.day)), price_open, price_close, timestamp]

        return result

    def load_tickers(self, tickers, start_date, end_date):
        for ticker in tickers:
            self.logger.info(f"fetching ticker {ticker}")
            new_data = self.get_range_of_days_prices(ticker, start_date, end_date)
            self.lookup_table[ticker] = pd.concat([self.lookup_table[ticker], new_data]).reset_index(drop=True)
            self.lookup_table[ticker].to_csv(f"{self.cache_dir}/{ticker}.csv")


class Fake_Price_Lookup(Yahoo_Price_Lookup):

    def __init__(self, cache_dir):
        super().__init__(cache_dir)

    def get_range_of_days_prices(self, ticker, start_date, end_date):
        result = pd.DataFrame(columns=["date", "open", "close", "timestamp"])

        curr_day = start_date
        while curr_day < end_date:
            open_price = random.random() * 500 + 100
            result.loc[len(result)] = [str(curr_day), open_price, open_price + random.random() * 10 - 5, str(curr_day.timestamp())]
            curr_day += datetime.timedelta(days=1)
        return result



class Alpaca_Price_Lookup(Yahoo_Price_Lookup):

    def __init__(self, cache_dir, prev_caches):
        super().__init__(cache_dir, prev_caches)
        APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
        APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
        self.client = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)


    def get_range_of_days_prices(self, ticker, start_date, end_date):
        # print("making alpaca req")

        if self.last_request_time is not None and time.time() - self.last_request_time < 5:
            time.sleep(self.API_SLEEP_TIME)
        self.last_request_time = time.time()
        req = StockBarsRequest(symbol_or_symbols=[ticker], timeframe=TimeFrame.Day, start=start_date, end=end_date)
        try:
            res = self.client.get_stock_bars(req)
        except APIError:
            self.logger.warn(f"Got error for ticker {ticker}")
            self.blacklist.add(ticker)
            self.logger.info(f"blacklist: {json.dumps(list(self.blacklist))}")
            return None

            
        if len(res.data) == 0:
            self.logger.warn(f"Got empty response for ticker {ticker} from URL from resonse: {res.data} ")
            return None

        result = pd.DataFrame(columns=["date", "open", "close", "timestamp"])
        if ticker.upper() in res.data:
            for day in res.data[ticker.upper()]:
                rounded_date = datetime.datetime(day.timestamp.year, day.timestamp.month, day.timestamp.day)
                result.loc[len(result)] = [str(rounded_date), day.open, day.close, rounded_date.timestamp()]
        else:
            raise Exception("Strange API response: " + str(res))
        return result



def main():

    year = "2010"
    if len(sys.argv) == 2:
        year = sys.argv[1]

    price_lookup = Yahoo_Price_Lookup("cached_ticker_data/" + year, [])
    # date = datetime.datetime(2022, 6, 21)
    # print(f"GOOG: {price_lookup.lookup('GOOG', date)}")
    # print(f"AAPL: {price_lookup.lookup('AAPL', date)}")
    # print(f"OJAD: {price_lookup.lookup('OJAD', date)}")
    # print(f"ADAW: {price_lookup.lookup('ADAW', date)}")

    print(f"SPY: {price_lookup.lookup('SPY', datetime.datetime(int(year), 1, 1), validate=False)}")


if __name__ == "__main__":
    main()


