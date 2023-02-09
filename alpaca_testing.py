from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockSnapshotRequest
from alpaca.data.timeframe import TimeFrame
import datetime

import pandas as pd

from alpaca.data.requests import StockBarsRequest

from alpaca.trading.client import TradingClient

# paper=True enables paper trading

APCA_API_KEY_ID = 'AKPYYWRH22CBIP972ME7'
APCA_API_SECRET_KEY = '2wM6nlA56bckhHyc1JkkRUkfrbbZiSNlNCxsy0SB'

trading_client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=False)



account = trading_client.get_account()
# Account test

print(account.status)


from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient

# no keys required.
crypto_client = CryptoHistoricalDataClient()

# keys required
client = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=["SPY", "GLD", "TLT"])

latest_multisymbol_quotes = client.get_stock_latest_quote(multisymbol_request_params)


barreq = StockBarsRequest(symbol_or_symbols=["ADADWA"], timeframe=TimeFrame.Day, start=datetime.datetime(2022, 1, 1), end=datetime.datetime(2022, 2, 1))
barres = client.get_stock_bars(barreq)

print(barres.data)
print(len(barres.data))

result = pd.DataFrame(columns=["date", "open", "close", "timestamp"])
for day in barres.data['NTUS']:
    print(day)
    result.loc[len(result)] = [day.timestamp, day.open, day.close, day.timestamp.timestamp()]


print(result)


# snapshopReq = StockSnapshotRequest(symbol_or_symbols=["TCF"])
# snapshotRes = client.get_stock_snapshot(snapshopReq)

# print(snapshopReq)


# client = StockHistoricalDataClient(api_key='AKGZ21ZIKLZJGT70QEZL', secret_key='ZzsOotruQam4AKp8JRocZ8Qf8gTBXTnyw49iQ6cA')

# # req = StockBarsRequest(symbol_or_symbols=["AAPL"])

# # data = client.get_stock_bars(req)

# # print(data)

# multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=["SPY", "GLD", "TLT"])

# latest_multisymbol_quotes = client.get_stock_latest_quote(multisymbol_request_params)

# print(latest_multisymbol_quotes)
# # No keys required for crypto data
# # client = CryptoHistoricalDataClient()


# # from alpaca.data.requests import CryptoBarsRequest
# # from alpaca.data.timeframe import TimeFrame

# # # Creating request object
# # request_params = CryptoBarsRequest(
# #                         symbol_or_symbols=["BTC/USD"],
# #                         timeframe=TimeFrame.Day,
# #                         start="2022-09-01",
# #                         end="2022-09-07"
# #                         )


# # # Retrieve daily bars for Bitcoin in a DataFrame and printing it
# # btc_bars = client.get_crypto_bars(request_params)

# # # Convert to dataframe
# # btc_bars.df