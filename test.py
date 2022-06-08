# Runs to localhost:5000

import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Flask, render_template
from flask import Response
import io
from requests import get
from datetime import datetime
from sklearn.datasets import load_iris
import pandas as pd

app = Flask(__name__)
County = "Uppsala"


def load_data():
    dir = '/home/toidface/Documents/GoHome/csv'
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d")
    csv_filepath = "/Hemnet-" + County + dt_string + ".csv"
    filename = dir + csv_filepath
    df = pd.read_csv(filename)
    # print(df[['size','final_price']].dtypes)
    return df


def plot_scatter(dataframe):
    N = len(dataframe)
    fig, ax = plt.subplots(figsize=(20, 5))
    dataframe[['size']] = dataframe[['size']].apply(
        pd.to_numeric, errors='coerce')
    x = dataframe[['size']]
    y = dataframe[['final_price']]
    colors = np.random.rand(N)
    area = 2  # 0 to 15 point radii

    ax.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.xlabel("Size[m²]")
    plt.ylabel("Cost [kr]")
    plt.savefig('args')
    plt.show()
    return fig


def plot_bar(dataframe):
    dataframe[["final_price"]] = dataframe[["final_price"]]/1000000
    dataframe["location"] = dataframe["location"].str.title()
    data = dataframe.groupby(["location"])["final_price"].mean()
    data = data.sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 15))
    x_lab = data.index.values
    y = data
    bars = ax.barh(x_lab, y)
    ax.bar_label(bars, x_lab, label_type='center')

    plt.xlabel("Cost [Mkr]")
    plt.ylabel("Location")
    plt.yticks([])
    plt.show()
    return fig


if __name__ == "__main__":
    print("HYYY")
    df = load_data()
    plot_bar(df)
