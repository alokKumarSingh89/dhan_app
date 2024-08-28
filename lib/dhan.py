from .login import Login
import pandas as pd

class DhanClass:
    def __init__(self):
        self.__dhan = Login().get_dhan()
    def getStatements(self, from_date,to_date):
        data = self.__dhan.get_trade_history(from_date,to_date)
        return data['data']
    def get(self):
        return self.__dhan;