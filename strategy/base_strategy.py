import pandas as pd
from strategy.order_element import Order

class Strategy:
    def __init__(self):
        pass

    def calc_signal(self, stock: pd.DataFrame) -> pd.DataFrame:
        return stock

    def decision(self) -> Order:
        pass