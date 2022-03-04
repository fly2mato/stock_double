import math

import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
# all_stock = pd.read_csv('./data/all_stock.csv', hader=0)



def calc_signal(stock: pd.DataFrame):
    stock['rsi_6'] = talib.RSI(stock['close'], timeperiod=6)
    stock['30_high_max'] = np.roll(stock[['high']].rolling(30).max().values, 1)
    stock['30_low_max'] = np.roll(stock[['low']].rolling(30).min().values, 1)
    stock['30_close_mean'] = np.roll(stock[['close']].rolling(30).mean().values, 1)
    stock['p75'] = (stock['30_high_max'] + stock['30_close_mean']) / 2
    stock['p25'] = (stock['30_low_max'] + stock['30_close_mean']) / 2
    return stock


def trade_stock(row: pd.Series, state: dict):
    buy = 0
    cash = state['cash']
    stock = state['stock']
    close = row.close
    if row.rsi_6 <= 20 and close <= row.p25:
        buy = int(math.floor(cash // (close * 100)))
    elif row.rsi_6 >= 80 and close >= row.p75:
        buy = -stock
    return buy, close

def update_state(buy, price, state, close):
    if buy > 0:
        tax = 3.2e-4
    elif buy < 0:
        tax = 1.32e-3
    else:
        tax = 0
    trade_value = buy * 100 * price
    state['cost'] += tax * math.fabs(trade_value)
    state['cash'] -= trade_value
    state['stock'] += buy
    state['value'] = state['cash'] + state['stock'] * 100 * close - state['cost']
    return state


def iter_date(stock: pd.DataFrame, state: dict, info:bool =True):
    value_list = []
    init_value = state['value']
    for idx, row in stock.iterrows():
        buy, price = trade_stock(row, state)
        state = update_state(buy, price, state, row.close)
        value_list.append(state['value']/init_value)
        if info:
            print(f"date={row.date}, cash={state['cash']:.2f}, stock={state['stock']:2d}, cost={state['cost']:.2f}, value={state['value']:.2f}")
    state['value_list'] = value_list
    return state

stock_pool_history = pd.read_csv('./data/stock_history_d.csv')
stock_pool_history['code'] = stock_pool_history['code'].apply(lambda x: x[3:])
test_code_list = ['600036', '000858', '002601', '002466']
test_code_list = ['000858']
test_code_list = ['600519']

trade_date = '2021-07-01'

fig = plt.figure()

for test_code in test_code_list:
    init_state = {
        'cash': 1e6,
        'stock': 0,
        'cost': 0,
        'value': 1e6
    }
    test_stock = stock_pool_history[stock_pool_history.code == test_code]
    test_stock = calc_signal(test_stock)
    state = iter_date(test_stock[test_stock.date >= trade_date], init_state)
    print(test_code, state['value'])
    plt.plot(state['value_list'], '-o')

plt.show()
print('end')



# stock_pool_history = pd.read_csv('./data/stock_history_d.csv')
# test_code_list = pd.read_csv('./data/stock_pool.csv', header=0).values
# trade_date = '2021-07-01'
#
# ans = []
#
# for test_code, code_name in test_code_list:
#     init_state = {
#         'cash': 1e5,
#         'stock': 0,
#         'cost': 0,
#         'value': 1e5
#     }
#     test_stock = stock_pool_history[stock_pool_history.code == test_code]
#     if len(test_stock) == 0:
#         continue
#     test_stock = calc_signal(test_stock)
#     state = iter_date(test_stock[test_stock.date >= trade_date], init_state, False)
#     # print(f"code={test_code}, name={code_name}, cash={state['cash']:.2f}, stock={state['stock']:2d}, cost={state['cost']:.2f}, value={state['value']:.2f}")
#     print(f"code={test_code}, name={code_name}, value={state['value']:.2f}")
#     ans.append([test_code, state])
# print('end')





