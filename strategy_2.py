import math

import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
from strategy.rsi6_s0 import *
from trade.trade import Trade
from utils.load_data import load_history
import warnings

warnings.filterwarnings("ignore")

start_date = '2021-07-01'
# end_date = '2022-02-28'
end_date = None




code = '600036'
# # code = '002594'
code = '600863'
code = '601668'
code = '000893'
code = '600418' #byd
code = '600031' #31
# code = '600519' #maotai

# stock_history = pd.read_csv('./data/stock_history_d.csv', header=0, dtype={'code': str})\
#         .query(f"code == '{code}'")

stock_history = load_history(code, start_date=start_date)

# policy = Rsi6_t0()
policy = Rsi6_t1()
trade = Trade(stock_history, start_date=start_date, end_date=end_date, init_cash=1e6)
trade.backtesting(policy, show=True)
# trade.backtesting(policy, show=False)


print(1)






#全池测试

# pool = pd.read_csv('./data/stock_pool.csv', header=0)
# pool = pool['code'].apply(lambda x: str(x[3:]))
# for codd in pool:









