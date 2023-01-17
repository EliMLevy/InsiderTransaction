import logging
from Portfolio import Portfolio
from datetime import (datetime, timedelta)
from Holding import Holding
import sys
import pandas as pd
import math


# Simulate the strategy:
# current_day = sept 1
# fragment_size = 0.2
# loss_stop = %5
# profit_target = 1%
# expiration = 14 days
# till the last day:
#   check any holdings to see if they are ready to be sold.
#       if the holding has lost more l=than loss_stop
#       if the holding has made more than profit_target
#       if the holding has been held for more than expiration
#   get all filings from today
#   find all filings that are worthy of buying
#   get the amount of money to spend today (total_val * fragment_size)
#       if we dont have that much money then use all that we have
#       if we have no money then skip today
#   split that amount by the number of worthy stocks
def run_simulator(start_date, end_date, insider_trades, price_lookup, fragment_size=0.1, loss_stop=0.95, profit_target=1.01, expiration=90, starting_cash=5000):
    logging.basicConfig(filename='2022Q3simulation.log',filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info("Initialize variables. Starting simulation...")
    
    current_day = start_date
    portfolio = Portfolio(starting_cash)
    holidays_df = pd.read_csv("./holidays.csv")
    portfolio_profit_df = pd.DataFrame(columns=["date", "$p/l", "%p/l", "SPY $p/l", "SPY %p/l"])
    spy_holding = None
    
    if price_lookup.lookup("SPY", current_day) is not None:
        spy_holding = Holding("SPY", 1, price_lookup.lookup("SPY", current_day), current_day, price_lookup)
    
    while current_day < end_date:
        # Check if its a trading day
        if current_day.weekday() >= 5:
            logging.info(f"[{str(current_day)}] Skipping weekend")
            current_day += timedelta(days=1)
            continue
        holiday = holidays_df[(holidays_df["Month"] == current_day.month) & (holidays_df["Day"] == current_day.day)]
        # holiday = holidays_df[holidays_df["Day"] == current_day.day]
        if len(holiday) > 0:
            logging.info(f"[{str(current_day)}] Skipping holiday")
            current_day += timedelta(days=1)

            continue
        
        # Ensure that we initialize the SPY holding on the first trading day
        if spy_holding is None and price_lookup.lookup("SPY", current_day) is not None:
            spy_holding = Holding("SPY", 1, price_lookup.lookup("SPY", current_day), current_day, price_lookup)
        
        logging.info(f"[{str(current_day)}] Current P/L: {portfolio.get_pl(current_day)}")
        logging.info(f"[{str(current_day)}] Current holdings: {portfolio.print_holdings(current_day)}")

        # Find holdings to sell
        for holding in list(portfolio.holdings.values()):
            profit_percent = holding.profit_percent(current_day)
            days_held = (current_day - holding.date_bought).days
            if profit_percent < loss_stop or profit_percent > profit_target or days_held >= expiration:
                logging.info(f"[{str(current_day)}] Selling asset [{holding.ticker}] for ${holding.val(current_day)}. Profit: {profit_percent}. Days Held: {days_held}")
                portfolio.sell_asset(holding.ticker, current_day)

        # Record our current profit
        portfolio_dollar_pl = portfolio.get_dollar_pl(current_day)
        portfolio_percent_pl = round(portfolio.get_percent_pl(current_day), 2) 
        spy_dollar_pl = spy_holding.profit_dollar(current_day) 
        spy_percent_pl = round(spy_holding.profit_percent(current_day), 2)
        portfolio_profit_df.loc[len(portfolio_profit_df)] = [str(current_day),portfolio_dollar_pl, portfolio_percent_pl, spy_dollar_pl, spy_percent_pl ]

        # Get today's trades
        todays_insider_trades = insider_trades[insider_trades["date"] == str(current_day)]

        logging.info(f"[{str(current_day)}] {len(todays_insider_trades)} interesting insider trades")

        if len(todays_insider_trades) > 0:
            # for trade in todays_insider_trades.values():
            tickers = todays_insider_trades["ticker"].unique()
            for ticker in tickers:
                money_to_spend = portfolio.portfolio_value(current_day) * fragment_size
                if money_to_spend > portfolio.cash_bal:
                    money_to_spend = portfolio.cash_bal

                if money_to_spend > 0:
                    price = price_lookup.lookup(ticker, current_day)
                    if price is None:
                        logging.info(f"[{str(current_day)}] failed to get price for {ticker}")
                        continue
                    
                    # Only buy if the insider bought the security for more than market value
                    insider_buy_price = todays_insider_trades[todays_insider_trades["ticker"] == ticker]["price"].mean()
                    if price >= insider_buy_price:
                        quantity = math.floor(money_to_spend/price)
                        if quantity > 0:
                            new_holding = Holding(ticker, quantity, price, current_day, price_lookup)
                            logging.info(f"[{str(current_day)}] buying {ticker} for {new_holding.val(current_day)}")
                            portfolio.buy_asset(new_holding, current_day)

        current_day += timedelta(days=1)
    portfolio_profit_df.to_csv("PortfolioProfit.csv")
    return portfolio