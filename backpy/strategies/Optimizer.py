import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random

from strategies.BaseStrategy import BaseStrategy


class Optimizer(BaseStrategy):
    def __init__(self, args):
        strategies = [
            f"TAMomentum_LIVE",
            f"RandomForest_LIVE",
            f"Multi_mac_LIVE"]
        self.params = {
            "days": [1, 2, 3, 4, 5, 6, 7],
            "max_positions": 10,
            "strategies": args["strategies"] if args.get("strategies") else strategies
        }

    def add_indicators(self, data, args):
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        return self.params["strategies"]

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = []
        return symbols
