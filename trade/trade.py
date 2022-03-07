import pandas as pd
import numpy as np
from strategy.base_strategy import Strategy
from strategy.order_element import Position, Order
import math
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib import ticker



class Record:
    def __init__(self, start_date, base_index='sh.000300'):
        self.value = []
        self.p = []
        self.can_trade = []
        self.price = []
        self.date = []
        self.base_index = base_index

        base_index = pd.read_csv('./data/index_history_d.csv', header=0).query(
            f"code == '{base_index}' and date >= '{start_date}'")
        self.base_index_close = base_index.close.values
        self.base_index_close /= self.base_index_close[0]

    def add(self, date, order: Order, position: Position, can_trade):
        self.date.append(date)
        self.p.append(order.p)
        self.price.append(order.price)
        self.can_trade.append(can_trade)
        self.value.append(position.value)

    def calc(self):
        self.value = np.array(self.value)
        self.p = np.array(self.p)
        self.can_trade = np.array(self.can_trade)
        self.buy_point = (self.p > 0) & (self.can_trade > 0)
        self.sell_point = (self.p < 0) & (self.can_trade > 0)
        self.profit = self.value/self.value[0]

class Trade:
    def __init__(self, stock_history: pd.DataFrame, start_date, end_date=None, init_cash=1e5):
        self.start_date = start_date
        self.stock_history = stock_history
        if end_date is None:
            self.end_date = stock_history.loc[:, 'date'].max()
        else:
            self.end_date = end_date
        self.cash=init_cash
        self.record=Record(start_date=start_date)

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

    def can_trade(self, price, row, order: Order):
        if row.tradestatus == 0 or price > row.high or price < row.low:
            return 0
        elif row.code[0] != '3' and row.pctChg >= 9.99 and order.p > 0:
            return 0
        elif row.code[0] != '3' and row.pctChg <= -9.99 and order.p < 0:
            return 0
        elif row.code[0] == '3' and row.pctChg >= 19.99 and order.p > 0:
            return 0
        elif row.code[0] == '3' and row.pctChg <= -19.99 and order.p < 0:
            return 0
        else:
            return 1

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
            self.record.add(row.date, order, position, can_trade)
            print(f"date={row.date}, price={order.price:.2f}, cash={position.cash:.2f}, stock={position.stock:2d}, cost={position.cost:.2f}, value={position.value:.2f}")
        self.record.calc()
        if show:
            trade_stock_history.loc[:, 'buy'] = np.where(self.record.buy_point, trade_stock_history.low*0.99, np.nan)
            trade_stock_history.loc[:, 'sell'] = np.where(self.record.sell_point, trade_stock_history.high*1.01, np.nan)

            add_plot = [
                mpf.make_addplot(trade_stock_history[strategy.signal]),
            ]
            if any(~trade_stock_history['buy'].isna()):
                add_plot.append(mpf.make_addplot(trade_stock_history['buy'], type='scatter', markersize=50, marker='^'))
            if any(~trade_stock_history['sell'].isna()):
                add_plot.append(mpf.make_addplot(trade_stock_history['sell'], type='scatter', markersize=50, marker='v'))

            fig, ax = plt.subplots()
            ax.plot(self.record.date, self.record.profit - 1.0, label='strategy')
            ax.plot(self.record.date, self.record.base_index_close - 1.0, label=self.record.base_index)
            plt.xticks(self.record.date[::int(len(self.record.date) // 5)], rotation=30)
            ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=2))
            plt.legend()

            mpf.plot(trade_stock_history, type='candle', volume=True, addplot=add_plot)
            plt.show()











