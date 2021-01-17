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
        html.Label('Smoothing {} to {} days'.format(data.swindow[0], data.swindow[1])),
        html.Div([daq.ToggleSwitch(
            id='smooth_toggle',
            value=True,
            label=['Off', 'On'],
        )],
        ),
    ],
    className="three columns",
)
toolbar=html.Div([area_type_tool,
                  smooth_tool,
                  t_inf_tool],
                 className="row",
                 style={'background': colours['toolbg'],
                        'padding': '1em',
                        'margin-bottom': '1em', 'border-radius': '4px',
                        'box-shadow': '1px 1px 4px #333377'})

titlebar=html.Div([
    html.H1('Coronavirus Statistics',
            style={'float': 'left', 'text-shadow': '1px 1px 4px #333377'}),
],
                  className='row')

body = html.Div(
    [
        titlebar,
        toolbar,
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

def ploterr(fig, x, y, yerr, name, colour, errcolour, dash=None):
    xe=x+x[::-1]
    yupper=(y+yerr).tolist()
    ylower=(y-yerr).tolist()
    ye=yupper+ylower[::-1]
    fig.add_trace(go.Scatter(x=x, y=y,
                             legendgroup=name,
                             name=name,
                             line=dict(color=colour, dash=dash),
    ))
    fig.add_trace(go.Scatter(x=xe, y=ye,
                             legendgroup=name,
                             name=name+" error",
                             fill='tozeroy',
                             fillcolor=errcolour, opacity=0.2,
                             line=dict(color='rgba(255,255,255,0)')
    ))

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
        margin=dict(l=80, r=30, t=30, b=20),
        height=350,
        legend=dict(font=dict(size=8)),
    )
    Rfig=go.Figure()
    Rfig.update_layout(
        xaxis_title="Date",
        yaxis_title="R value",
        margin=dict(l=80, r=30, t=30, b=20),
        height=350,
        legend=dict(font=dict(size=8)),
    )
    colours=[
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'   # blue-teal
    ]
    def hex_to_rgb(h):
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    def rgbacolour(h, opacity=1):
        return "rgba({:d},{:d},{:d},{:f})".format(*(list(hex_to_rgb(h))+[opacity]))
    areas=data.listAreas(area_type)
    for area in areas:
        colour=colours[areas.index(area) % len(areas)]
        curve=data.getCurveForArea(area, smooth=smooth)
        R, sig_R=coronavirus.CalcR(curve, t_infectious)
        ploterr(Dfig,
                x=curve['datetime'], y=curve['daily'], yerr=curve['dailyerr'],
                name=area,
                colour=rgbacolour(colour),
                errcolour=rgbacolour(colour, 0.5))
        ploterr(Rfig,
                x=curve['datetime'],
                y=R,
                yerr=sig_R,
                name=area,
                colour=rgbacolour(colour),
                errcolour=rgbacolour(colour, 0.5))
    return Dfig, Rfig, "Assume people are infectious for {} days".format(t_infectious)

if __name__ == '__main__':
    app.run_server()

