import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random

from .BaseStrategy import BaseStrategy

class Btc_mac(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [3],
            "max_positions" : 1,
            "fast_period": args["fast_period"] if args.get("fast_period") else 6,
            "slow_period_mult": args["slow_period_mult"] if args.get("slow_period_mult") else 3,
        }

    def add_indicators(self, data, args):
        data["sma_fast"] = data["close"].rolling(self.params["fast_period"]).mean()
        data["sma_slow"] = data["close"].rolling(self.params["fast_period"] * self.params["slow_period_mult"]).mean()
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        cross_up = data["sma_fast"]["BTC"].loc[date] > data["sma_slow"]["BTC"].loc[date] 

        symbols = []
        if cross_up:
            symbols = ["BTC"]
        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        cross_down = data["sma_fast"]["BTC"].loc[date] < data["sma_slow"]["BTC"].loc[date]

        symbols = []
        if cross_down:
            symbols = ["BTC"]
        return symbols