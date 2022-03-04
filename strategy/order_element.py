
class Position:
    def __init__(self, cash=0, stock=0, cost=0):
        self.cash = cash
        self.stock = stock
        self.cost = cost
        self.value = cash + stock * 0 - cost


class Order:
    def __init__(self, price, trade_percent):
        self.price = price
        self.p = trade_percent
