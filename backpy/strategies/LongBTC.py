from .BaseStrategy import BaseStrategy

class LongBTC(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [0,1,2,3,4,5,6,7],
            "max_positions": 1
        }

    def add_indicators(self, data, args):
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        return ["BTC"]

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        return []

        