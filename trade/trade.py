import pandas as pd
from strategy.base_strategy import Strategy
from strategy.order_element import Position, Order
import math


class Trade:
    def __init__(self, stock_history: pd.DataFrame, start_date, end_date=None, init_cash=1e5):
        self.start_date = start_date
        self.stock_history = stock_history
        if end_date is None:
            self.end_date = stock_history.loc[:, 'date'].max()
        else:
            self.end_date = end_date
        self.cash=init_cash

    def check_out(self, row: pd.Series, order: Order, position: Position):
        if order.p > 0:
            trade_cnt = int(math.floor(position.cash * order.p // (order.price * 100)))
            trade_value = order.price * 100 * trade_cnt
            position.cash -= trade_value
            position.stock += trade_cnt
            position.cost += 3.2e-4 * trade_value
        elif order.p < 0:
            trade_cnt = int(math.floor( - position.stock * order.p))
            trade_value = order.price * 100 * trade_cnt
            position.cash += trade_value
            position.stock -= trade_cnt
            position.cost += 1.32e-3 * trade_value
        else:
            pass
        position.value = position.cash + position.stock * 100 * row.close - position.cost

    def can_trade(self, price, row, order: Order) -> bool:
        if row.tradestatus == 0 or price > row.high or price < row.low:
            return False
        elif row.code[0] != 3 and row.pctChg >= 9.99 and order.cnt > 0:
            return False
        elif row.code[0] != 3 and row.pctChg <= -9.99 and order.cnt < 0:
            return False
        elif row.code[0] == 3 and row.pctChg >= 19.99 and order.cnt > 0:
            return False
        elif row.code[0] == 3 and row.pctChg <= -19.99 and order.cnt < 0:
            return False
        else:
            return True

    def backtesting(self, strategy: Strategy):
        tmp_stock_history = strategy.calc_signal(self.stock_history)
        trade_stock_history = tmp_stock_history.query(f"'{self.start_date}' <= date <= '{self.end_date}'")
        position = Position(self.cash, 0, 0)
        for step, row in trade_stock_history.iterrows():
            if row.date == self.end_date:
                self.check_out(row, Order(row.close, -1), position)
            else:
                order = strategy.decision(position, row)
                if self.can_trade(order.price, row, order):
                    self.check_out(row, order, position)
            print(f"date={row.date}, cash={position.cash:.2f}, stock={position.stock:2d}, cost={position.cost:.2f}, value={position.value:.2f}")







