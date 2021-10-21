def power_cap(symbols, date, data, args):
    day_caps = data["cap"].loc[date].sort_values(ascending=False)
    day_caps = day_caps[~day_caps.index.str.contains('USD')]
    day_caps = dict(zip(day_caps.index, day_caps.values))
    
    # div_factor = args["diversification_factor"] if args.get("diversification_factor") else 0
    weights = {symbol: cap**(1-args["diversification_factor"]) for symbol, cap in day_caps.items() if symbol in symbols}
    total_adjusted_cap = sum(weights.values())
    weights = {k: v/total_adjusted_cap for k, v in weights.items()}
    return weights