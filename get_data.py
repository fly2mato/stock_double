import os
import pandas as pd



from utils.load_data import *



if __name__ == '__main__':
    load_history_k_data()
    load_history_k_data(freq='5', adjust='3', start_date='2021-01-01')

    # df = load_trade_dates('2011-01-01')
    # df.to_csv('./data/trade_dates.csv', index=False)
    #
    # df = load_stock_industry()
    # df.to_csv('./data/stock_industry.csv', index=False)

    bs.login()
    df = bs.query_all_stock().get_data()
    df.to_csv('./data/all_stock.csv', index=False)
    bs.logout()

    print(1)

