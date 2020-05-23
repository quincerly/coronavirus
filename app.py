#! /usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import coronavirus
import utils

app=dash.Dash()

data=coronavirus.Data('https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv')

colors = {
    'background': 'white',
    'text': 'black'
}
app.layout = html.Div(style={'backgroundColor': colors['background'], 'textAlign': 'center'},
                      children=[
    html.H2(
        children='Coronavirus Statistics',
        style={'textAlign': 'center', 'color': colors['text']
        }
    ),
    html.Div(children=[
        html.Div(style={ 'border': 'solid 1px #aaaaaa',
                         'padding': '1em',
                         'margin': '1em' },
                 children=[
            dcc.Slider(id='t_infectious_slider',
                       min=1, max=21, step=1,
                       marks={1: '1 day', 7: '7 days', 14: '14 days', 21: '21 days'},
                       value=7,
            ),
            html.Div(id='t_infectious_slider_value'),
            ]),
        html.Div(id='coronavirus_plot_div',
                 children=[html.Img(id='coronavirus_plot_img', src='')]
        )
    ])
])

@app.callback(
    [dash.dependencies.Output('coronavirus_plot_img', 'src'),
     dash.dependencies.Output('t_infectious_slider_value', 'children')],
    [dash.dependencies.Input('t_infectious_slider', 'value')])
def update_coronavirus_plot(t_inf):
    # Convert MatPlotLib figure encoded as PNG image. More clunky than using
    # plotly Graphs but I want to see how well it works as I have many complex
    # maplotlib visualisations in existing projects which I want to use.
    fig=coronavirus.Plot(data,
                         #area_type='Nation',
                         area_type='Region',
                         t_infectious=t_inf # Days for which a patient is infectious
    )
    return utils.fig_to_uri(fig, tight_layout=True, dpi=64), "Assume people are infectious for {} days".format(t_inf)

if __name__ == '__main__':
    app.run_server(debug=True)

