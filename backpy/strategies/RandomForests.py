import pandas_ta as ta
import pandas as pd
import os

from .BaseStrategy import BaseStrategy

CEREBRO_PATH = os.environ["CEREBRO_PATH"]

class RandomForests(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [1, 2, 3, 4, 5, 6, 7],
            "max_positions": 100,
            "roc": 10,
            "strategies" : [
                f"RandomForest_BTC",
                f"RandomForest_ETH",
                f"RandomForest_USDC"
            ]
        }

    def add_indicators(self, data, args):
        data["roc"] = data["close"].apply(lambda x: ta.roc(x, length=self.params["roc"]), axis=0)

        load_path = f"{CEREBRO_PATH}results/values/weights/"
        for strategy in self.params["strategies"]:
            data[f"{strategy}"] = pd.read_csv(load_path+strategy+".csv", index_col="date", parse_dates=["date"])
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        selected_symbols_by_strat = {}
        for strategy in self.params["strategies"]:
            symbols = data[strategy].loc[date].to_dict()
            symbols = {k:v for k, v in symbols.items() if v > 0}
            selected_symbols_by_strat[strategy] = symbols

        selected_symbols = []
        for symbol in current_constituents:
            include_symbol = True

            for strat, symbols in selected_symbols_by_strat.items():
                if symbol not in symbols:
                    include_symbol = False

            if include_symbol:
                selected_symbols.append(symbol)

        return selected_symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = current_constituents
        return symbols

