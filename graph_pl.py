import csv
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates

from matplotlib.pyplot import figure


def graph_pl(input_file, output_file, liquidity_graph_file):
    figure(figsize=(12, 6), dpi=80)

    data = pd.read_csv(input_file)


    spyPL = list(data["SPY %p/l"])
    myPL = list(data["%p/l"])
    percent_liquid = list(data["percent liquid"])
    dates = list(data["date"])
    datetimes = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date() for d in dates]
    # y = range(len(datetimes))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

    plt.plot(datetimes, spyPL, label="SPY PL")
    plt.plot(datetimes, myPL, label="My PL")
    # plt.plot(x,y)
    plt.gcf().autofmt_xdate()


    plt.ylabel("% PL")
    plt.xlabel("Date")
    plt.legend(loc="upper left")
    plt.savefig(output_file)

    plt.plot(datetimes, percent_liquid, label="Percent Liquid")


    plt.savefig(liquidity_graph_file)
    plt.clf()


if __name__ == "__main__":
    graph_pl("output/PortfolioProfit_2019JumpSell.csv", "output/AAAAAAAAAAAAAA.png", "output/AAAAAAAAAAAAAAB.png")

