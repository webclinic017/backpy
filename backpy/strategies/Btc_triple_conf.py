from .BaseStrategy import BaseStrategy

class Btc_triple_conf(BaseStrategy):
    def __init__(self, args):
        self.params = {
            "days": [0,1,2,3,4,5,6,7],
            "max_positions" : 10,
            "bbands": args["bbands"] if args.get("bbands") else 150,
        }

    def add_indicators(self, data):
        data["30_ago"] = data["close"].shift(30)
        data["60_ago"] = data["close"].shift(60)
        data["90_ago"] = data["close"].shift(15)
        return data

    def get_buy_signals(self, data, date, daily_positions, current_constituents, i):
        # s30 = data["close"]["BTC"].loc[date] > data["30_ago"]["BTC"].loc[date]
        # s60 = data["close"]["BTC"].loc[date] > data["60_ago"]["BTC"].loc[date] 
        # s90 = data["close"]["BTC"].loc[date] > data["90_ago"]["BTC"].loc[date] 

        symbols = []
        if i%2==0:
            symbols = ["ETH"]
        if i%2==1:
            symbols = ["BTC"]
        
        
        # if s30 and s60 and s90:
        # symbols += ["BTC"]
        return symbols

    def get_sell_signals(self, data, date, daily_positions, current_constituents, i):
        s30 = data["close"]["BTC"].loc[date] < data["30_ago"]["BTC"].loc[date]
        s60 = data["close"]["BTC"].loc[date] < data["60_ago"]["BTC"].loc[date] 
        s90 = data["close"]["BTC"].loc[date] < data["90_ago"]["BTC"].loc[date] 

        symbols = ["BTC"]
        # if s30 or s60 or s90:
        #     symbols += ["BTC"]

        symbols = ["BTC", "ETH"]
        return symbols