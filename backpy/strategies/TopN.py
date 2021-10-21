import pandas_ta as ta
from datetime import datetime
import pandas as pd
import random
from binance.client import Client
import requests

from strategies.BaseStrategy import BaseStrategy


def get_broker_symbols(broker: str):
    symbols = None
    if broker == "Binance":
        client = Client()
        info = client.get_exchange_info()
        symbols = [symbol['baseAsset'] for symbol in info['symbols'] if symbol['quoteAsset'] == 'USDT']
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


class TopN(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [6],
            "max_positions": args["max_positions"],
            "symbols" : get_broker_symbols(args["broker"])
        }

    def add_indicators(self, data, args):
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        symbols = sorted(self.params["symbols"])
        symbols = [s for s in symbols if s in list(data["cap"].columns)]
        symbols = list(sorted(symbols, key=lambda symbol: data["cap"][symbol].loc[date],reverse=True))
        symbols = symbols[:self.params["max_positions"]]
        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        return self.params["symbols"]
