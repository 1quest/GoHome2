# Runs to localhost:5000

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from flask import Flask, render_template
from flask import request
from datetime import datetime
import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import re
import os
import pwd

County = "Uppsala"
user_name = pwd.getpwuid(os.getuid())[0]
matplotlib.use('Agg')
if user_name == 'toidface':
    path_to_csv = "/home/toidface/Documents/GoHome/csv"
    template_dir = "/home/toidface/Documents/GoHome/templates"
elif user_name == 'ubuntu':
    path_to_csv = "/home/ubuntu/GoHome2/csv"
    template_dir = "/home/ubuntu/GoHome2/templates"
else:
    template_dir = '/home/GoHome2/GoHome2/templates/'
    path_to_csv = '/home/GoHome2/GoHome2/csv'

app = Flask(__name__, template_folder=template_dir)


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/')
def index():
    df = load_data()
    bar_plot = bar(df)
    scatter_plot = sold_scatter(df)
    table_apts = table_of_sold_apts(df)

    return render_template('index.html', plot=bar_plot, scatter=scatter_plot,
                           table=table_apts)


@app.route('/future', methods=['POST', 'GET'])
def future():
    df = load_future_data()
    bar_plot = future_bar(df)
    scatter_plot = future_scatter(df)
    table_apts = table_of_future_apts(df)
    return render_template('future.html', plot=bar_plot, scatter=scatter_plot,
                           table=table_apts)


@app.route('/futureareas/', methods=['POST', 'GET'])
def future_areas():
    #df = load_future_data()
    #locations = df["location"].str.title()
    # json.dumps(sorted(dict(locations.drop_duplicates()).values()))
    return "WHAAAGGAGA"


@app.route('/get_areas', methods=['POST', 'GET'])
def areas():
    df = load_data()
    locations = df["location"].str.title()
    return json.dumps(sorted(dict(locations.drop_duplicates()).values()))


@app.route('/callback', methods=['POST', 'GET'])
def callback():
    df = load_future_data()
    df = df[df["num_of_rooms"] == 1.0]
    return future_scatter(df)


@app.route('/sold_filterplots', methods=['POST', 'GET'])
def areafilter():
    df = load_data()
    areas_data = request.args.getlist('areas')
    if(len(request.args.getlist('min_rooms')) > 0 and request.args.getlist('min_rooms')[0] != ''):
        min_rooms_req = float(request.args.getlist('min_rooms')[0])
    else:
        min_rooms_req = 1
    if(len(request.args.getlist('min_rooms')) > 0 and request.args.getlist('max_rooms')[0] != ''):
        max_rooms_req = float(request.args.getlist('max_rooms')[0])
    else:
        max_rooms_req = 10
    if len(areas_data) > 0:
        df = df[df['location'].isin(areas_data)]
    df = df[(df['num_of_rooms'] <= max_rooms_req)
            & (df['num_of_rooms'] >= min_rooms_req)]
    bar_plot = bar(df)
    scatter_plot = sold_scatter(df)
    plots = {"bar_plot": bar_plot, "scatter_plot": scatter_plot}
    plotsJSON = json.dumps(plots, cls=plotly.utils.PlotlyJSONEncoder)
    return plotsJSON


@app.route('/upforsale_filterplots', methods=['POST', 'GET'])
def filter_upforsale():
    df = load_future_data()
    areas_data = request.args.getlist('areas')
    print(request.args)
    if(len(request.args.getlist('min_rooms')) > 0 and request.args.getlist('min_rooms')[0] != ''):
        min_rooms_req = float(request.args.getlist('min_rooms')[0])
    else:
        min_rooms_req = 1
    if(len(request.args.getlist('min_rooms')) > 0 and request.args.getlist('max_rooms')[0] != ''):
        max_rooms_req = float(request.args.getlist('max_rooms')[0])
    else:
        max_rooms_req = 10
    if len(areas_data) > 0:
        df = df[df['location'].isin(areas_data)]
    df = df[(df['num_of_rooms'] <= max_rooms_req)
            & (df['num_of_rooms'] >= min_rooms_req)]
    bar_plot = future_bar(df)
    scatter_plot = future_scatter(df)
    plots = {"bar_plot": bar_plot, "scatter_plot": scatter_plot}
    plotsJSON = json.dumps(plots, cls=plotly.utils.PlotlyJSONEncoder)
    return plotsJSON


@app.route('/scatter_update_table', methods=['POST', 'GET'])
def cb_future_table():
    df = load_future_data()
    df = df.sort_values(by=['index_col'])
    data = request.args.getlist('data')
    df = df.iloc[data]
    return table_of_future_apts(df)


@app.route('/scatter_update_sold_table', methods=['POST', 'GET'])
def cb_sold_table():
    df = load_data()
    df = df.sort_values(by=['index_col'])
    data = request.args.getlist('data')
    df = df.iloc[data]
    return table_of_sold_apts(df)


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
    filename = getlatestfilename('sold')
    df = pd.read_csv(filename)
    df['index_col'] = df.index
    df["location"] = df["location"].str.title()
    return df.sort_values(by=['num_of_rooms', 'size'])


def load_future_data():
    filename = getlatestfilename('future')
    df = pd.read_csv(filename)
    df["location"] = df["location"].str.title()
    df['index_col'] = df.index
    return df.sort_values(by=['num_of_rooms', 'size'])


def getlatestfilename(time):
    file_names = os.listdir(path_to_csv)
    ok_list = [time]
    files = [url for url in file_names if any(sub in url for sub in ok_list)]
    file_name_string = "".join(files)
    numbers = re.compile(r'\d+(?:\.\d+)?')
    numbers_list = numbers.findall(file_name_string)
    latest = sorted(numbers_list, key=lambda d: datetime.strptime(
        d, '%Y%m%d'), reverse=True)[0]
    csv_filepath = path_to_csv + "/Hemnet_" + time + "-" + County + latest + ".csv"
    return csv_filepath


def bar(dataframe):
    print(dataframe[['final_price']])
    dataframe[['final_price']] = dataframe[['final_price']]/1000000
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
                                         height=500)
    data = data.update_xaxes(title="Cost [Mkr]")
    data = data.update_yaxes(title="City Area")

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def sold_scatter(dataframe):
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
                                         customdata=dataframe_filtered['index_col'],
                                         name="Rooms: " + str(round(x, 1))))
    data = data.update_layout(title="Size vs Cost", showlegend=True,
                              autosize=True, height=500,)
    data = data.update_xaxes(
        title="Log. Cost [Mkr]").update_yaxes(title="Size[m²]")
    data = data.update_traces(hovertemplate="<br>".join(
        ["Size: %{y}m²", "Cost: %{x} Mkr"]))
    # "Rooms: %{customdata}
    data = data.update_xaxes(type="log")

    # data = [data]
    graphJSON = json.dumps(
                             data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def future_bar(dataframe):
    dataframe[["price"]] = dataframe[["price"]].apply(
        pd.to_numeric, errors='coerce')/1000000
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
                                         height=500,)
    data = data.update_xaxes(title="Cost [Mkr]")
    data = data.update_yaxes(title="City Area")

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def future_scatter(dataframe):
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
                                         customdata=dataframe_filtered['index_col'],
                                         name="Rooms: " + str(round(float(x),
                                                                    1))))
    data = data.update_layout(title="# Rooms vs Cost", showlegend=True,
                              autosize=True, height=500)
    data = data.update_xaxes(
        title="Log. Cost [Mkr]").update_yaxes(title="Size[m²]")
    data = data.update_traces(hovertemplate="<br>".join(
        ["Size: %{y}m²", "Cost: %{x} Mkr"]))
    # "Rooms: %{customdata}
    data = data.update_xaxes(type="log")

    # data = [data]
    graphJSON = json.dumps(
                             data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def make_clickable(val):
    return '<a href="{}">{}</a>'.format(val, val)


def table_of_future_apts(dataframe):

    dataframe.link = "<a href='" + dataframe.link + \
        "'>[Länk]</a>"

    fig = go.Figure(data=[go.Table(header=dict(values=["Region", "Location",
                                                       "Link",
                                                       "Street Address",
                                                       "# Rooms",
                                                       "Size m²",
                                                       "Fee",
                                                       "Sales Price"]),
                                   cells=dict(values=[dataframe.link,
                                                      dataframe.region,
                                                      dataframe.location,
                                                      dataframe.street_address,
                                                      dataframe.num_of_rooms,
                                                      dataframe['size'],
                                                      dataframe.fee,
                                                      dataframe.price]))
                          ])
    fig = fig.update_layout(title="Listings clicked in scatterplot",
                            autosize=True, height=400)
    graphJSON = json.dumps(
            fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def table_of_sold_apts(dataframe):

    dataframe.link = "<a href='" + dataframe.link + \
        "'>[Länk]</a>"

    fig = go.Figure(data=[go.Table(header=dict(values=["Region", "Location",
                                                       "Link",
                                                       "Street Address",
                                                       "# Rooms",
                                                       "Size m²", "Fee",
                                                       "Final Price",
                                                       "Percentage change",
                                                       "Initial Price"]),
                                   cells=dict(values=[dataframe.region,
                                                      dataframe.location,
                                                      dataframe.link,
                                                      dataframe.street_address,
                                                      dataframe.num_of_rooms,
                                                      dataframe['size'],
                                                      dataframe.fee,
                                                      dataframe.final_price,
                                                      list(
                                                          map(str, dataframe.percentage_change)),
                                                      np.round(dataframe.price/1000000, 2)]))
                          ])
    fig = fig.update_layout(title="Listings clicked in scatterplot",
                            autosize=True, height=400)
    graphJSON = json.dumps(
            fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
