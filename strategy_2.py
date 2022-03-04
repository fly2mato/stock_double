import math

import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
from strategy.rsi6_s0 import Rsi6_t0
from trade.trade import Trade

start_date = '2021-07-01'
# end_date = '2022-02-28'
end_date = None

code = '600036'
stock_history = pd.read_csv('./data/stock_history_d.csv', header=0, dtype={'code': str})\
        .query(f"code == '{code}'")

policy = Rsi6_t0()
trade = Trade(stock_history, start_date=start_date, end_date=end_date, init_cash=1e5)
trade.backtesting(policy)