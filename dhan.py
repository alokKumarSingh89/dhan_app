from login import Login

class DhanClass:
    def __init__(self):
        self.__dhan = Login().get_dhan()
    def getStatements(self, from_date,to_date):
        return self.__dhan.get_trade_history(from_date,to_date)['data']