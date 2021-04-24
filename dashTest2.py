import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np


np.random.seed(42)

rand_x = np.random.randint(1, 101, 100)
rand_y = np.random.randint(1, 101, 100)

app = dash.Dash()
app.layout = html.Div(children=
                        [dcc.Graph(
                            id='scatterplot',
                            figure=dict(
                                data=[go.Scatter(
                                    x=rand_x,
                                    y=rand_y,
                                    mode='markers',
                                    marker = dict(
                                        size=12,
                                        color='rgb(51,204,153)',
                                        line=dict(width=2)
                                    )
                                )],
                                layout=go.Layout(title='My Scatter Plot!')
                                )
                            ),
                        dcc.Graph(
                            id='scatterplot2',
                            figure=dict(
                                data=[go.Scatter(
                                    x=rand_x,
                                    y=rand_y,
                                    mode='markers',
                                    marker = dict(
                                        size=12,
                                        color='rgb(51,204,153)',
                                        line=dict(width=2)
                                    )
                                )],
                                layout=go.Layout(title='My Scatter Plot!')
                                )
                            )])

if __name__=='__main__':
    app.run_server()