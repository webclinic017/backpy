import pandas_ta as ta

from .BaseStrategy import BaseStrategy

class Momentum(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [1,2,3,4,5,6,7],
            "max_positions" : 20,
            "roc": 21,
            "sma": 100
        }

    def add_indicators(self, data, args):
        data["roc"] = data["close"].apply(lambda x: ta.roc(x, length=self.params["roc"]), axis=0)
        data["sma"] = data["close"].apply(lambda x: ta.ema(x, length=self.params["sma"]), axis=0)

        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        if data["close"]["BTC"].loc[date] < data["sma"]["BTC"].loc[date]:
            return []
        
        symbols = list(filter(lambda symbol: data["close"][symbol].loc[date] > data["sma"][symbol].loc[date], current_constituents))
        symbols = list(sorted(symbols, key=lambda symbol: data["roc"][symbol].loc[date],reverse=True))
        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = []
        a = list(sorted(daily_positions, key=lambda symbol: data["roc"][symbol].loc[date],reverse=True))[-5:]
        b = list(filter(lambda symbol: data["sma"][symbol].loc[date] < data["close"][symbol].loc[date], daily_positions))
        symbols = symbols + a + b
        return symbols