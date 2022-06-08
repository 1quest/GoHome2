# Runs to localhost:5000

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template
from flask import Response
import io
from datetime import datetime
import pandas as pd
import plotly
import plotly.express as px
import json

app = Flask(__name__)
County = "Uppsala"


@app.route('/')
def index():
    matplotlib.use('Agg')
    JSON = notdash()
    return render_template('index.html', GraphJSON=JSON)


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/plot_scatter.png')
def scatterplot():
    df = load_data()
    plot_scatter(df)
    fig = plot_scatter(df)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/plot_bar.png')
def barplot():
    df = load_data()
    plot_bar(df)
    fig = plot_bar(df)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig, ax = plt.subplots(figsize=(6, 6))
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
    csv_filepath = "/Hemnet-" + County + dt_string + ".csv"
    filename = dir + csv_filepath
    df = pd.read_csv(filename)
    # print(df[['size','final_price']].dtypes)
    return df


def plot_scatter(dataframe):
    N = len(dataframe)
    fig, ax = plt.subplots(figsize=(12, 12))
    dataframe[['size']] = dataframe[['size']].apply(
        pd.to_numeric, errors='coerce')
    x = dataframe[['size']]
    y = dataframe[['final_price']]
    colors = np.random.rand(N)
    area = 2  # 0 to 15 point radii

    ax.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.xlabel("Size[m²]")
    plt.ylabel("Cost [kr]")
    plt.savefig('args', bbox_inches='tight')
    plt.show
    return fig


def plot_bar(dataframe):
    dataframe[["final_price"]] = dataframe[["final_price"]]/1000000
    dataframe["location"] = dataframe["location"].str.title()
    data = dataframe.groupby(["location"])["final_price"].mean()
    data = data.sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(12, 15))
    x_lab = data.index.values
    y = data
    bars = ax.barh(x_lab, y)
    ax.bar_label(bars, x_lab, label_type='center')

    plt.xlabel("Size[m²]")
    plt.subplots_adjust(top=None)
    plt.ylabel("Cost [Mkr]")
    plt.yticks([])
    plt.savefig('args', bbox_inches='tight')
    return fig


def notdash():
    df = pd.DataFrame({
      'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges',
                'Bananas'],
      'Amount': [4, 1, 2, 2, 4, 5],
      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
                    })
    fig = px.bar(df, x='Fruit', y='Amount', color='City',
                 barmode='group')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
