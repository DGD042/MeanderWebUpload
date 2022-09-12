# -*- coding: utf-8 -*-
# _____________________________________________________________________________
# _____________________________________________________________________________
#
#                       Coded by: Daniel Gonzalez-Duque
#                               Last revised 2022-05-20
# _____________________________________________________________________________
# _____________________________________________________________________________
"""
______________________________________________________________________________

 DESCRIPTION:
    This script creates a plot selector embedded in Tkinter to select possible
    meander points

______________________________________________________________________________
"""
# ----------------
# Import packages
# ----------------
# Data
import json
import pickle
# Data Management
import pandas as pd
import numpy as np
from sklearn.metrics import DistanceMetric
# Dash and Plotly
import dash
from dash import html,dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

# Utilities
from utilities import filesManagement as FM
from ReachExtraction import CompleteReachExtraction as CRE


# --------------------
# General Functions
# --------------------
def generate_random_reach(path_data, path_out):
    # --------------------------
    # Load information
    # --------------------------
    data_1703_pd = FM.load_data(f'{path_out}table_HUC04_1703.csv',
                                pandas_dataframe=True)
    data_1703_pd.drop(['Divergence'], axis=1)

    # Get Headwaters
    headwaters = data_1703_pd[data_1703_pd['StartFlag'] == 1]
    # i = 0
    i = np.random.randint(0, len(data_1703_pd))
    comid = headwaters.iloc[i, 0]

    # --------------------------
    # Generate Reach
    # --------------------------
    # time2 = time.time()
    reach_generator = CRE(data_1703_pd, path_data)
    del data_1703_pd
    # time1 = time.time()
    comid_network = reach_generator.map_complete_reach(comid)
    # utl.toc(time1)
    # time1 = time.time()
    data = reach_generator.map_coordinates(comid_network)
    # utl.toc(time1)
    # time1 = time.time()
    data_fitted = reach_generator.fit_splines(data)
    # utl.toc(time1)
    # utl.toc(time2)

    # x = data['x'].values
    # y = data['y'].values
    # x_poly = data_fitted['x_poly'].values
    # y_poly = data_fitted['y_poly'].values

    # --------------------------
    # Plot
    # --------------------------
    return data_fitted, i


def load_river(figure_river, n_clicks_load_river):
    if n_clicks_load_river >= 1:
        path_data = 'demo_data/test_NUC04_1703_database/coordinates/'
        path_out = 'demo_data/test_NUC04_1703_database/'
        data_reach, id_reach = generate_random_reach(path_data, path_out)
        x = data_reach['x_poly']
        y = data_reach['y_poly']
        figure_river = new_river_plot(x, y, id_reach)
        n_clicks_load_river = 0
    return figure_river, n_clicks_load_river


def new_meander(fig_river, n_clicks, clickData, data_meander):
    global points_selected
    global saved_data
    global data_reach
    # global fig_river
    # Populate meanders
    data_meander = data_meander or {'meanders': {},
                                    'id_meanders': ['All', 'None']}
    n_points = len(points_selected)
    msg = (f'Clicks {n_clicks}\nN. Points: {n_points}\nPoints:'
           f' {points_selected}')
    if n_clicks == 0:
        fig_river.update_layout(clickmode='none')
    elif n_clicks >= 1:
        fig_river.update_layout(clickmode='event+select')
        if clickData:
            i_sel = clickData['points'][0]['pointIndex']
            points_selected.append(i_sel)
        data_meander['meanders'][saved_data] = points_selected
        fig_river = update_meander_points(fig_river, data_reach, points_selected)
        n_points = len(points_selected)
    if n_points >= 2:
        points_selected = []
        fig_river.update_layout(clickmode='select')
        data_meander['id_meanders'].append(f'{saved_data:04d}')
        saved_data += 1
        clickData = None
        n_clicks = 0
    return (msg, n_clicks, fig_river, clickData, data_meander)

# Figures
def update_meander_points(fig, data_reach, points_selected):
    n_points = len(points_selected)
    if n_points == 1:
        x_sel_1 = [data_reach['x'][points_selected[-1]]]
        y_sel_1 = [data_reach['y'][points_selected[-1]]]
        fig.add_trace(go.Scatter(x=x_sel_1, y=y_sel_1, mode='markers',
                                 marker=dict(color='red')))
    if n_points >= 2:
        x_sel_2 = [data_reach['x'][points_selected[-1]]]
        y_sel_2 = [data_reach['y'][points_selected[-1]]]
        fig.add_trace(go.Scatter(x=x_sel_2, y=y_sel_2, mode='markers',
                                 marker=dict(color='red')))
        x_sel = data_reach['x'][min(points_selected): max(points_selected)]
        y_sel = data_reach['y'][min(points_selected): max(points_selected)]
        fig.add_trace(go.Scatter(x=x_sel, y=y_sel, line=dict(color='red')))

    return fig

def new_river_plot(x, y, id_reach):
    fig_river = go.Figure()
    fig_river.add_trace(go.Scatter(x=x, y=y, line=dict(color='black')))
    # fig = px.line(data_pd, x='x', y='y', color='Order')
    fig_river.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    fig_river.update_layout(title=f'Reach {id_reach}')
    fig_river.update_layout(uirevision='dont change')
    fig_river.update_layout(showlegend=False)
    return fig_river


# ----------------
# Read Information
# ----------------
points_selected = []
saved_data = 0

# Open Data
# file_open = open('demo_data/data_input.p', "rb")
# data = pickle.load(file_open)
# file_open.close()
# id_reach = 0
# data_reach_all = data[0]
# x = data_reach_all['x_poly']
# y = data_reach_all['y_poly']

x = np.linspace(0, 10, 100)
y = 3 * np.sin(x * np.pi / 2)
z = np.zeros(x.shape)
data_reach = {'x_poly': x, 'y_poly': y}
data_meander = {
    'meanders': {},
    'id_meanders': ['All', 'None']
}

# ----------------
# Create Figure
# ----------------
fig_river = new_river_plot(x, y, 0)

# ----------------
# Web page Styles
# ----------------
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
# ----------------
# Create Dash app
# ----------------
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Meander Characterization: Selecting Meanders in the NHD Datasets"
# ----------------
# Update Layout
# ----------------
app.layout = html.Div(
    children=[
        dcc.Store(id='meanders', data=data_meander),
        #Header
        html.Div(
            children=[
                html.H1(
                children="Meander Characterization", className="header-title"
                ),
                html.P(
                    children="Help us to characterize Meanders in the High"
                             " Resolution National Hydrography"
                             " Dataset (NHDPlus_HR)"
                             " for the continental US.",
                    className='header-description'
                ),
            ],
            className='header'
        ),
        # Body
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children='Load River', className='menu-title'),
                        html.Button('Load Random River',
                                    id='load-river',
                                    n_clicks=0,
                                    className='button'),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children='Meanders', className='menu-title'),
                        dcc.Dropdown(
                            data_meander['id_meanders'], 'All',
                            id='meander-dropdown',
                            clearable=False,
                            className='dropdown',
                        ),
                        html.Div(
                            children=[
                                html.Button('New Meander', id='new-meander',
                                            n_clicks=0, className='button'),
                                # html.P(' '),
                                html.Button('Remove Meander',
                                            id='remove-meander',
                                            n_clicks=0,
                                            className='button'),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children='Save Meanders',
                                 className='menu-title'),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children='Statistics',
                                 className='menu-title'),
                    ]
                ),
            ],
            className='menu'
        ),
        # Graph
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='figure-general', figure=fig_river),
                    className='card'
                )
            ],
            className='wrapper'
        ),
        html.Div(id='meanders-created',
                 children='New Meander'),
    ],
)


# ------------------
# Classes
# ------------------
class DataMeander:
    def __init__(self, data):
        self.data = data
        return

    def add_data(self):
        return



# ------------------
# Callbacks
# ------------------
@app.callback(
    Output('figure-general', 'figure'),
    Output('load-river', 'n_clicks'),
    Output('new-meander', 'n_clicks'),
    Output('meanders', 'data'),
    Output('meanders-created', 'children'),
    Output('figure-general', 'clickData'),
    Input('figure-general', 'figure'),
    Input('load-river', 'n_clicks'),
    Input('new-meander', 'n_clicks'),
    Input('figure-general', 'clickData'),
    State('meanders', 'data'),
)
def update_river_figure(figure_river, n_clicks_load_river,
                        n_clicks_new_meander, clickData, data_meander):

    data_meander = data_meander or {'meanders': {},
                                    'id_meanders': ['All', 'None']}

    if n_clicks_load_river >= 1:
        msg = ''
        figure_river, n_clicks_load_river = load_river(figure_river,
                                                       n_clicks_load_river)

    elif n_clicks_new_meander >= 1:
        data = new_meander(figure_river, n_clicks_new_meander, clickData,
                           data_meander)
        msg = data[0]
        n_clicks_new_meander = data[1]
        figure_river = data[2]
        clickData = data[3]
        data_meander = data[4]
    else:
        msg = ''

    return (figure_river, n_clicks_load_river, n_clicks_new_meander,
            data_meander, msg, clickData)




# Remove new Meander
# @app.callback(
#     Output('remove-meander', 'n_clicks'),
#     Input('remove-meander', 'n_clicks'),
#     Input('meander-dropdown', 'value'),
#     State('meanders', 'data'),
# )
# def remove_meander(n_clicks, meander_dropdown, data_meander):
#
#     if n_clicks > 0:
#         if not(meander_dropdown in ['All', 'None']):
#             data_meander['meanders'].pop(int(meander_dropdown), None)
#             data_meander['id_meanders'].remove(meander_dropdown)
#
#         n_clicks = 0
#
#     return n_clicks


@app.callback(
    Output('meander-dropdown', 'options'),
    Input('meanders', 'data'),
)
def update_meander_dropdown(data):
    options = sorted(data['id_meanders'])
    return options


if __name__ == '__main__':


    app.run_server(debug=True)
    # app.run_server()
