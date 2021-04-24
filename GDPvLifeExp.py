import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd

try:
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')
except:
    'Failed to read data from source.'


app = dash.Dash()

app.layout = html.Div([
                dcc.Graph(id='graph'),
                dcc.Dropdown(id='year-picker',
                             options=[{'label':str(year), 'value':year} for year in df.year.unique()],
                             value=df.year.min())
])

@app.callback(Output('graph', 'figure'),
              [Input('year-picker', 'value')])
def update_figure(selected_year):
    filtered_df = df[df.year==selected_year]
    traces = []
    for cont in filtered_df.continent.unique():
        df_by_continent = filtered_df[filtered_df.continent==cont]
        traces.append(go.Scatter(
            x = df_by_continent['gdpPercap'],
            y = df_by_continent['lifeExp'],
            mode='markers',
            opacity=0.45,
            marker=dict(size=15),
            name=cont))

    return dict(data=traces,
                layout=go.Layout(title='My Plot',
                                 xaxis=dict(title='GDP Per Cap', type='log'),
                                 yaxis=dict(title='Life Exp.')))
if __name__=='__main__':
    app.run_server()