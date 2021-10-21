import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random

from strategies.BaseStrategy import BaseStrategy

# python satoshi.py -strategy Passive -start_date 2021-01-15 -fee 0.001 -sizer market_cap -diversification_factor 0.7 -management_commission 0 -success_commission 0 -save index -plot True

class Passive(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [3],
            "max_positions" :  args["top"] if args.get("top") else 10,
        }

    def add_indicators(self, data, args):
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        return self._get_top_n_market_cap(data, date, self.params["max_positions"])

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        current_top = self._get_top_n_market_cap(data, date, self.params["max_positions"])
        symbols = [symbol for symbol in daily_positions if symbol not in current_top]
        return symbols

    def _get_top_n_market_cap(self, data, date, max_positions):
        day_caps = data["cap"].loc[date].sort_values(ascending=False)
        day_caps = day_caps[~day_caps.index.str.contains('USD')]
        day_caps = day_caps[~day_caps.index.str.contains('HEX')]
        day_caps = day_caps.iloc[:max_positions]
        symbols = list(day_caps.index)
        return symbols
        