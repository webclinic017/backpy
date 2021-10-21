from matplotlib import pyplot as plt
from itertools import product
import multiprocessing
import time
from datetime import datetime

from satoshi import run_strat

def run_experiments():
    start_time = time.time()

    parameters = {
        "start_date": [
            "2019-12-01",
            "2020-03-01",
            "2020-06-01",
            "2020-09-01",
        ],
        "end_date": [
            "2020-12-01",
            "2021-03-01",
            "2021-06-01",
            "2021-09-01",
        ]
    }

    experiments = [dict(zip(parameters.keys(), value))
                   for value in product(*parameters.values())]

    labels = [f"{str(experiment['start_date']).split('-')[1]} {str(experiment['end_date']).split('-')[1]}" for experiment in experiments]

    with multiprocessing.Pool() as p:
        all_metrics = p.map(run_experiment, experiments)


    end_time = time.time()
    print(f"{(end_time - start_time):.2f}s")

    fig, ax = plt.subplots()

    x_metric = [metric["draw_down"] for metric in all_metrics]
    y_metric = [metric["nav"] for metric in all_metrics]

    plt.xlabel("Maximum Drawdown")
    plt.ylabel("Final Net Asset Value")

    ax.scatter(x_metric, y_metric)

    for i, label in enumerate(labels):
        ax.annotate(label, (x_metric[i], y_metric[i]))

    plt.show()


def run_experiment(experiment):
    metrics, _ = run_strat(experiment)
    return {
        "nav": float(metrics["Final NAV"]),
        "sharpe": float(metrics["Sharpe Ratio"]),
        "draw_down": float(metrics["Max-Drawdown"])
    }


if __name__ == "__main__":
    run_experiments()
