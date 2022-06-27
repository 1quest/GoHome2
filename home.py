# Runs to localhost:5000

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template
from flask import Response, request
import io
from datetime import datetime
import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import ipywidgets

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


@app.route('/future', methods=['POST', 'GET'])
def future():
    df = load_future_data()
    bar_plot = notdash_future_bar(df)
    scatter_plot = ass_notdash_future_scatter_widget(df)
    return render_template('future.html', plot=bar_plot, scatter=scatter_plot)


@app.route('/callback', methods=['POST', 'GET'])
def cb():
    print("HELLO")
    df = load_future_data()
    # ass(request.args.get('data'))
    return ass_notdash_future_scatter_widget(df)


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
    csv_filepath = "/Hemnet_sold-" + County + dt_string + ".csv"
    filename = dir + csv_filepath
    df = pd.read_csv(filename)
    # print(df[['size','final_price']].dtypes)
    return df


def load_future_data():
    dir = '/home/toidface/Documents/GoHome/csv'
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d")
    csv_filepath = "/Hemnet_future-" + County + dt_string + ".csv"
    filename = dir + csv_filepath
    df = pd.read_csv(filename)
    # print(df[['size','final_price']].dtypes)
    return df


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
    data = go.Figure(data).update_layout(title="City Area vs Cost",
                                         autosize=True,
                                         height=800,)
    data = data.update_xaxes(title="Cost [Mkr]")
    data = data.update_yaxes(title="City Area")

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
        data = data.add_trace(go.Scatter(x=dataframe_filtered['final_price'],
                                         y=dataframe_filtered['size'],
                                         mode='markers',
                                         customdata=dataframe_filtered['num_of_rooms'],
                                         name="Rooms: " + str(round(x, 1))))
    data = data.update_layout(title="Size vs Cost", showlegend=True,
                              autosize=True, height=800,)
    data = data.update_xaxes(
        title="Log. Cost [Mkr]").update_yaxes(title="Size[m²]")
    data = data.update_traces(hovertemplate="<br>".join(
        ["Size: %{y}m²", "Cost: %{x} Mkr", "Rooms: %{customdata}"]))
    data = data.update_xaxes(type="log")

    # data = [data]
    graphJSON = json.dumps(
                             data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def notdash_future_bar(dataframe):
    dataframe[["price"]] = dataframe[["price"]].apply(
        pd.to_numeric, errors='coerce')/1000000
    dataframe["location"] = dataframe["location"].str.title()
    data = dataframe.groupby(["location"])["price"].mean()
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
    data = go.Figure(data).update_layout(title="City Area vs Cost",
                                         autosize=True,
                                         height=800,)
    data = data.update_xaxes(title="Cost [Mkr]")
    data = data.update_yaxes(title="City Area")

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def notdash_future_scatter(dataframe):
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
        data = data.add_trace(go.Scatter(x=dataframe_filtered['price'],
                                         y=dataframe_filtered['size'],
                                         mode='markers',
                                         customdata=dataframe_filtered['num_of_rooms'],
                                         name="Rooms: " + str(round(float(x), 1))))
    data = data.update_layout(title="Size vs Cost", showlegend=True,
                              autosize=True, height=800,)
    data = data.update_xaxes(
        title="Log. Cost [Mkr]").update_yaxes(title="Size[m²]")
    data = data.update_traces(hovertemplate="<br>".join(
        ["Size: %{y}m²", "Cost: %{x} Mkr", "Rooms: %{customdata}"]))
    data = data.update_xaxes(type="log")

    # data = [data]
    graphJSON = json.dumps(
                             data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def notdash_future_scatter_widget(dataframe):
    dataframe[['size']] = dataframe[['size']].apply(
        pd.to_numeric, errors='coerce')
    data = go.Figure()
    room_types = dataframe.drop_duplicates(subset=['num_of_rooms'])
    room_types = room_types['num_of_rooms'].sort_values()
    # loop over number of rooms

    # add dots and name sequence
    for x in [1]:  # room_types:
        dataframe_filtered = dataframe.loc[dataframe['num_of_rooms']
                                           == x]
        data = data.add_trace(go.Scatter(x=dataframe_filtered['price'],
                                         y=dataframe_filtered['size'],
                                         mode='markers',
                                         customdata=dataframe_filtered['num_of_rooms'],
                                         name="Rooms: " + str(round(float(x), 1))))
    # data = data.update_layout(title="Size vs Cost", showlegend=True,
    #                           autosize=True, height=800,)
    # data = data.update_xaxes(
    #     title="Log. Cost [Mkr]").update_yaxes(title="Size[m²]")
    # data = data.update_traces(hovertemplate="<br>".join(
    #     ["Size: %{y}m²", "Cost: %{x} Mkr", "Rooms: %{customdata}"]))
    # data = data.update_xaxes(type="log")

    data = go.FigureWidget(data)
    scatter = data.data[0]
    colors = ['#a3a7e4'] * 100

    scatter.marker.color = colors
    scatter.marker.size = [10] * 100
    data.layout.hovermode = 'closest'

    def update_point(trace, points, selector):
        c = list(scatter.marker.color)
        s = list(scatter.marker.size)
        for i in points.point_inds:
            c[i] = '#bae2be'
            s[i] = 20
            with data.batch_update():
                scatter.marker.color = c
                scatter.marker.size = s

    scatter.on_click(update_point)

    # data = [data]
    graphJSON = json.dumps(
                             data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def ass_notdash_future_scatter_widget(dataframe):
    np.random.seed(1)

    x = np.random.rand(100)
    y = np.random.rand(100)

    f = go.FigureWidget([go.Scatter(x=x, y=y, mode='markers')])

    scatter = f.data[0]
    colors = ['#a3a7e4'] * 100
    scatter.marker.color = colors
    scatter.marker.size = [10] * 100
    f.layout.hovermode = 'closest'

    # create our callback function
    def update_point(trace, points, selector):
        c = list(scatter.marker.color)
        print("*ASADAs")
        s = list(scatter.marker.size)
        for i in points.point_inds:
            c[i] = '#bae2be'
            s[i] = 20
            with f.batch_update():
                scatter.marker.color = c
                scatter.marker.size = s

    scatter.on_click(update_point)
    # data = [data]
    graphJSON = json.dumps(
                             f, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
