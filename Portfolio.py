from collections import deque

import logging_utils



class Portfolio():
    def __init__(self, initial_cash):
        self.initial_cash = initial_cash
        self.cash_bal = initial_cash
        # map tickers to Holding objs
        self.holdings = {}
        self.portfolio_logger = logging_utils.get_logger(__name__, f"portfolio.log")
        self.portfolio_logger.info("Initialized!")

    def sell_asset(self, ticker, date, purchase_date):
        holding = self.holdings[ticker][str(purchase_date)]
        value = holding.val(date)

        self.cash_bal += value
        del self.holdings[ticker][str(purchase_date)]

    
    def portfolio_value(self, date):
        asset_bal = self.asset_bal(date)
        if asset_bal is None:
            self.portfolio_logger.info(f"On {str(date)} asset bal was None")
        return self.cash_bal + asset_bal

    def asset_bal(self, date):
        asset_bal = 0
        for holdings_dict in self.holdings.values():
            for holding in holdings_dict.values():
                if holding.val(date) is not None:
                    asset_bal += holding.val(date)
                else:
                    self.portfolio_logger.info(f"On {str(date)} val of {holding.ticker} was None")
                    asset_bal += (holding.purchase_price * holding.quantity)
        if asset_bal is None:
            self.portfolio_logger.info(f"On {str(date)} return value of asset bal was None")

        return asset_bal

    def buy_asset(self, holding, date):
        self.cash_bal -= holding.val(date)
        if holding.ticker not in self.holdings:
            self.holdings[holding.ticker] = {}
        self.holdings[holding.ticker][str(date)] = holding

    def print_holdings(self, date):
        output = "["
        for holdings_dict in self.holdings.values():
            for holding in holdings_dict.values():
                output += f"[{holding.ticker} quantity:{holding.quantity}; profit:{round(holding.profit_percent(date), 2)}; value: {round(holding.val(date))}]"

        output += "]"
        return output

    def get_dollar_pl(self, date):
        val = self.portfolio_value(date)
        if val is None:
            self.portfolio_logger.info(f"On {str(date)} val was None")
        return val - self.initial_cash
    
    def get_percent_pl(self, date):
        val = self.portfolio_value(date)
        return val / self.initial_cash

    def get_pl(self, date):
        return f"${self.get_dollar_pl(date)}, %{self.get_percent_pl(date)}"