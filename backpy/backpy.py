import os
import argparse

os.environ['environment'] = 'PROD' #TEST, PROD
ENVIRONMENT = os.environ["environment"]

if ENVIRONMENT == "TEST":
    from strategies._strat_dict import strategies
    from utils import charge_fees, charge_commissions, load_data
    import utils as ut
else:
    from .strategies._strat_dict import strategies
    from . import utils as ut
    from .utils import charge_fees, charge_commissions, load_data


CEREBRO_PATH = os.environ["CEREBRO_PATH"]


def get_args(meta_args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-start_date", default="2010-01-01")
    parser.add_argument("-end_date", default="3000-01-01")
    parser.add_argument("-strategy", required=False)
    parser.add_argument("-plot", required=False)
    parser.add_argument("-save", required=False)
    parser.add_argument("-top", default=30)
    parser.add_argument("-sizer", default="equal")
    parser.add_argument("-fee", default=0.001)
    parser.add_argument("-max_weight", default=1)
    parser.add_argument("-train", default=False)
    parser.add_argument("-profile", default=False)
    parser.add_argument("-parallel", default=False)
    parser.add_argument("-data", default="quandl")
    parser.add_argument("-factor", default=0)
    parser.add_argument("-market", default="spot")
    parser.add_argument("-live", default=False)
    parser.add_argument("-cppi_floor", default=-1)
    parser.add_argument("-cppi_multiplier", default=-1)

    parser.add_argument("-diversification_factor", default=0)
    parser.add_argument("-success_commission", default=0)
    parser.add_argument("-management_commission", default=0)
    parser.add_argument("-fast_period", default=0)
    parser.add_argument("-slow_period_mult", default=0)
    parser.add_argument("-predicted_symbol", default="BTC")
    parser.add_argument("-broker", default="Binance")
    parser.add_argument("-max_positions", default=10)

    parser.add_argument("-stop_loss_fixed", default=None)
    parser.add_argument("-stop_gain_fixed", default=None)

    args = ut.get_args(parser.parse_args(), meta_args)
    return args


def run_strat(strategy, data, args):
    initial_cash = 100

    # data = ut.add_short_returns(data)
    # data = ut.add_short_ohlc(data)

    data = strategy.add_indicators(data, args)
    weights = strategy.compute_weights(data, args)

    data = ut.filter_dates(data, args["start_date"], args["end_date"])
    if args["cppi_floor"] != -1:
        if args["cppi_multiplier"] == -1:
            raise Exception("You must add cpp_multiplier flag to use CPPI")
        weights = ut.apply_cppi(
            data, weights, args["cppi_floor"], args["cppi_multiplier"], initial_cash)

    performance = ut.compute_performance(weights, data, initial_cash)
    performance = charge_fees(weights, performance, initial_cash, args["fee"])
    performance = charge_commissions(performance, data["close"]["BTC"], args["management_commission"], args["success_commission"], int(
        str(args["start_date"]).split("-")[-1][:2]))

    metrics = ut.compute_metrics(performance)
    print(metrics)

    # ut.save_output(weights, args, performance, metrics)
    # if args["plot"]:
    #     ut.plot(data, performance, strategy, metrics, weights, args)

    return metrics, performance, weights


def main():
    meta_args = {
        "strategy": "TopN",
        "start_date": "2020-08-01",
        "fee": 0,
        "sizer": "power_cap",
        "diversification_factor": 1,
        "management_commission": 0,
        "success_commission": 0,
        "save": "TopN",
        "data": "cmc",
        "plot": True,
        "cppi_floor": 0.6,
        "cppi_multiplier": 1,
        "plot": True
    }
    args = get_args(meta_args)
    strategy = strategies[args["strategy"]](args)
    data = load_data(args, strategy)
    data["returns"] = data["close"].pct_change()
    metrics, performance, weights = run_strat(strategy, data, args)
    print(metrics)
    print(performance)
    print(weights)


# if __name__ == "__main__":
#     do_profiling = False
#     if do_profiling:
#         with cProfile.Profile() as pr:
#             main()

#         with open('./profiling_stats.txt', 'w') as stream:
#             stats = Stats(pr, stream=stream)
#             stats.strip_dirs()
#             stats.sort_stats('time')
#             stats.dump_stats('.prof_stats')
#             stats.print_stats()
#     else:

if __name__ == "__main__":
    main()
