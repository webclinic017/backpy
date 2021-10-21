from .BaseStrategy import BaseStrategy
import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
import multiprocessing
from joblib import dump, load
import os

CEREBRO_PATH = os.environ["CEREBRO_PATH"]


class RandomForestLongShort(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [0, 1, 2, 3, 4, 5, 6, 7],
            "max_positions": 10,
            "train_set_length": 90,
            "prediction_range": 15,
            "predicted_symbol": args["predicted_symbol"] if args.get("predicted_symbol") else "ETH"
        }
        self.models = {}
        self.last_updated = None
        self.args = args
        self.labels = {}
        self.features = {}

    def add_indicators(self, data, args):
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        predictions = self.make_predictions(date, data, current_constituents)
        return predictions

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        return daily_positions

    def update_models(self, data, date, constituents):
        configs = [[data, date, symbol] for symbol in constituents]

        date_str = date.strftime("%Y-%m-%d")
        models_path = f"{CEREBRO_PATH}src/satoshi/strategies/models/RandomForest/{self.params['prediction_range']}/{date_str}/"

        if os.path.isdir(models_path) and not self.args["train"]:
            files = os.listdir(models_path)
            for file in files:
                clf = load(models_path + file)
                self.models[clf.symbol] = clf

        else:
            clfs = []
            if self.args["parallel"] == True:
                with multiprocessing.Pool() as p:
                    clfs = p.map(self.train_model, configs)
            else:
                for config in configs:
                    clf = self.train_model(config)
                    clfs.append(clf)

            os.makedirs(models_path, exist_ok=True)
            for clf in clfs:
                self.models[clf.symbol] = clf
                dump(clf, models_path + f"{clf.symbol}.pkl")

    def train_model(self, config):
        data, date, symbol = config[0], config[1], config[2]

        btc_frame, y_btc = self.load_frame(
            data, self.params["predicted_symbol"])
        symbol_frame, y_symbol = self.load_frame(data, symbol)
        btc_frame, y_btc, symbol_frame, y_symbol = self.filter_dates(
            date, btc_frame, y_btc, symbol_frame, y_symbol)
        x, y = self.combine_frames(btc_frame, y_btc, symbol_frame, y_symbol)

        clf = RandomForestClassifier(random_state=0)
        clf.symbol = symbol
        clf.fit(x, y)

        return clf

    def combine_frames(self, btc_frame, y_btc, symbol_frame, y_symbol):
        frame = pd.DataFrame(index=btc_frame.index)
        for btc_col, symbol_col in zip(btc_frame.columns, symbol_frame.columns):
            frame[btc_col] = symbol_frame[symbol_col] < btc_frame[btc_col]
        frame = frame.fillna(0)
        y = y_symbol > y_btc

        return frame, y

    def filter_dates(self, date, btc_frame, y_btc, symbol_frame, y_symbol):
        dates = list(filter(lambda d: d < date, list(btc_frame.index)))
        n = self.params["train_set_length"]
        btc_frame2 = btc_frame.loc[dates].tail(n)
        y_btc2 = y_btc.loc[dates].tail(n)
        symbol_frame2 = symbol_frame.loc[dates].tail(n)
        y_symbol2 = y_symbol.loc[dates].tail(n)

        no_dates = len(dates) == 0
        if len(btc_frame) != len(symbol_frame) or no_dates:
            raise Exception("Error filter_dates: Invalid dates")

        return btc_frame2, y_btc2, symbol_frame2, y_symbol2

    def load_frame(self, data, symbol):
        df = None
        y = None
        if symbol in self.features.keys():
            df = self.features[symbol]
            y = self.labels[symbol]
        else:
            periods = [3, 5, 7, 10, 15, 20, 30, 50, 100, 150, 200]
            df = pd.DataFrame(index=data["close"].index)
            df['y'] = data["close"][symbol].shift(
                self.params["prediction_range"]*-1) / data["close"][symbol] - 1
            for length in periods:
                df[f"mfi{length}"] = ta.mfi(
                    data["high"][symbol], 
                    data["low"][symbol], 
                    data["close"][symbol], 
                    data["volume"][symbol], 
                    length=length)
                df[f"roc{length}"] = ta.roc(
                    data["close"][symbol], length=length)
                df[f"rsi{length}"] = ta.rsi(
                    data["close"][symbol], length=length)
            y = df["y"]
            del df["y"]
            self.features[symbol] = df.copy(deep=True)
            self.labels[symbol] = y

        return df, y

    def make_predictions(self, date, data, current_constituents):
        if (not self.models or date.weekday() == 3) and self.last_updated != date:
            self.last_updated = date
            self.update_models(data, date, current_constituents)

        long_predictions = []
        short_predictions = []
        for symbol in current_constituents:
            btc_frame, y_btc = self.load_frame(
                data, self.params["predicted_symbol"])
            symbol_frame, y_symbol = self.load_frame(data, symbol)

            btc_frame, y_btc, symbol_frame, y_symbol = btc_frame.loc[date].fillna(
                0), y_btc.loc[date], symbol_frame.loc[date].fillna(0), y_symbol.loc[date]

            x = symbol_frame < btc_frame
            try:
                res = self.models[symbol].predict_proba([x])[0]
                short_prob, long_prob = res[0], res[1]
                if short_prob > long_prob:
                    short_predictions.append([symbol, short_prob])
                else:
                    long_predictions.append([symbol, long_prob])
            except:
                pass
        short_predictions = sorted(
            short_predictions, key=lambda x: x[1], reverse=True)
        short_predictions = [
            f"{prediction[0]}s" for prediction in short_predictions]

        long_predictions = sorted(
            long_predictions, key=lambda x: x[1], reverse=True)
        long_predictions = [prediction[0] for prediction in long_predictions]

        split = int(self.params["max_positions"]/2)
        short_predictions = short_predictions[:split]
        long_predictions = long_predictions[:split]

        symbols = short_predictions + long_predictions
        return symbols
