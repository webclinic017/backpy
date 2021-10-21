
from .BaseStrategy import BaseStrategy

class OneLongShort(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [1,2,3,4,5,6,7],
            "max_positions" : 1,
            "fast_periods": [6,8,10],
            "slow_periods_mult": [2,3,4],
            "roc": args["roc"] if args.get("roc") else 100,
            "sma": 150,
            "symbol": "BTC"
        }

    def add_indicators(self, data, args):
        data[f"sma"] = data["close"].rolling(self.params["sma"]).mean()
        for i, (fast, multi) in enumerate(zip(self.params["fast_periods"], self.params["slow_periods_mult"])):
            data[f"sma_fast_{i}"] = data["close"].rolling(self.params["fast_periods"][i]).mean()
            data[f"sma_slow_{i}"] = data["close"].rolling(self.params["fast_periods"][i] * self.params["slow_periods_mult"][i]).mean()
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        crosses = 0
        symbols = []
        for i in range(len(self.params["fast_periods"])):
            cross_up = data[f"sma_fast_{i}"][self.params["symbol"]].loc[date] > data[f"sma_slow_{i}"][self.params["symbol"]].loc[date]
            if cross_up:
                crosses += 1
        if crosses == 3:
            symbols = ["BTC"]
        
        if crosses == 0:
            symbols = ["BTCs"]

        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        return daily_positions