def equal(symbols, date, data, args):
    weights = {}
    for symbol in symbols:
        weights[symbol] = 1/len(symbols)

    return weights