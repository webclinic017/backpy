from satoshi import run_strat
import pandas as pd
import matplotlib.pyplot as plt
import datetime
START_DATE = "2020-08-01"


def main():
    brokers = ["Bitso"]
    floors = [0.7]
    multipliers = [1.5]
    positions = [2, 5]
    performances = pd.DataFrame()

    common = {
        "year": datetime.datetime.now().year,
        "launch_date": "August 1, 2020",
        "end_date": "July 1, 2021"
    }

    fact_sheets = {
        "BTC/ETH": {
            "portfolio_name": "BTC/ETH",
            "investment_objective": "Gain exposure to the top coins in the crypto space, which represent over 60 % of the crypto market capitalization.",
            "rebalance_frecuency": "Monthly",
            "weighting_method": "Market-cap hybrid",
            "portfolio_description_1": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eleifend ipsum quis sem hendrerit suscipit vitae at augue. Morbi massa diam, condimentum eget porta ut, viverra at lectus. Fusce commodo laoreet neque sit amet rutrum. Quisque vehicula risus felis, eu interdum ante egestas vitae. ",
            "portfolio_description_2": "Nullam sollicitudin eros at ex pharetra, sed eleifend risus gravida. Nulla sit amet magna id arcu ullamcorper pretium nec a enim. Nam eu pharetra est. Etiam congue turpis non sapien accumsan, vitae vehicula ante feugiat. Morbi sollicitudin urna",
            "methodology_1": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eleifend ipsum quis sem hendrerit ",
            "methodology_2": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eleifend ipsum quis sem hendrerit s",
            "portfolio_attributes_strategy": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eleifend ipsum quis sem hendrerit s",
            "portfolio_attributes_rebalancing": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eleifend ipsum quis sem hendrerit s",

        }
    }
    for b in brokers:
        for f in floors:
            for m in multipliers:
                for p in positions:
                    args = {
                        "strategy": "TopN",
                        "start_date": START_DATE,
                        "fee": 0,
                        "sizer": "power_cap",
                        "diversification_factor": 1,
                        "management_commission": 0,
                        "success_commission": 0,
                        "top": 10,
                        "data": "cmc",
                        "broker": b,
                        "cppi_floor": f,
                        "cppi_multiplier": m,
                        "max_positions": p,
                    }
                    _, performance, weights = run_strat(args)
                    metrics = compute_metrics(performance, weights)

    # performances.plot()
    # performances.to_csv("/home/edg/Desktop/cppi_results.csv")
    # plt.show()


def compute_metrics(performance, weights):
    jan_1 = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
    dates = list(filter(lambda d: d >= jan_1, list(performance.index)))

    time_frames = {
        "1M": performance.tail(30),
        "3M": performance.tail(90),
        "YTD": performance.loc[dates],
        "12M": performance.tail(360),
        "18M": performance.tail(540),
    }

    print(time_frames)


if __name__ == "__main__":
    main()
