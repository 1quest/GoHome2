# Runs to localhost:5000

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template
from flask import Response
import io
from datetime import datetime
import plotly
import plotly.graph_objs as go
import pandas as pd
import json
from math import log10

app = Flask(__name__)
County = "Uppsala"
matplotlib.use('Agg')


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/')
def index():
    df = load_data()
    bar_plot = notdash_bar(df)
    scatter_plot = notdash_scatter(df)
    return render_template('index.html', plot=bar_plot, scatter=scatter_plot)


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
    fig, ax = plt.subplots(figsize=(8, 8))
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


def notdash_bar(dataframe):
    dataframe[["final_price"]] = dataframe[["final_price"]]/1000000
    dataframe["location"] = dataframe["location"].str.title()
    data = dataframe.groupby(["location"])["final_price"].mean()
    data = data.sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(12, 15))
    x_lab = data.index.values
    y = data
    df = pd.DataFrame({'x': x_lab, 'y': y})  # creating a sample dataframe

    data = [
        go.Bar(
            x=df['y'],  # assign x as the dataframe column 'x'
            y=df['x'], orientation='h')
    ]
    data = go.Figure(data).update_layout(title="Area vs Cost",
                                         autosize=True, height=800,).update_xaxes(title="Cost [Mkr]").update_yaxes(title="Area")

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def notdash_scatter(dataframe):
    dataframe[['size']] = dataframe[['size']].apply(
        pd.to_numeric, errors='coerce')
    data = go.Figure()
    room_types = dataframe.drop_duplicates(subset=['num_of_rooms'])
    room_types = room_types['num_of_rooms'].sort_values()
    # loop over number of rooms

    # add dots and name sequence
    for x in room_types:
        dataframe_filtered = dataframe.loc[dataframe['num_of_rooms']
                                           == x]
        data = data.add_trace(go.Scatter(x=dataframe_filtered['final_price'],  # assign x as the dataframe column 'x'
                                         y=dataframe_filtered['size'], mode='markers', customdata=dataframe_filtered['num_of_rooms'], name="Rooms: " + str(round(x, 1))))
    data = data.update_layout(title="Size vs Cost", showlegend=True,
                              autosize=True, height=800,)
    data = data.update_xaxes(title="Cost [Mkr]").update_yaxes(title="Size[m²]")
    data = data.update_traces(hovertemplate="<br>".join(
        ["Size: %{y}m²", "Cost: %{x} Mkr", "Rooms: %{customdata}"])).update_xaxes(type="log")
    data.show()
    return "graphJSON"


if __name__ == "__main__":
    print("HYYY")
    df = load_data()
    notdash_scatter(df)
