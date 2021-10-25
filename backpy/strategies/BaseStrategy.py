
import pandas as pd
import os
from binance.client import Client

ENVIRONMENT = os.environ["environment"]

if ENVIRONMENT == "TEST":
    from sizers._sizers_dict import sizers
else:
    from ..sizers._sizers_dict import sizers


# DATASETS_PATH = os.environ["DATASETS_PATH"]


class BaseStrategy():
    def compute_weights(self, data, args):
        all_weights = {}
        daily_positions = []
        dates = list(filter(
            lambda d: d >= args["start_date"] and d <= args["end_date"], list(data["close"].index)))
        symbols = sorted(list(data["close"].columns))
        short_symbols = [f"{symbol}s" for symbol in symbols]
        weights = [0] * len(symbols)
        all_symbols = symbols + short_symbols

        all_current_constituents = self.get_available_constituents()
        for i, date in enumerate(dates):
            # print(date)
            if date.weekday() in self.params["days"]:
                current_constituents = [
                    symbol for symbol in all_current_constituents if symbol in list(data["close"].columns)]

                if len(daily_positions) > 0:
                    sell_signals = self.get_sell_signals(
                        data, date, daily_positions, current_constituents, i)
                    daily_positions = [
                        position for position in daily_positions if position not in sell_signals]
                if len(daily_positions) < self.params["max_positions"]:
                    buy_signals = self.get_buy_signals(
                        data, date, daily_positions, current_constituents, i)
                    buy_signals = [
                        signal for signal in buy_signals if signal not in daily_positions]
                    daily_positions = daily_positions + buy_signals
                    if len(daily_positions) > self.params["max_positions"]:
                        daily_positions = daily_positions[:self.params["max_positions"]]

                weights = self.compute_day_weights(
                    all_symbols, daily_positions, date, data, args)

            all_weights[date] = weights.copy()

        all_weights = pd.DataFrame.from_dict(
            all_weights, orient="index", columns=all_symbols)
        all_weights.index.name = "date"
        return all_weights

    def get_available_constituents(self):
        client = Client()
        coin_data = client.get_exchange_info()["symbols"]
        symbols = sorted([data["baseAsset"]
                         for data in coin_data if data["quoteAsset"] == "USDT"])

        return sorted(symbols)

    def compute_day_weights(self, all_symbols, daily_positions, date, data, args):
        sized_positions = sizers[args["sizer"]](
            daily_positions, date, data, args)
        sized_positions = {k: min(v, args["max_weight"])
                           for (k, v) in sized_positions.items()}

        for symbol in all_symbols:
            if symbol not in list(sized_positions.keys()):
                sized_positions[symbol] = 0

        weights = [sized_positions[key] for key in all_symbols]
        return weights
