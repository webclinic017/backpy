from binance.client import Client
import requests
from datetime import datetime, timedelta

from .BaseStrategy import BaseStrategy
import pandas_ta as ta


def get_broker_symbols(broker: str):
    symbols = None
    if broker == "Binance":
        client = Client()
        info = client.get_exchange_info()
        symbols = [symbol['baseAsset']
                   for symbol in info['symbols'] if symbol['quoteAsset'] == 'USDT']
    elif broker == "Bitso":
        r = requests.get('https://api.bitso.com/v3/available_books')
        payload = r.json()["payload"]
        pairs = [symbol["book"]
                 for symbol in payload if "_btc" in symbol["book"]]
        symbols = [pair.split("_")[0].upper() for pair in pairs]
        symbols.insert(0, "BTC")
    else:
        raise Exception("Invalid broker flag must be Binance or Bitso")

    return [s for s in symbols if "USD" not in s]


class Penrose(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [0,1,2,3,4,5,6],
            "max_positions": args["max_positions"],
            "symbols": get_broker_symbols(args["broker"]),
            "roc": 15,
        }

    def add_indicators(self, data, args):
        data["roc"] = data["close"].apply(
            lambda x: ta.roc(x, length=self.params["roc"]), axis=0)
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        current_constituents = list(sorted(
            current_constituents, key=lambda symbol: data["cap"][symbol].loc[date], reverse=True))[:50]
        symbols = list(sorted(
            current_constituents, key=lambda symbol: data["roc"][symbol].loc[date], reverse=True))
        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = list(sorted(
            daily_positions, key=lambda symbol: data["roc"][symbol].loc[date], reverse=True))[-2:]
        return symbols
