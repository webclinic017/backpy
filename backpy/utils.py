
import ast
from datetime import datetime
import empyrical as emp
import pandas as pd
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import os
from requests import Session
import json
from pathlib import Path
from google.cloud import bigquery
from consts import CMC_KEY

if __package__ is None or __package__ == '':
    from stops._stops_dict import stops
else:
    from .stops._stops_dict import stops

key_path = "./lambda1-bigquery-service-account.json"

bq_client = bigquery.Client.from_service_account_json(key_path)


# DATASETS_PATH = os.environ["DATASETS_PATH"]
# CEREBRO_PATH = os.environ["CEREBRO_PATH"]
# cmk_path = f"{DATASETS_PATH}mod/cmk/"


def get_args(parsed_args, meta_args):
    args = {arg: getattr(parsed_args, arg) for arg in vars(parsed_args)}
    for key, value in args.items():
        try:
            args[key] = ast.literal_eval(value)
        except:
            continue

    for arg in meta_args:
        args[arg] = meta_args[arg]

    args["start_date"] = datetime.strptime(args["start_date"], "%Y-%m-%d")
    args["end_date"] = datetime.strptime(args["end_date"], "%Y-%m-%d")
    return args


def compute_metrics(performance):
    returns = performance.pct_change().fillna(0)
    num_days = len(performance)
    metrics = {
        "Final NAV": performance[-1],
        "Sharpe Ratio": emp.sharpe_ratio(returns),
        "CAGR": emp.cagr(returns),
        "Sortino": emp.sortino_ratio(returns),
        "Max-Drawdown": emp.max_drawdown(returns) * 100,
        "returns-1M": performance.iloc[-1]/ performance.iloc[max(-30, -1*num_days)],
        "returns-3M": performance.iloc[-1]/ performance.iloc[max(-90, -1*num_days)],
        "returns-YTD": performance.iloc[-1]/ performance.loc["2021-01-01"],
        "returns-12M": performance.iloc[-1]/ performance.iloc[max(-364, -1*num_days)],
    }

    return metrics


def filter_dates(datas, start_date, end_date):
    for name, df in datas.items():
        if name != "constituents":
            dates = list(filter(lambda d: d >= start_date and d <=
                                end_date, list(datas[name].index)))
            datas[name] = df.loc[dates]
    return datas


def plot(data, performance, strategy, metrics, weights, args, benchmark="BTC"):
    fig = plt.figure()
    gs = GridSpec(2, 1, height_ratios=[4, 1])

    ax1 = fig.add_subplot(gs[0])
    ax1.plot(performance / performance.iloc[0], label=args["strategy"])
    ax1.plot((data["close"][benchmark] / data["close"]
              [benchmark].iloc[0]), label=benchmark)
    ax1.set_title('Strategy Results')
    ax1.set_ylabel('Performance')
    ax1.grid(True)
    ax1.legend(loc='upper left', shadow=True)

    ax2 = fig.add_subplot(gs[1])
    ax2.plot(weights.sum(axis=1), label="Invested Cash", color="green")
    # if "etf_sma_slow" in data:
    #     market_filter = (data["etf_close"]["SPY"] >= data["etf_sma_slow"]["SPY"] * strategy.params["market_filter_margin"]).astype(int)
    #     ax2.plot(market_filter, label="Market Filter")
    ax2.legend(loc='lower left', shadow=True)
    ax2.tick_params(labelbottom=False)

    plt.show()


# def save_output(weights, args, performance, metrics):
#     if args["save"]:
#         paths = ["performance", "weights", "positions", "metrics"]
#         for path in paths:
#             Path(
#                 f"{CEREBRO_PATH}results/values/{path}/").mkdir(parents=True, exist_ok=True)
#         performance.to_csv(
#             f"{CEREBRO_PATH}results/values/performance/{args['save']}.csv")
#         if args["data"] == "performance":
#             weights = compute_optimized_weights(weights, args["strategies"])
#         weights.to_csv(
#             f"{CEREBRO_PATH}results/values/weights/{args['save']}.csv")
#         positions = compute_positions(weights)
#         positions.to_csv(
#             f"{CEREBRO_PATH}results/values/positions/{args['save']}.csv", index=False)
#         metrics.to_csv(
#             f"{CEREBRO_PATH}results/values/metrics/{args['save']}.csv", index=False)


def charge_fees(weights, performance, initial_cash, fee=0.001):  # TODO: verify
    returns = performance.pct_change().fillna(0)
    weights_change = (weights - weights.shift(1).fillna(0)).abs().sum(axis=1)
    new_navs = []
    for wc, r in zip(weights_change, returns):
        last_nav = new_navs[-1] if len(new_navs) != 0 else initial_cash
        new_nav = (last_nav - last_nav * wc * fee) * (1+r)
        new_navs.append(new_nav)

    return pd.DataFrame(new_navs, index=performance.index).iloc[:, 0]


def charge_commissions(performance, btc_close, management_commission, success_commission, charge_day):
    new_navs = []
    returns = performance.pct_change().fillna(0)
    last_month_btc = None
    last_month_nav = None
    for date, r in zip(performance.index, returns):
        month_day = int(str(date).split("-")[-1][:2])
        last_nav = new_navs[-1] if len(new_navs) != 0 else performance[0]
        nav = last_nav * (1+r)

        if month_day == charge_day:

            alpha_charge = 0
            management_charge = 0
            if last_month_nav:
                btc_alpha = (btc_close.loc[date] -
                             last_month_btc) / last_month_btc
                strat_alpha = (nav - last_month_nav) / last_month_nav
                alpha_charge = max(0, (strat_alpha - btc_alpha)
                                   * success_commission * nav)

                management_charge = nav * management_commission

            nav = nav - management_charge - alpha_charge

            last_month_btc = btc_close.loc[date]
            last_month_nav = nav

        new_navs.append(nav)
    return pd.DataFrame(new_navs, index=performance.index).iloc[:, 0]


def compute_positions(weights):
    data = []
    for index, row in weights.iterrows():
        weights_sum = sum(row)
        for symbol, weight in row.items():
            side = "short" if "s" in symbol else "long"
            symbol = symbol.replace("s", "")
            if weight > 0.001:
                data.append({
                    "date": datetime.strftime(index.date(), "%Y-%m-%d"),
                    "symbol": symbol,
                    "weight": weight,
                    "side": side,
                    "price_limit": 0,
                    "stop_perc": 0.15,
                    # "stop_perc": round(1-self.params["trailing_percent"], 3),
                    "strategy": "None",
                })
        if weights_sum < 0.999:
            data.append({
                "date": datetime.strftime(index.date(), "%Y-%m-%d"),
                "symbol": "USDT",
                "weight": 1-weights_sum,
                "side": "long",
                "price_limit": 0,
                "stop_perc": 0,
                # "stop_perc": round(1-self.params["trailing_percent"], 3),
                "strategy": "None",
            })

    return pd.DataFrame.from_records(data)


def get_bq_data():
    bq_table_id = "lambda1-299719.crypto_cmk.mod_daily_"
    data = {
        "open": bq_query(bq_table_id+"open"),
        "high": bq_query(bq_table_id+"high"),
        "low": bq_query(bq_table_id+"low"),
        "close": bq_query(bq_table_id+"close"),
        "volume": bq_query(bq_table_id+"volume"),
        "cap": bq_query(bq_table_id+"marketcap"),
    }
    for k, df in data.items():
        df.columns = [name.replace("_", "") for name in df.columns]
        df['date'] = pd.to_datetime(df['date'])
        data[k] = df.set_index('date')
        data[k] = data[k].fillna(method='ffill').fillna(method='bfill')
    data["returns"] = data["close"].pct_change()
    return data


def bq_query(
    table_id: str,
    bigquery_client=bq_client,
):
    filtering_query = f"""
            SELECT *
            FROM {table_id}
            ORDER BY date
        """

    query_job = bigquery_client.query(filtering_query)
    df = query_job.to_dataframe()

    return df


def load_data(args, strategy):
    data = get_bq_data()
    return data


# def load_cmc_data(args) -> dict:
#     crypto_open = pd.read_csv(
#         cmk_path + f"metasets/open.csv", index_col="date", parse_dates=["date"])
#     crypto_high = pd.read_csv(
#         cmk_path + f"metasets/high.csv", index_col="date", parse_dates=["date"])
#     crypto_close = pd.read_csv(
#         cmk_path + f"metasets/close.csv", index_col="date", parse_dates=["date"])
#     crypto_low = pd.read_csv(
#         cmk_path + f"metasets/low.csv", index_col="date", parse_dates=["date"])
#     crypto_volume = pd.read_csv(
#         cmk_path + f"metasets/volume.csv", index_col="date", parse_dates=["date"])
#     crypto_cap = pd.read_csv(
#         cmk_path + f"metasets/market_cap.csv", index_col="date", parse_dates=["date"])
#     daily_constituents = pd.read_csv(
#         cmk_path + f"top_caps/{args['top']}.csv", index_col="date", parse_dates=["date"])

    # data = {
    #     "open": crypto_open,
    #     "high": crypto_high,
    #     "low": crypto_low,
    #     "close": crypto_close,
    #     "volume": crypto_volume,
    #     "cap": crypto_cap,
    #     # "current_constituents": daily_constituents,
    # }

    # if args["live"]:
    #     data = add_current_data(data)

    # return data


def add_current_data(data):
    symbols = list(data["close"].columns)
    price_data = get_current_price_data(symbols)
    cap_data = get_current_cap_data(symbols)
    data = add_data(data, price_data, cap_data)
    return data


def get_current_price_data(symbols):
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_KEY,
    }

    session = Session()
    session.headers.update(headers)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/latest'
    symbols_str = ",".join(symbols)
    parameters = {
        "symbol": symbols_str
    }
    try:
        response = session.get(url, params=parameters)
        datas = json.loads(response.text)['data']
        for _, data in datas.items():
            data["quote"]["USD"]["cap"] = 0  # TODO: get real cap data

        return datas
    except Exception as e:
        raise Exception(e)


def get_current_cap_data(symbols):
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_KEY,
    }

    session = Session()
    session.headers.update(headers)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    try:
        response = session.get(url)
        datas = json.loads(response.text)["data"]
        caps = {symbol: None for symbol in symbols}
        for data in datas:
            caps[data["symbol"]] = data["quote"]["USD"]["market_cap"]
        return caps
    except Exception as e:
        raise Exception(e)


def add_data(data, price_data, cap_data):
    frame_names = ['open', 'high', 'low', 'close', 'volume']
    new_index = list(data["open"].index)[-1] + pd.DateOffset(1)
    for frame_name in frame_names:
        data[frame_name] = add_price_data(
            frame_name, data[frame_name], price_data, new_index)

    data = add_cap_data(data, cap_data, new_index)
    # data["current_constituents"].loc[new_index] = data["current_constituents"].iloc[-1]
    return data


def add_price_data(frame_name, frame, new_data, new_index):
    d = {symbol: v["quote"]["USD"][frame_name]
         for symbol, v in new_data.items()}
    values = [d[symbol] if symbol in d.keys(
    ) else None for symbol in list(frame.columns)]
    frame.loc[new_index] = values
    frame = frame.fillna(method='ffill')
    return frame


def add_cap_data(data, cap_data, new_index):
    values = [cap_data[symbol] if symbol in cap_data.keys(
    ) else None for symbol in list(data["cap"].columns)]
    data["cap"].loc[new_index] = values
    return data


# def load_performance_data(args, strategy) -> dict:
#     cerebro_path = f"{CEREBRO_PATH}results/values/performance/"
#     # files = os.listdir(cerebro_path)
#     files = strategy.params["strategies"]
#     close = None
#     for file in files:
#         df = pd.read_csv(cerebro_path+file+".csv",
#                          index_col=["date"], parse_dates=["date"])
#         if close is None:
#             close = pd.DataFrame(index=df.index)
#         close[file] = df.iloc[:, 0]

#     crypto_close = pd.read_csv(
#         cmk_path + f"metasets/close.csv", index_col="date", parse_dates=["date"])
#     close["BTC"] = crypto_close["BTC"]
#     daily_constituents = pd.read_csv(
#         cmk_path + f"top_caps/{args['top']}.csv", index_col="date", parse_dates=["date"])

#     df = pd.DataFrame()
#     data = {
#         "open": df,
#         "high": df,
#         "low": df,
#         "close": close,
#         "volume": df,
#         "cap": df,
#         # "current_constituents": daily_constituents,
#     }

#     if args["live"]:
#         new_index = list(data["close"].index)[-1]
#         # data["current_constituents"].loc[new_index] = data["current_constituents"].iloc[-1]

#     return data


# def compute_optimized_weights(weights, strategies):
#     weights = weights[strategies]
#     strategies = weights.columns

#     frames = {}
#     weights_path = f"{CEREBRO_PATH}results/values/weights/"
#     for strategy in strategies:
#         df = pd.read_csv(weights_path + strategy + ".csv",
#                          index_col="date", parse_dates=["date"])
#         frames[strategy] = df

#     d = {}
#     for date in list(weights.index):
#         strat_day_weights = weights.loc[date].to_dict()
#         strats_weights = []
#         for strat, weight in strat_day_weights.items():
#             row = frames[strat].loc[date] * weight
#             strats_weights.append(row)
#         d[date] = sum(strats_weights).values

#     final_weights = pd.DataFrame.from_dict(
#         d, orient="index", columns=frames[strategies[0]].columns)
#     final_weights.index.name = "date"
#     return final_weights


def compute_performance(weights, data, initial_cash):
    weighted_returns = weights * data["returns"].shift(-1)
    performance = (1 + weighted_returns.sum(axis=1)).cumprod() * initial_cash
    performance[0] = initial_cash
    return performance


def apply_cppi(data, weights, floor_value, multiplier, initial_cash, days=30):
    performance = compute_performance(weights, data, initial_cash)
    floors = performance.rolling(days).max().fillna(initial_cash) * floor_value
    invested_percents = (multiplier * (performance-floors)/100).clip(0, 1)
    for date, row in weights.iterrows():
        invested_percent = invested_percents.loc[date]
        weights.loc[date] = row * invested_percent
    return weights


def compute_stoped_returns(data: dict, args: dict) -> dict:
    if args["stop_loss_fixed"] or args["stop_gain_fixed"]:
        return stops["fixed_percent"](data, args)
    # elif args["stop_loss_percent"]:

    return data["returns"]


def compute_weighted_returns(weights, data, args) -> pd.DataFrame:

    stoped_returns = compute_stoped_returns(data, args)

    # weighted_returns = weights.shift(1) * data["returns"]
    weighted_returns = weights.shift(1) * stoped_returns
    return weighted_returns


def add_short_returns(data):
    long_returns = data["close"].pct_change()
    short_returns = data["close"].pct_change() * -1
    short_columns = [f"{symbol}s" for symbol in short_returns.columns]
    short_returns.columns = short_columns
    data["returns"] = pd.concat([long_returns, short_returns], axis=1)
    return data


def add_short_ohlc(data):
    ohlc_dict = compute_ohlc_data(data)
    shorts_dict = compute_shorts_ohlc(ohlc_dict)
    # data = append_short_ohlc(shorts_dict)

    raise ValueError("asdf")
    return data


def compute_ohlc_data(data: dict) -> dict:
    ohlc_dict = {}
    symbols = data["close"].columns
    columns = ["open", "high", "low", "close"]
    for symbol in symbols:
        df = pd.DataFrame()
        for column in columns:
            df[column] = data[column][symbol]
        ohlc_dict[symbol] = df
    return ohlc_dict


def compute_shorts_ohlc(ohlc_dict: dict) -> dict:
    shorts_dict = {}
    symbols = list(ohlc_dict.keys())
    for symbol in symbols:
        shorts_dict[symbol] = compute_short_ohlc(ohlc_dict[symbol])
    return shorts_dict


def compute_short_ohlc(ohlc: pd.DataFrame) -> pd.DataFrame:
    short_ohlc = pd.DataFrame(index=ohlc.index, columns=ohlc.columns)
    short_returns = ohlc.pct_change().fillna(1)  # Todo: dapt high,low and close
    yesterday = None
    for i, today in enumerate(ohlc.index):
        for col in ohlc.columns:
            val = 1
            if col == "open" and i != 0:
                val = short_ohlc.loc[yesterday]["close"]
            if col == "high":
                val = short_ohlc.loc[today]["open"] * \
                    (1 - short_returns.loc[today]["high"])
            if col == "low":
                val = short_ohlc.loc[today]["open"] * \
                    (1 - short_returns.loc[today]["low"])
            if col == "close":
                val = short_ohlc.loc[today]["open"] * \
                    (1 - short_returns.loc[today]["close"])
            short_ohlc.loc[today, col] = val

        yesterday = today
    return short_ohlc



