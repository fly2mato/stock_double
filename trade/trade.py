import pandas as pd
import numpy as np
from strategy.base_strategy import Strategy
from strategy.order_element import Position, Order
import math
import mplfinance as mpf
import matplotlib.pyplot as plt

class Trade:
    def __init__(self, stock_history: pd.DataFrame, start_date, end_date=None, init_cash=1e5):
        self.start_date = start_date
        self.stock_history = stock_history
        if end_date is None:
            self.end_date = stock_history.loc[:, 'date'].max()
        else:
            self.end_date = end_date
        self.cash=init_cash
        self.record=[]

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
        elif row.code[0] != '3' and row.pctChg >= 9.99 and order.p > 0:
            return False
        elif row.code[0] != '3' and row.pctChg <= -9.99 and order.p < 0:
            return False
        elif row.code[0] == '3' and row.pctChg >= 19.99 and order.p > 0:
            return False
        elif row.code[0] == '3' and row.pctChg <= -19.99 and order.p < 0:
            return False
        else:
            return True

    def backtesting(self, strategy: Strategy, show=False):
        tmp_stock_history = strategy.calc_signal(self.stock_history)
        trade_stock_history = tmp_stock_history.query(f"'{self.start_date}' <= date <= '{self.end_date}'")
        trade_stock_history.index = pd.to_datetime(trade_stock_history.date)
        position = Position(self.cash, 0, 0)
        for step, row in trade_stock_history.iterrows():
            order = strategy.decision(position, row)
            can_trade = self.can_trade(order.price, row, order)
            if can_trade:
                self.check_out(row, order, position)
            self.record.append([order.p, order.price, can_trade*1])
            print(f"date={row.date}, price={order.price:.2f}, cash={position.cash:.2f}, stock={position.stock:2d}, cost={position.cost:.2f}, value={position.value:.2f}")

        if show:
            record = pd.DataFrame(self.record, columns=['p', 'price', 'can_trade'])
            trade_stock_history['buy'] = np.where((record.p > 0) & (record.can_trade > 0), trade_stock_history.low*0.99, np.nan)
            trade_stock_history['sell'] = np.where((record.p < 0) & (record.can_trade > 0), trade_stock_history.high*1.01, np.nan)

            add_plot = [
                mpf.make_addplot(trade_stock_history[strategy.signal]),
            ]
            if any(~trade_stock_history['buy'].isna()):
                add_plot.append(mpf.make_addplot(trade_stock_history['buy'], type='scatter', markersize=50, marker='^'))
            if any(~trade_stock_history['sell'].isna()):
                add_plot.append(mpf.make_addplot(trade_stock_history['sell'], type='scatter', markersize=50, marker='v'))

            mpf.plot(trade_stock_history, type='candle', volume=True, addplot=add_plot)
            plt.show()











