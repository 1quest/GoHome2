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


def load_data():
    dir = '/home/toidface/Documents/GoHome/csv'
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d")
    csv_filepath = "/Hemnet-" + dt_string + ".csv"
    filename = dir + csv_filepath
    df = pd.read_csv(filename)
    # print(df[['size','final_price']].dtypes)
    return df


def plot_scatter(dataframe):
    N = len(dataframe)
    dataframe[['size']] = dataframe[['size']].apply(
        pd.to_numeric, errors='coerce')
    test = dataframe[['size']]
    print(test)
    x = dataframe[['size']]
    y = dataframe[['final_price']]
    colors = np.random.rand(N)
    area = (30 * colors)**2  # 0 to 15 point radii

    plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.xlabel("Size[m²]")
    plt.ylabel("Cost [kr]")
    plt.show()


if __name__ == "__main__":
    df = load_data()
    plot_scatter(df)
