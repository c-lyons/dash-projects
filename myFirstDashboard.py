import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np
import pandas as pd

df = pd.read_csv('data/abalone.txt')

x = df.Height
y = df.Diameter

app = dash.Dash()

app.layout = html.Div([

        'Welcome to Gigable!', 
        html.Div(dcc.Graph(
                id='scatterplot',
                figure=dict(
                    data=[go.Scatter(
                        x=x,
                        y=y,
                        mode='markers',
                        marker=dict(
                            size=12,
                            color='rgb(51,204,153)',
                            line=dict(width=1))
                    )],
                    layout=go.Layout(title='My Scatter Plot!',
                                    xaxis=dict(title='Height'),
                                    yaxis=dict(title='Diameter'))
                            )
                ),
                style=dict(
                    color='red',
                    border='1px red solid'))],
        style=dict(
                color='green',
                border='2px green solid'
        ))

if __name__=='__main__':
    app.run_server()