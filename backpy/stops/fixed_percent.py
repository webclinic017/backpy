def fixed_percent(data, args):

    # value = args["stop_loss_value"] if mode == "loss" else args["stop_gain_value"]
    stoped_returns = data["returns"].copy()
    y_close = data["close"].shift(1)

    indexes = data["close"].index
    symbols = data["returns"].columns
    for ind in indexes:
        for symbol in symbols:
            if args["stop_loss_fixed"] and data["low"].loc[ind, symbol] < y_close.loc[ind, symbol] * (1-args["stop_loss_fixed"]):
                stoped_returns.loc[ind, symbol] = -args["stop_loss_fixed"] 
            elif args["stop_gain_fixed"]  and data["high"].loc[ind, symbol] > y_close.loc[ind, symbol] * (1+args["stop_gain_fixed"] ):
                stoped_returns.loc[ind, symbol] = args["stop_gain_fixed"] 

    return stoped_returns
