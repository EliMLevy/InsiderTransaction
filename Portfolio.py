class Portfolio():
    def __init__(self, initial_cash):
        self.initial_cash = initial_cash
        self.cash_bal = initial_cash
        # map tickers to holding objs
        self.holdings = {}

    def sell_asset(self, ticker, date):
        holding = self.holdings[ticker]
        value = holding.val(date)

        self.cash_bal += value
        del self.holdings[ticker]

    
    def portfolio_value(self, date):
        asset_bal = 0
        for holding in self.holdings.values():
            asset_bal += holding.val(date)

        return self.cash_bal + asset_bal


    def buy_asset(self, holding, date):
        self.cash_bal -= holding.val(date)
        self.holdings[holding.ticker] = holding

    def print_holdings(self, date):
        output = "["
        for holding in self.holdings.values():
            output += f"[{holding.ticker} quantity:{holding.quantity}; profit:{round(holding.profit_percent(date), 2)}]"
        
        output += "]"
        return output

    def get_dollar_pl(self, date):
        val = self.portfolio_value(date)
        return val - self.initial_cash
    
    def get_percent_pl(self, date):
        val = self.portfolio_value(date)
        return val / self.initial_cash

    def get_pl(self, date):
        return f"${self.get_dollar_pl(date)}, %{self.get_percent_pl(date)}"