import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random
import math

# python satoshi.py -strategy C10_multi_mac -start_date 2021-01-01 -fee 0.001 -sizer market_cap -diversification_factor 0.7 -management_commission 0 -success_commission 0 -plot True -top 30 -max_weight 0.2

from strategies.BaseStrategy import BaseStrategy

class TAMomentum(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [1,2,3,4,5,6,7],
            "max_positions" : 20,
            "trend_period": 30,
            "roc": 100,
            "sma": 100
        }

    def add_indicators(self, data, args):
        data["roc"] = data["close"].apply(lambda x: ta.roc(x, length=self.params["roc"]), axis=0)
        data["sma"] = data["close"].apply(lambda x: ta.ema(x, length=self.params["sma"]), axis=0)

        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        if data["close"]["BTC"].loc[date] < data["sma"]["BTC"].loc[date]:
            return []
        dates = sorted(list(filter(lambda x: x < date, list(data["close"].index))))[-self.params["trend_period"]:]
        selected_symbols = []

        for symbol in current_constituents:
            past_close_data = data["close"].loc[dates[:len(dates)//2], [symbol]].values
            current_close_data = data["close"].loc[dates[len(dates)//2:], [symbol]].values
            
            if  current_close_data[-1] > max(past_close_data): #Observe price over support line
                if min(past_close_data) < min(current_close_data): #Observe Higher Lows
                    selected_symbols.append(symbol)
        
        return selected_symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = []
        return daily_positions