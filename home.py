# Runs to localhost:5000

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template
from flask import Response
import io
from datetime import datetime
import pandas as pd

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/plot_scatter.png')
def plot_scatter():
    df = load_data()
    plot_scatter(df)
    fig = plot_scatter(df)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#E8E5DA')
    x = [1, 1, 1, 1]
    y = [2, 2, 2, 2]
    ax.bar(x, y, color="#304C89")

    plt.xticks(rotation=30, size=5)
    plt.ylabel("Expected Clean Sheets", size=5)
    plt.savefig('args')
    return fig


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
    x = dataframe[['size']]
    y = dataframe[['final_price']]
    colors = np.random.rand(N)
    area = (30 * colors)**2  # 0 to 15 point radii

    fig = plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.xlabel("Size[m²]")
    plt.ylabel("Cost [kr]")
    return fig
