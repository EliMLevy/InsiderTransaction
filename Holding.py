class Holding:
    def __init__(self, ticker, quantity, purchase_price, date_bought, price_lookup):
        self.ticker = ticker
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.date_bought = date_bought
        self.price_lookup = price_lookup

    def profit_percent(self, date):
        # print(f"{self.ticker} calculating profit: {self.get_price(date)} {(self.purchase_price)}")
        if self.get_price(date) is None:
            return 1
        return self.get_price(date) / (self.purchase_price)

    def profit_dollar(self, date):
        if self.get_price(date) is None:
            return 0
        return self.get_price(date) - self.purchase_price

    def val(self, date):
        if self.get_price(date) is None:
            return 1
        return self.quantity * self.get_price(date)

    def get_price(self, date):
        return self.price_lookup.lookup(self.ticker, date)

    def __str__(self):
        return f"[{self.ticker}, quantity:{self.quantity};]"

    def __repr__(self):
        return f"[{self.ticker}, quantity:{self.quantity};]"

    