import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random

from strategies.BaseStrategy import BaseStrategy

class MarketLeaders(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [3],
            "max_positions": 3
        }

    def add_indicators(self, data, args):
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        return ["BTC", "ETH", "XRP"]

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        return []

        