import os
import pandas as pd
import numpy as np
import baostock as bs
from tqdm import tqdm
import multiprocessing
from datetime import datetime
import time

stock_pool_path = './data/stock_pool.csv'
stock_history_path = './data'


def get_stock_pool(date=''):
    bs.login()
    hs300 = bs.query_hs300_stocks(date).get_data()
    zz500 = bs.query_zz500_stocks(date).get_data()
    stock_pool = pd.concat([hs300, zz500]).reset_index(drop=True).drop(columns=['updateDate'])
    bs.logout()
    return stock_pool


def load_code_kdata(idx, code_list, fields, start_date, end_date, freq, adjust):
    bs.login()
    history_list = []
    for code in tqdm(code_list):
        rs = bs.query_history_k_data_plus(code, fields, start_date, end_date, freq, adjust)
        history_list.append(rs.get_data())
    history_data = pd.concat(history_list)
    history_data.to_csv(stock_history_path + f'/tmp/{idx}.csv', index=False)
    bs.logout()


def load_history_k_data(freq='d', adjust='2', start_date='2011-01-01'):
    if os.path.exists(stock_pool_path):
        stock_pool = pd.read_csv(stock_pool_path, header=0)
    else:
        stock_pool = get_stock_pool()
        stock_pool.to_csv(stock_pool_path, index=False)

    if freq=='d':
        fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"
    else:
        fields = 'date,time,code,open,high,low,close,volume,amount,adjustflag'

    end_date = datetime.strftime(datetime.fromtimestamp(int(time.time())), '%Y-%m-%d')

    s_stime = int(time.time())
    n = 20
    jobs = []
    for idx in range(n):
        code_list = stock_pool.code.values[idx * 40:(idx + 1) * 40]
        process = multiprocessing.Process(target=load_code_kdata, args=(idx, code_list, fields, start_date, end_date, freq, adjust))
        jobs.append(process)
        process.start()

    for p in jobs:
        p.join()

    print(f'time cost = {int(time.time() - s_stime)} sec')
    stock_history_list = []
    for idx in range(n):
        stock_history_list.append(pd.read_csv(stock_history_path + f'/tmp/{idx}.csv', header=0))
        os.remove(stock_history_path + f'/tmp/{idx}.csv')
    stock_history = pd.concat(stock_history_list)
    stock_history.to_csv(stock_history_path + f'/stock_history_{freq}.csv', index=False)


def load_trade_dates(start_date=''):
    bs.login()
    df = bs.query_trade_dates(start_date).get_data()
    bs.logout()
    return df


def load_stock_industry():
    bs.login()
    df = bs.query_stock_industry().get_data()
    bs.logout()
    return df