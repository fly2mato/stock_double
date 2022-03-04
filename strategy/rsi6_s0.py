import pandas as pd
import numpy as np
import talib
from strategy.base_strategy import Strategy
from trade.trade import Position, Order
import math

class Rsi6_t0(Strategy):
    def __init__(self):
        super(Rsi6_t0, self).__init__()

    def calc_signal(self, stock: pd.DataFrame) -> pd.DataFrame:
        stock['rsi_6'] = talib.RSI(stock['close'], timeperiod=6)
        stock['30_high_max'] = np.roll(stock[['high']].rolling(30).max().values, 1)
        stock['30_low_max'] = np.roll(stock[['low']].rolling(30).min().values, 1)
        stock['30_close_mean'] = np.roll(stock[['close']].rolling(30).mean().values, 1)
        stock['p75'] = (stock['30_high_max'] + stock['30_close_mean']) / 2
        stock['p25'] = (stock['30_low_max'] + stock['30_close_mean']) / 2
        return stock

    def decision(self, position: Position, row: pd.Series) -> Order:
        price = row.close
        trade_p = 0
        # if row.rsi_6 <= 20:
        if row.rsi_6 <= 20 and row.close <= row.p25:
            trade_p = 1
        # elif row.rsi_6 >= 80:
        elif row.rsi_6 >= 80 and row.close >= row.p75:
            trade_p = -1
        return Order(price, trade_p)


