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

# ----------------
# Functions
# ----------------

# ----------------
# Read Information
# ----------------
points_selected = []
saved_data = 0

# Open Data
file_open = open('demo_data/data_input.p', "rb")
data = pickle.load(file_open)
file_open.close()
id_reach = 0
data_reach_all = data[0]
x = data_reach_all['x_poly']
y = data_reach_all['y_poly']
data_reach = {'x': x, 'y': y}
data_meander = {
    'meanders': {},
    'id_meanders': ['All', 'None']
}

# ----------------
# Create Figure
# ----------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, line=dict(color='black')))
# fig = px.line(data_pd, x='x', y='y', color='Order')
fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
  )
fig.update_layout(title=f'Reach {0}')
fig.update_layout(uirevision='dont change')
fig.update_layout(showlegend=False)

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
                        id='figure-general', figure=fig),
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
# Functions
# ------------------
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

# ------------------
# Callbacks
# ------------------
@app.callback(
    Output('meanders-created', 'children'),
    Output('new-meander', 'n_clicks'),
    Output('figure-general', 'figure'),
    Output('figure-general', 'clickData'),
    Output('meanders', 'data'),
    Input('new-meander', 'n_clicks'),
    Input('figure-general', 'clickData'),
    State('meanders', 'data'),
)
def new_meander(n_clicks, clickData, data_meander):
    global points_selected
    global saved_data
    global data_reach
    global fig
    # Populate meanders
    data_meander = data_meander or {'meanders': {},
                                    'id_meanders': ['All', 'None']}
    n_points = len(points_selected)
    msg = (f'Clicks {n_clicks}\nN. Points: {n_points}\nPoints:'
           f' {points_selected}')
    if n_clicks == 0:
        fig.update_layout(clickmode='none')
    elif n_clicks >= 1:
        fig.update_layout(clickmode='event+select')
        if clickData:
            i_sel = clickData['points'][0]['pointIndex']
            points_selected.append(i_sel)
        data_meander['meanders'][saved_data] = points_selected
        fig = update_meander_points(fig, data_reach, points_selected)
        n_points = len(points_selected)
    if n_points >= 2:
        points_selected = []
        fig.update_layout(clickmode='select')
        data_meander['id_meanders'].append(f'{saved_data:04d}')
        saved_data += 1
        clickData = None
        n_clicks = 0
    return (msg, n_clicks, fig, clickData, data_meander)


# Remove new Meander
@app.callback(
    Output('remove-meander', 'n_clicks'),
    Input('remove-meander', 'n_clicks'),
    Input('meander-dropdown', 'value'),
    State('meanders', 'data'),
)
def remove_meander(n_clicks, meander_dropdown, data_meander):

    if n_clicks > 0:
        if not(meander_dropdown in ['All', 'None']):
            data_meander['meanders'].pop(int(meander_dropdown), None)
            data_meander['id_meanders'].remove(meander_dropdown)

        n_clicks = 0

    return n_clicks


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
