import pandas_ta as ta

# python satoshi.py -strategy C10_multi_mac -start_date 2021-01-01 -fee 0.001 -sizer market_cap -diversification_factor 0.7 -management_commission 0 -success_commission 0 -plot True -top 30 -max_weight 0.2

from .BaseStrategy import BaseStrategy

class C10_multi_mac(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [1,2,3,4,5,6,7],
            "max_positions" : 10,
            "fast_periods": [8,12],
            "slow_periods_mult": [2,2],
            "roc": args["roc"] if args.get("roc") else 100,
            "sma": 150
        }

    def add_indicators(self, data, args):
        data["roc"] = data["close"].apply(lambda x: ta.roc(x, length=self.params["roc"]), axis=0)
        data[f"sma"] = data["close"].rolling(self.params["sma"]).mean()
        for i, (fast, multi) in enumerate(zip(self.params["fast_periods"], self.params["slow_periods_mult"])):
            data[f"sma_fast_{i}"] = data["close"].rolling(self.params["fast_periods"][i]).mean()
            data[f"sma_slow_{i}"] = data["close"].rolling(self.params["fast_periods"][i] * self.params["slow_periods_mult"][i]).mean()
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = []
        for symbol in current_constituents:
            crosses = 0
            for i in range(len(self.params["fast_periods"])):
                cross_up = data[f"sma_fast_{i}"][symbol].loc[date] > data[f"sma_slow_{i}"][symbol].loc[date]
                if cross_up:
                    crosses += 1
            if crosses >= 2:
                symbols.append(symbol)

        symbols = list(sorted(symbols, key=lambda symbol: data["roc"][symbol].loc[date], reverse=True))
        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = []
        for symbol in current_constituents:
            crosses = 0
            for i in range(len(self.params["fast_periods"])):
                cross_up = data[f"sma_fast_{i}"][symbol].loc[date] > data[f"sma_slow_{i}"][symbol].loc[date]
                if cross_up:
                    crosses += 1

            if crosses <= 3:
                symbols.append(symbol)

        s = list(sorted(daily_positions, key=lambda symbol: data["roc"][symbol].loc[date],reverse=True))
        symbols = symbols + s[:2]
        symbols = list(set(symbols))
        return symbols