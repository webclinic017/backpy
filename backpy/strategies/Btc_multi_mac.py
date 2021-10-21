import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random

from strategies.BaseStrategy import BaseStrategy

class Btc_multi_mac(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [3],
            "max_positions" : 1,
            "fast_periods": [2,4,6],
            "slow_periods_mult": [3,4,5],
        }

    def add_indicators(self, data, args):
        for i, (fast, multi) in enumerate(zip(self.params["fast_periods"], self.params["slow_periods_mult"])):
            data[f"sma_fast_{i}"] = data["close"].rolling(self.params["fast_periods"][i]).mean()
            data[f"sma_slow_{i}"] = data["close"].rolling(self.params["fast_periods"][i] * self.params["slow_periods_mult"][i]).mean()
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        crosses = 0
        for i in range(len(self.params["fast_periods"])):
            cross_up = data[f"sma_fast_{i}"]["BTC"].loc[date] > data[f"sma_slow_{i}"]["BTC"].loc[date]
            if cross_up:
                crosses += 1

        symbols = []
        if crosses >= 2:
            symbols = ["BTC"]
        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        crosses = 0
        for i in range(len(self.params["fast_periods"])):
            cross_up = data[f"sma_fast_{i}"]["BTC"].loc[date] > data[f"sma_slow_{i}"]["BTC"].loc[date]
            if cross_up:
                crosses += 1

        symbols = []
        if crosses <= 1:
            symbols = ["BTC"]
        return symbols