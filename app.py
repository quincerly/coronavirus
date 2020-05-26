#! /usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

import coronavirus
import utils

nbsp='\u00a0'

data=coronavirus.Data('https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv')

colours = {
    'background': 'white',
    'text': 'black',
    'toolbg': '#eeeeff',
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
        html.H1('Coronavirus Statistics'),
        html.Div([area_type_tool,
                  smooth_tool,
                  t_inf_tool,
        ],
                 className="row",
                 style={'background': colours['toolbg'],
                        'padding': '1em'}),
        html.Div([dcc.Loading(type='circle',
                              children=[
                                  html.Div(id='coronavirus_plot_div', children=[html.Img(id='coronavirus_plot_img', src='')]),
                              ]),
        ],
                 className='six columns',
        ),
    ],
)

app.layout = html.Div([body])

@app.callback(
    [dash.dependencies.Output('coronavirus_plot_img', 'src'),
     dash.dependencies.Output('t_infectious_slider_value', 'children')],
    [dash.dependencies.Input('t_infectious_slider', 'value'),
     dash.dependencies.Input('area_type_dropdown', 'value'),
     dash.dependencies.Input('smooth_toggle', 'value'),
    ])
def update_coronavirus_plot(t_inf, area_type, smooth):
    # Convert MatPlotLib figure encoded as PNG image. More clunky than using
    # plotly Graphs but I want to see how well it works as I have many complex
    # maplotlib visualisations in existing projects which I want to use.
    fig=coronavirus.Plot(data,
                         area_type=area_type,
                         t_infectious=t_inf, # Days for which a patient is infectious,
                         smooth=smooth,
    )
    return utils.fig_to_uri(fig, tight_layout=True, dpi=64), "Assume people are infectious for {} days".format(t_inf)

if __name__ == '__main__':
    app.run_server()

