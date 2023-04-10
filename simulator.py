from Portfolio import Portfolio
from datetime import (datetime, timedelta)
from Holding import Holding
import sys
import pandas as pd
import math
import logging_utils
import traceback


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
def run_simulator(start_date, end_date, insider_trades, price_lookup, simlation_output_file, valid_trade_days_ticker="SPY", fragment_size=0.1, loss_stop=0.95, profit_target=1.01, jump_sell=0.05, expiration=90, starting_cash=5000):
    
    sim_logger = logging_utils.get_logger(__name__, f"{start_date.year}_{start_date.month}_{start_date.day}-{end_date.year}_{end_date.month}_{end_date.day}simulation.log")

    current_day = start_date
    last_trading_day = None
    portfolio = Portfolio(starting_cash)
    portfolio_profit_df = pd.DataFrame(columns=["date", "$p/l", "%p/l", "SPY $p/l", "SPY %p/l", "percent liquid", "cash balance"])
    spy_holding = None
    
    if price_lookup.lookup("SPY", current_day) is not None:
        spy_holding = Holding("SPY", 1, price_lookup.lookup("SPY", current_day), current_day, price_lookup)
    
    df = price_lookup.lookup_table[valid_trade_days_ticker]
    trade_days = set(df["date"])
    print(trade_days)

    stats = {
        "total_target_reaches": 0,
        "total_expiries": 0,
        "total_stop_losses": 0,
        "stop_loss_tickers": [],
        "target_reached_tickers": [],
        "jump_sells": 0,
        "jump_sell_tickers": []
    }

    # Sometimes insiders just buy their stock regularly. To try preventing these 
    # sales from ruining us we will ignore tickers that have triggered the stop loss
    ticker_weight = {}

    try:        
        while current_day < end_date:
            # Check if its a trading day
            if current_day.weekday() >= 5:
                sim_logger.info(f"[{str(current_day)}] Skipping weekend")
                current_day += timedelta(days=1)
                continue
            # holiday = holidays_df[(holidays_df["Month"] == current_day.month) & (holidays_df["Day"] == current_day.day)]
            # holiday = holidays_df[holidays_df["Day"] == current_day.day]
            # if len(holiday) > 0:
            #     sim_logger.info(f"[{str(current_day)}] Skipping holiday")
            #     current_day += timedelta(days=1)
            #     continue
            if trade_days is not None and str(current_day) not in trade_days:
                sim_logger.info(f"[{str(current_day)}] Skipping invalid trade day {str(current_day) not in trade_days} ")
                current_day += timedelta(days=1)
                continue
            # else:
            #     sim_logger.info(f"[{str(current_day)}] found in trade days {len(trade_days)}. {trade_days is not None}. {str(current_day) not in trade_days}. {price_lookup.lookup(valid_trade_days_ticker, current_day)}")

            # Ensure that we initialize the SPY holding on the first trading day
            if spy_holding is None and price_lookup.lookup("SPY", current_day) is not None:
                spy_holding = Holding("SPY", 1, price_lookup.lookup("SPY", current_day), current_day, price_lookup)
            
            sim_logger.info(f"[{str(current_day)}] Current P/L: {portfolio.get_pl(current_day)}")
            sim_logger.info(f"[{str(current_day)}] Current holdings: {portfolio.print_holdings(current_day)}")

            # Find holdings to sell
            for holding_dict in list(portfolio.holdings.values()):
                for holding in list(holding_dict.values()):
                    profit_percent = holding.profit_percent(current_day)
                    if last_trading_day is None:
                        last_trading_day_profit_percent = holding.profit_percent(current_day)
                    else:
                        last_trading_day_profit_percent = holding.profit_percent(last_trading_day)
                    days_held = (current_day - holding.date_bought).days
                    if profit_percent < loss_stop or profit_percent > profit_target or days_held >= expiration or profit_percent - last_trading_day_profit_percent > jump_sell:
                        if profit_percent < loss_stop:
                            stats["total_stop_losses"] += 1
                            if holding.ticker in ticker_weight:
                                ticker_weight[ticker] *= 0.9
                            stats["stop_loss_tickers"].append(holding.ticker)
                            sim_logger.info(f"[{str(current_day)}] STOP LOSS Selling asset [{holding.ticker}] for ${holding.val(current_day)}. Profit: {profit_percent}. Days Held: {days_held}")
                        elif profit_percent > profit_target:
                            stats["total_target_reaches"] += 1
                            stats["target_reached_tickers"].append(holding.ticker)
                            sim_logger.info(f"[{str(current_day)}] TARGET REACHED Selling asset [{holding.ticker}] for ${holding.val(current_day)}. Profit: {profit_percent}. Days Held: {days_held}")
                        elif days_held >= expiration:
                            stats["total_expiries"] += 1
                            sim_logger.info(f"[{str(current_day)}] EXPIRED Selling asset [{holding.ticker}] for ${holding.val(current_day)}. Profit: {profit_percent}. Days Held: {days_held}")
                        elif profit_percent - last_trading_day_profit_percent > jump_sell:
                            stats["jump_sells"] += 1
                            stats["jump_sell_tickers"].append(holding.ticker)
                            sim_logger.info(f"[{str(current_day)}] JUMP Selling asset [{holding.ticker}] for ${holding.val(current_day)}. Profit: {profit_percent}. Days Held: {days_held}")
                        portfolio.sell_asset(holding.ticker, current_day, holding.date_bought)

            # Record our current profit
            portfolio_dollar_pl = portfolio.get_dollar_pl(current_day)
            portfolio_percent_pl = portfolio.get_percent_pl(current_day) 
            spy_dollar_pl = spy_holding.profit_dollar(current_day) 
            spy_percent_pl = spy_holding.profit_percent(current_day)
            percent_liquid = portfolio.cash_bal / portfolio.portfolio_value(current_day)
            dollar_liquid = portfolio.cash_bal
            portfolio_profit_df.loc[len(portfolio_profit_df)] = [str(current_day),portfolio_dollar_pl, portfolio_percent_pl, spy_dollar_pl, spy_percent_pl, percent_liquid, dollar_liquid ]
            # Get today's trades
            todays_insider_trades = insider_trades[insider_trades["date"] == str(current_day)]

            sim_logger.info(f"[{str(current_day)}] {len(todays_insider_trades)} interesting insider trades")

            if len(todays_insider_trades) > 0:
                # for trade in todays_insider_trades.values():
                tickers = todays_insider_trades["ticker"].unique()
                # tickers = [n for n in todays_insider_trades["ticker"].unique() if n not in bad_tickers]

                sim_logger.info(f"[{str(current_day)}] {len(tickers)} unique tickers")

                for ticker in tickers:
                    money_to_spend = (portfolio.portfolio_value(current_day) * fragment_size) / len(tickers)
                    if ticker in ticker_weight:
                        money_to_spend *= ticker_weight[ticker]
                        
                    if money_to_spend > portfolio.cash_bal:
                        money_to_spend = portfolio.cash_bal

                    if money_to_spend > 0:
                        price = price_lookup.lookup(ticker, current_day)
                        if price is None:
                            sim_logger.info(f"[{str(current_day)}] failed to get price for {ticker}")
                            continue
                        
                        # Only buy if the insider bought the security for more than market value
                        insider_buy_price = todays_insider_trades[todays_insider_trades["ticker"] == ticker]["price"].mean()
                        if price <= insider_buy_price:
                            quantity = math.floor(money_to_spend/price)
                            if quantity > 0:
                                new_holding = Holding(ticker, quantity, price, current_day, price_lookup)
                                sim_logger.info(f"[{str(current_day)}] buying {ticker} for {price}. Total: {new_holding.val(current_day)}")
                                portfolio.buy_asset(new_holding, current_day)

            last_trading_day = current_day
            current_day += timedelta(days=1)
    except Exception as e:
        traceback.print_exc()
        portfolio_profit_df.to_csv(simlation_output_file)
        print(f"Portfolio cash: {portfolio.cash_bal}; Portfolio assets: {portfolio.asset_bal(current_day)};")
        print(portfolio.print_holdings(current_day))
        sys.exit(1)
        
    portfolio_profit_df.to_csv(simlation_output_file)
    print(stats)
    print(f"Portfolio cash: {portfolio.cash_bal}; Portfolio assets: {portfolio.asset_bal(current_day)};")
    print(portfolio.print_holdings(current_day))
    return portfolio, stats