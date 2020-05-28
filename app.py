#! /usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import coronavirus

nbsp='\u00a0'

data=coronavirus.Data('https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv')

colours = {
    'background': 'white',
    'text': 'black',
    'toolbg': '#e6edf6',
}

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
]
app=dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server
app.title='Covid19 Dash Test App'

area_type_tool=html.Div(
    [
        html.Label('Statistics for'),
        dcc.Dropdown(id='area_type_dropdown',
                     options=[{'label': t, 'value': t} for t in ['Nation', 'Region']],
                     value='Nation',
                     clearable=False)
    ],
    className="three columns",
)
t_inf_tool=html.Div(
    [
        html.Label(id='t_infectious_slider_value'),
        html.Div(
            [
                dcc.Slider(id='t_infectious_slider',
                           min=1, max=21, step=1,
                           marks={
                               1: '1{}day'.format(nbsp),
                               7: '7{}days'.format(nbsp),
                               14: '14{}days'.format(nbsp),
                               21: '21{}days'.format(nbsp),
                           },
                           value=7,
                )])
    ],
    className="six columns",
)
smooth_tool=html.Div(
    [
        html.Label('Smoothing'),
        html.Div([daq.ToggleSwitch(
            id='smooth_toggle',
            value=False,
            label=['Off', 'On'],
        )],
        ),
    ],
    className="three columns",
)

body = html.Div(
    [
        html.H1('Coronavirus Statistics', style={'text-shadow': '1px 1px 4px #333377'}),
        html.Div([area_type_tool,
                  smooth_tool,
                  t_inf_tool,
        ],
                 className="row",
                 style={'background': colours['toolbg'],
                        'padding': '1em',
                        'margin-bottom': '1em', 'border-radius': '4px',
                        'box-shadow': '1px 1px 4px #333377'}),
        html.Div([dcc.Loading(type='circle', children=[
            dcc.Graph(id='coronavirus_plot_graph_D'),
        ])],
                 className='twelve columns',
        ),
        html.Div([dcc.Loading(type='circle', children=[
            dcc.Graph(id='coronavirus_plot_graph_R'),
        ])],
                 className='twelve columns',
        ),
        'Data from: ', html.A(data.url, href=data.url),
    ],
)

app.layout = html.Div([body])

@app.callback(
    [dash.dependencies.Output('coronavirus_plot_graph_D', 'figure'),
     dash.dependencies.Output('coronavirus_plot_graph_R', 'figure'),
     dash.dependencies.Output('t_infectious_slider_value', 'children')],
    [dash.dependencies.Input('t_infectious_slider', 'value'),
     dash.dependencies.Input('area_type_dropdown', 'value'),
     dash.dependencies.Input('smooth_toggle', 'value'),
    ])
def update_coronavirus_plot(t_infectious, area_type, smooth):
    Dfig=go.Figure()
    Dfig.update_layout(
        xaxis_title="Date",
        yaxis_title="Daily cases",
        margin=dict(l=20, r=20, t=30, b=20),
        height=350,
    )
    Rfig=go.Figure()
    Rfig.update_layout(
        xaxis_title="Date",
        yaxis_title="R value",
        margin=dict(l=20, r=20, t=30, b=20),
        height=350,
    )
    for area in data.listAreas(area_type):
        curve=data.getCurveForArea(area, smooth=smooth)
        n_infectious=coronavirus.NInfectious(curve, t_infectious)
        R=curve['daily']*t_infectious/n_infectious
        Dfig.add_trace(go.Scatter(x=curve['datetime'], y=curve['daily'], name=area))
        Rfig.add_trace(go.Scatter(x=curve['datetime'], y=R, name=area))
    return Dfig, Rfig, "Assume people are infectious for {} days".format(t_infectious)

if __name__ == '__main__':
    app.run_server()

