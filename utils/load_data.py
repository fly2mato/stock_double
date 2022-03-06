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

    pool_len = len(stock_pool)
    print(pool_len)
    if freq=='d':
        fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"
    else:
        fields = 'date,time,code,open,high,low,close,volume,amount,adjustflag'

    end_date = datetime.strftime(datetime.fromtimestamp(int(time.time())), '%Y-%m-%d')

    s_stime = int(time.time())
    n = 1
    process_len = int(pool_len // n)
    jobs = []
    for idx in range(n):
        code_list = stock_pool.code.values[idx * process_len:(idx + 1) * process_len]
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
    stock_history.loc[:, 'code'] = stock_history.loc[:, 'code'].apply(lambda x: str(x[3:]))
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


def load_index_history(start_date='', end_date='', freq='d'):
    bs.login()

    index_code = ['sh.000001',
                 'sh.000300', #hs300
                 'sh.000905', #zz500
                 'sz.399303', #国2000
                 'sz.399673', #创50
                 ]

    data_list = []
    for code in index_code:
        df = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,pctChg",
                                      start_date=start_date, end_date=end_date, frequency=freq).get_data()
        data_list.append(df)

    index_history = pd.concat(data_list)
    # index_history.loc[:, 'code'] = index_history.loc[:, 'code'].apply(lambda x: str(x[3:]))
    index_history.to_csv(f'./data/index_history_{freq}.csv', index=False)
    bs.logout()


def load_history(code, start_date='2018-01-01'):
    stock_history = pd.read_csv('./data/stock_history_d.csv', header=0, dtype={'code': str}) \
        .query(f"code == '{code}'")

    if len(stock_history) == 0:
        bs.login()
        fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"
        if code[0] == '6':
            prex = 'sh.'
        else:
            prex = 'sz.'
        stock_history = bs.query_history_k_data_plus(prex+code, fields, start_date=start_date, frequency='d', adjustflag='2').get_data()\
        .query("tradestatus != '0' and tradestatus != 0")\
        .astype({
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'close': 'float64',
            'preclose': 'float64',
            'volume': 'float64',
            'amount': 'float64',
            'adjustflag': 'int64',
            'turn': 'float64',
            'tradestatus': 'int64',
            'pctChg': 'float64',
            'peTTM': 'float64',
            'pbMRQ':'float64',
            'psTTM':'float64',
            'pcfNcfTTM':'float64',
            'isST': 'int64'
        })
        stock_history['code'] = code
        bs.logout()
    return stock_history
